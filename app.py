import re
from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Hotel Analyzer | Management Platform",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# 2. MODERN DESIGN
# ============================================================

st.markdown("""
<style>

/* Main background */
.stApp {
    background: #f4f7fc;
    color: #172033;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* Main content */
.block-container {
    max-width: 1500px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Hide Streamlit branding */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #14213d;
    border-right: 1px solid #253654;
}

section[data-testid="stSidebar"] * {
    color: #f1f5ff;
}

section[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 9px;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label {
    background: #1d3153;
    border: 1px solid #2b4165;
    padding: 11px 13px;
    border-radius: 10px;
    transition: all 0.2s ease;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: #2b4773;
    border-color: #6095e5;
}

/* Headings */
h1 {
    color: #172b4d !important;
    font-weight: 750 !important;
    letter-spacing: -1px;
}

h2, h3 {
    color: #20385e !important;
    font-weight: 650 !important;
}

/* Metric cards */
div[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e3eaf4;
    border-radius: 15px;
    padding: 19px;
    min-height: 112px;
    box-shadow: 0 4px 15px rgba(22, 40, 75, 0.045);
}

div[data-testid="stMetricLabel"] {
    color: #64748b;
    font-size: 14px;
    font-weight: 600;
}

div[data-testid="stMetricValue"] {
    color: #2459a6;
    font-size: 28px;
    font-weight: 750;
}

/* Buttons */
.stButton > button,
.stFormSubmitButton > button {
    background: #2459a6;
    color: white;
    border: 1px solid #2459a6;
    border-radius: 10px;
    padding: 10px 18px;
    font-weight: 650;
    transition: all 0.2s ease;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: #173f7b;
    color: white;
    border-color: #173f7b;
}

/* Inputs */
.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stSelectbox div[data-baseweb="select"] {
    border-radius: 9px;
}

/* Forms */
div[data-testid="stForm"] {
    background: #ffffff;
    padding: 22px;
    border: 1px solid #e3eaf4;
    border-radius: 16px;
    box-shadow: 0 4px 18px rgba(22, 40, 75, 0.04);
}

/* Tables */
div[data-testid="stDataFrame"] {
    border: 1px solid #e3eaf4;
    border-radius: 12px;
    overflow: hidden;
}

/* Alerts */
div[data-testid="stAlert"] {
    border-radius: 12px;
}

/* Dividers */
hr {
    border-color: #e3eaf4;
    margin-top: 22px;
    margin-bottom: 22px;
}

/* Responsive */
@media (max-width: 768px) {
    .block-container {
        padding: 1rem;
    }

    h1 {
        font-size: 27px !important;
    }

    div[data-testid="stMetric"] {
        padding: 13px;
    }
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# 3. DATABASE CONNECTION
# ============================================================

@st.cache_resource
def get_engine():

    database_url = st.secrets["NEON_DATABASE_URL"]

    if database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://",
            "postgresql+psycopg2://",
            1
        )

    return create_engine(
        database_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5
    )


def load_data(query, params=None):

    with get_engine().connect() as connection:

        return pd.read_sql(
            text(query),
            connection,
            params=params or {}
        )


# ============================================================
# 4. COMMON UI FUNCTIONS
# ============================================================

def page_header(title, subtitle, icon="🏨"):

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(115deg, #142b50, #2459a6);
            padding: 27px 30px;
            border-radius: 17px;
            margin-bottom: 25px;
        ">
            <div style="
                color: #b9d5ff;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 2px;
            ">
                HOTEL MANAGEMENT PLATFORM
            </div>

            <div style="
                color: white;
                font-size: 29px;
                font-weight: 750;
                margin-top: 7px;
            ">
                {icon} {title}
            </div>

            <div style="
                color: #e0ebff;
                font-size: 14px;
                margin-top: 7px;
            ">
                {subtitle}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def show_error(message, error=None):

    st.error(message)

    if error is not None:
        with st.expander("Technical details"):
            st.code(str(error))


# ============================================================
# 5. SIDEBAR NAVIGATION
# ============================================================

st.sidebar.markdown(
    """
    <div style="padding: 12px 5px 22px 5px;">
        <div style="font-size: 30px;">🏨</div>
        <div style="
            font-size: 21px;
            font-weight: 750;
            color: white;
        ">
            HOTEL ANALYZER
        </div>
        <div style="
            font-size: 11px;
            color: #b9c9e3;
            letter-spacing: 1px;
        ">
            MANAGEMENT PLATFORM
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

page = st.sidebar.radio(
    "MAIN MENU",
    [
        "Dashboard",
        "Hotel Management",
        "Room Management",
        "Customer Management",
        "Booking Management",
        "Dynamic Pricing",
        "Analytics"
    ]
)

st.sidebar.divider()

st.sidebar.markdown(
    """
    <div style="
        background: #1d3153;
        border: 1px solid #334c72;
        border-radius: 11px;
        padding: 13px;
    ">
        <div style="font-weight: 650;">Database Status</div>
        <div style="color: #86efac; font-size: 13px;">
            ● Neon PostgreSQL
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.divider()

st.sidebar.caption(
    "Built with Python · PostgreSQL · Streamlit"
)


# ============================================================
# 6. CHECK DATABASE CONNECTION
# ============================================================

try:

    engine = get_engine()

    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

except Exception as e:

    show_error(
        "Database connection failed. Check your Neon credentials "
        "in Streamlit Cloud → App Settings → Secrets.",
        e
    )

    st.stop()


# ============================================================
# 7. DASHBOARD
# ============================================================

if page == "Dashboard":

    page_header(
        "Welcome to Hotel Analyzer",
        "Manage properties, rooms, customers and reservations "
        "from one centralized dashboard.",
        "🏨"
    )

    try:

        total_hotels = load_data("""
            SELECT COUNT(*) AS total FROM hotels
        """).iloc[0]["total"]

        total_rooms = load_data("""
            SELECT COUNT(*) AS total FROM rooms
        """).iloc[0]["total"]

        total_customers = load_data("""
            SELECT COUNT(*) AS total FROM customers
        """).iloc[0]["total"]

        total_bookings = load_data("""
            SELECT COUNT(*) AS total FROM bookings
        """).iloc[0]["total"]

        confirmed_bookings = load_data("""
            SELECT COUNT(*) AS total
            FROM bookings
            WHERE status = 'confirmed'
        """).iloc[0]["total"]

        cancelled_bookings = load_data("""
            SELECT COUNT(*) AS total
            FROM bookings
            WHERE status = 'cancelled'
        """).iloc[0]["total"]

        pending_bookings = load_data("""
            SELECT COUNT(*) AS total
            FROM bookings
            WHERE status = 'pending'
        """).iloc[0]["total"]

        # Overview
        st.subheader("Platform Overview")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Hotels", f"{int(total_hotels):,}")

        with col2:
            st.metric("Total Rooms", f"{int(total_rooms):,}")

        with col3:
            st.metric("Total Customers", f"{int(total_customers):,}")

        with col4:
            st.metric("Total Bookings", f"{int(total_bookings):,}")

        st.divider()

        # Booking status
        st.subheader("Booking Status")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Confirmed",
                f"{int(confirmed_bookings):,}"
            )

        with col2:
            st.metric(
                "Pending",
                f"{int(pending_bookings):,}"
            )

        with col3:
            st.metric(
                "Cancelled",
                f"{int(cancelled_bookings):,}"
            )

        st.divider()

        # Recent bookings
        st.subheader("Recent Bookings")

        recent_bookings = load_data("""
            SELECT
                b.booking_id,
                c.customer_name,
                h.hotel_name,
                h.city,
                r.room_number,
                b.check_in,
                b.check_out,
                b.status
            FROM bookings b
            JOIN customers c
                ON b.customer_id = c.customer_id
            JOIN rooms r
                ON b.room_id = r.room_id
            JOIN hotels h
                ON r.hotel_id = h.hotel_id
            ORDER BY b.booking_id DESC
            LIMIT 8
        """)

        if recent_bookings.empty:
            st.info("No bookings found.")

        else:
            st.dataframe(
                recent_bookings,
                width="stretch",
                hide_index=True
            )

    except Exception as e:

        show_error("Unable to load dashboard.", e)


# ============================================================
# 8. HOTEL MANAGEMENT
# ============================================================

elif page == "Hotel Management":

    page_header(
        "Hotel Management",
        "View and explore all registered hotel properties.",
        "🏨"
    )

    try:

        df = load_data("""
            SELECT
                hotel_id,
                hotel_name,
                city,
                address,
                star_rating,
                created_at
            FROM hotels
            ORDER BY hotel_id
        """)

        st.metric("Total Properties", len(df))

        st.subheader("Registered Hotels")

        st.dataframe(
            df,
            width="stretch",
            hide_index=True
        )

        st.divider()

        st.subheader("Properties by City")

        city_data = (
            df.groupby("city")
            .size()
            .reset_index(name="hotel_count")
        )

        fig = px.bar(
            city_data,
            x="city",
            y="hotel_count",
            text="hotel_count",
            color="hotel_count",
            color_continuous_scale="Blues",
            title="Hotel Distribution by City"
        )

        fig.update_layout(
            xaxis_title="City",
            yaxis_title="Number of Hotels",
            showlegend=False,
            margin=dict(l=15, r=15, t=60, b=15)
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    except Exception as e:

        show_error("Unable to load hotel information.", e)


# ============================================================
# 9. ROOM MANAGEMENT
# ============================================================

elif page == "Room Management":

    page_header(
        "Room Management",
        "Explore room inventory, room categories and base prices.",
        "🛏️"
    )

    try:

        df = load_data("""
            SELECT
                r.room_id,
                h.hotel_name,
                h.city,
                r.room_number,
                r.room_type,
                r.capacity,
                r.base_price,
                r.room_status
            FROM rooms r
            JOIN hotels h
                ON r.hotel_id = h.hotel_id
            ORDER BY h.hotel_name, r.room_number
        """)

        st.metric("Total Rooms", len(df))

        col1, col2 = st.columns(2)

        with col1:

            cities = ["All Cities"] + sorted(
                df["city"].dropna().unique().tolist()
            )

            selected_city = st.selectbox(
                "Filter by City",
                cities
            )

        with col2:

            room_categories = ["All Room Types"] + sorted(
                df["room_type"].dropna().unique().tolist()
            )

            selected_type = st.selectbox(
                "Filter by Room Type",
                room_categories
            )

        filtered_df = df.copy()

        if selected_city != "All Cities":
            filtered_df = filtered_df[
                filtered_df["city"] == selected_city
            ]

        if selected_type != "All Room Types":
            filtered_df = filtered_df[
                filtered_df["room_type"] == selected_type
            ]

        st.dataframe(
            filtered_df,
            width="stretch",
            hide_index=True
        )

        st.divider()

        st.subheader("Room Type Distribution")

        room_types = (
            filtered_df.groupby("room_type")
            .size()
            .reset_index(name="total_rooms")
        )

        fig = px.pie(
            room_types,
            names="room_type",
            values="total_rooms",
            hole=0.45,
            title="Room Categories"
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    except Exception as e:

        show_error("Unable to load room information.", e)


# ============================================================
# 10. CUSTOMER MANAGEMENT
# ============================================================

elif page == "Customer Management":

    page_header(
        "Customer Management",
        "View customer information and registered accounts.",
        "👥"
    )

    try:

        df = load_data("""
            SELECT
                customer_id,
                customer_name,
                email,
                phone
            FROM customers
            ORDER BY customer_id DESC
        """)

        st.metric("Registered Customers", len(df))

        search = st.text_input(
            "Search Customer",
            placeholder="Enter customer name or email..."
        )

        if search:

            mask = (
                df["customer_name"].str.contains(
                    search,
                    case=False,
                    na=False
                )
                |
                df["email"].str.contains(
                    search,
                    case=False,
                    na=False
                )
            )

            df = df[mask]

        st.dataframe(
            df,
            width="stretch",
            hide_index=True
        )

    except Exception as e:

        show_error("Unable to load customer information.", e)


# ============================================================
# 11. BOOKING MANAGEMENT
# ============================================================

elif page == "Booking Management":

    page_header(
        "Booking Management",
        "Create reservations and manage hotel booking records.",
        "📅"
    )

    # --------------------------------------------------------
    # EXISTING BOOKINGS
    # --------------------------------------------------------

    st.subheader("Booking Overview")

    try:

        bookings_df = load_data("""
            SELECT
                b.booking_id,
                c.customer_name,
                h.hotel_name,
                h.city,
                r.room_number,
                r.room_type,
                b.check_in,
                b.check_out,
                b.total_price,
                b.status
            FROM bookings b
            JOIN customers c
                ON b.customer_id = c.customer_id
            JOIN rooms r
                ON b.room_id = r.room_id
            JOIN hotels h
                ON r.hotel_id = h.hotel_id
            ORDER BY b.booking_id DESC
        """)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Bookings", len(bookings_df))

        with col2:
            st.metric(
                "Confirmed",
                int(
                    (bookings_df["status"] == "confirmed").sum()
                )
            )

        with col3:
            st.metric(
                "Cancelled",
                int(
                    (bookings_df["status"] == "cancelled").sum()
                )
            )

        if bookings_df.empty:
            st.info("No bookings available.")

        else:

            st.dataframe(
                bookings_df,
                width="stretch",
                hide_index=True
            )

    except Exception as e:

        show_error("Unable to load existing bookings.", e)


    st.divider()

    # --------------------------------------------------------
    # NEW BOOKING
    # --------------------------------------------------------

    st.subheader("Create a New Booking")

    st.markdown(
        "Complete the following steps to reserve a hotel room."
    )

    try:

        hotels_df = load_data("""
            SELECT
                hotel_id,
                hotel_name,
                city
            FROM hotels
            ORDER BY hotel_name
        """)

        if hotels_df.empty:

            st.warning("No hotels are registered.")

        else:

            # Step 1: Hotel selection
            st.markdown("#### 1. Choose Hotel")

            hotel_options = {
                f"{row.hotel_name} — {row.city}":
                    int(row.hotel_id)
                for row in hotels_df.itertuples()
            }

            selected_hotel = st.selectbox(
                "Select Property",
                list(hotel_options.keys()),
                key="booking_hotel"
            )

            hotel_id = hotel_options[selected_hotel]

            # Step 2: Dates
            st.markdown("#### 2. Choose Booking Dates")

            date_col1, date_col2 = st.columns(2)

            with date_col1:

                check_in = st.date_input(
                    "Check-in Date",
                    value=date.today(),
                    min_value=date.today(),
                    key="booking_checkin"
                )

            with date_col2:

                check_out = st.date_input(
                    "Check-out Date",
                    value=date.today() + timedelta(days=1),
                    min_value=date.today() + timedelta(days=1),
                    key="booking_checkout"
                )

            # Step 3: Search available rooms
            st.markdown("#### 3. Available Rooms")

            available_rooms = pd.DataFrame()

            if check_out <= check_in:

                st.warning(
                    "Check-out must be after check-in."
                )

            else:

                available_rooms = load_data("""
                    SELECT
                        r.room_id,
                        r.room_number,
                        r.room_type,
                        r.capacity,
                        r.base_price
                    FROM rooms r

                    WHERE r.hotel_id = :hotel_id

                    AND NOT EXISTS (
                        SELECT 1
                        FROM bookings b
                        WHERE b.room_id = r.room_id
                        AND b.status <> 'cancelled'
                        AND b.check_in < :check_out
                        AND b.check_out > :check_in
                    )

                    ORDER BY r.room_number
                """, {
                    "hotel_id": hotel_id,
                    "check_in": check_in,
                    "check_out": check_out
                })

            if check_out > check_in and available_rooms.empty:

                st.warning(
                    "No rooms are available for these dates. "
                    "Try another date or hotel."
                )

            elif not available_rooms.empty:

                st.success(
                    f"{len(available_rooms)} room(s) available."
                )

                room_options = {}

                for row in available_rooms.itertuples():

                    label = (
                        f"Room {row.room_number} | "
                        f"{row.room_type} | "
                        f"Capacity: {row.capacity} | "
                        f"₹{row.base_price:,.2f}/night"
                    )

                    room_options[label] = {
                        "room_id": int(row.room_id),
                        "base_price": float(row.base_price),
                        "room_number": row.room_number,
                        "room_type": row.room_type
                    }

                selected_room = st.selectbox(
                    "Select Available Room",
                    list(room_options.keys()),
                    key="booking_room"
                )

                room_details = room_options[selected_room]

                nights = (check_out - check_in).days

                total_price = (
                    room_details["base_price"] * nights
                )

                # Booking summary
                st.markdown("#### Booking Summary")

                sum_col1, sum_col2, sum_col3 = st.columns(3)

                with sum_col1:
                    st.metric("Room", room_details["room_number"])

                with sum_col2:
                    st.metric("Number of Nights", nights)

                with sum_col3:
                    st.metric(
                        "Estimated Total",
                        f"₹{total_price:,.2f}"
                    )

                st.caption(
                    "The amount is calculated using the room's "
                    "base price per night. It is an estimate and "
                    "does not include separate payment processing."
                )

                st.divider()

                # Step 4: Customer information
                st.markdown("#### 4. Customer Information")

                with st.form(
                    "customer_booking_form",
                    clear_on_submit=False
                ):

                    customer_name = st.text_input(
                        "Customer Name",
                        placeholder="Enter full name"
                    )

                    customer_email = st.text_input(
                        "Email Address",
                        placeholder="example@email.com"
                    )

                    customer_phone = st.text_input(
                        "Phone Number",
                        placeholder="Enter phone number"
                    )

                    confirm_booking = st.form_submit_button(
                        "Confirm Reservation",
                        type="primary",
                        width="stretch"
                    )

                # Step 5: Save booking
                if confirm_booking:

                    if not customer_name.strip():

                        st.error("Please enter the customer name.")

                    elif not customer_email.strip():

                        st.error("Please enter the email address.")

                    elif not re.match(
                        r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
                        customer_email.strip()
                    ):

                        st.error("Please enter a valid email address.")

                    elif check_out <= check_in:

                        st.error("Please select valid booking dates.")

                    else:

                        normalized_email = (
                            customer_email.strip().lower()
                        )

                        try:

                            # One transaction:
                            # 1. Lock the room.
                            # 2. Check overlapping bookings.
                            # 3. Create/find customer.
                            # 4. Insert booking.

                            with get_engine().begin() as connection:

                                # Lock selected room
                                room = connection.execute(
                                    text("""
                                        SELECT room_id
                                        FROM rooms
                                        WHERE room_id = :room_id
                                        FOR UPDATE
                                    """),
                                    {
                                        "room_id":
                                            room_details["room_id"]
                                    }
                                ).fetchone()

                                if room is None:

                                    raise ValueError(
                                        "Selected room no longer exists."
                                    )

                                # Final availability check
                                overlap = connection.execute(
                                    text("""
                                        SELECT booking_id
                                        FROM bookings
                                        WHERE room_id = :room_id
                                        AND status <> 'cancelled'
                                        AND check_in < :check_out
                                        AND check_out > :check_in
                                        LIMIT 1
                                    """),
                                    {
                                        "room_id":
                                            room_details["room_id"],
                                        "check_in": check_in,
                                        "check_out": check_out
                                    }
                                ).fetchone()

                                if overlap:

                                    raise ValueError(
                                        "This room has already been "
                                        "booked for the selected dates. "
                                        "Please choose another room."
                                    )

                                # Create customer or reuse existing email
                                customer_result = connection.execute(
                                    text("""
                                        INSERT INTO customers (
                                            customer_name,
                                            email,
                                            phone
                                        )
                                        VALUES (
                                            :customer_name,
                                            :email,
                                            :phone
                                        )
                                        ON CONFLICT (email)
                                        DO UPDATE SET
                                            customer_name =
                                                EXCLUDED.customer_name,
                                            phone = COALESCE(
                                                EXCLUDED.phone,
                                                customers.phone
                                            )
                                        RETURNING customer_id
                                    """),
                                    {
                                        "customer_name":
                                            customer_name.strip(),
                                        "email": normalized_email,
                                        "phone":
                                            customer_phone.strip() or None
                                    }
                                )

                                customer_id = (
                                    customer_result.scalar_one()
                                )

                                # Insert confirmed booking
                                booking_result = connection.execute(
                                    text("""
                                        INSERT INTO bookings (
                                            room_id,
                                            customer_id,
                                            check_in,
                                            check_out,
                                            total_price,
                                            status
                                        )
                                        VALUES (
                                            :room_id,
                                            :customer_id,
                                            :check_in,
                                            :check_out,
                                            :total_price,
                                            'confirmed'
                                        )
                                        RETURNING booking_id
                                    """),
                                    {
                                        "room_id":
                                            room_details["room_id"],
                                        "customer_id": customer_id,
                                        "check_in": check_in,
                                        "check_out": check_out,
                                        "total_price": total_price
                                    }
                                )

                                booking_id = (
                                    booking_result.scalar_one()
                                )

                            # Clear cached data if added later
                            st.success(
                                "Reservation confirmed successfully!"
                            )

                            st.markdown(
                                f"""
                                <div style="
                                    background: #ecfdf5;
                                    border: 1px solid #a7f3d0;
                                    border-radius: 14px;
                                    padding: 20px;
                                    margin-top: 12px;
                                ">
                                    <div style="
                                        color: #047857;
                                        font-weight: 750;
                                        font-size: 20px;
                                    ">
                                        Booking Confirmed
                                    </div>
                                    <div style="
                                        color: #065f46;
                                        margin-top: 10px;
                                    ">
                                        Booking ID: <b>{booking_id}</b>
                                    </div>
                                    <div style="
                                        color: #065f46;
                                        margin-top: 5px;
                                    ">
                                        Customer: <b>{customer_name}</b>
                                    </div>
                                    <div style="
                                        color: #065f46;
                                        margin-top: 5px;
                                    ">
                                        Total: <b>₹{total_price:,.2f}</b>
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                            st.rerun()

                        except IntegrityError:

                            st.error(
                                "Booking rejected. PostgreSQL detected "
                                "a conflicting booking or invalid record."
                            )

                        except Exception as e:

                            show_error(
                                "Unable to complete the booking.",
                                e
                            )

    except Exception as e:

        show_error(
            "Unable to load the booking form.",
            e
        )


# ============================================================
# 12. DYNAMIC PRICING
# ============================================================

elif page == "Dynamic Pricing":

    page_header(
        "Dynamic Pricing Analyzer",
        "Analyze room prices generated using demand, "
        "occupancy and weekend adjustments.",
        "💰"
    )

    try:

        df = load_data("""
            SELECT
                h.hotel_name,
                h.city,
                r.room_id,
                r.room_number,
                r.room_type,
                r.base_price,
                p.price AS dynamic_price,
                p.effective_date,
                p.pricing_reason
            FROM pricing_history p
            JOIN rooms r
                ON p.room_id = r.room_id
            JOIN hotels h
                ON r.hotel_id = h.hotel_id
            ORDER BY p.effective_date DESC
            LIMIT 5000
        """)

        if df.empty:

            st.warning("No dynamic pricing records found.")

        else:

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Pricing Records",
                    len(df)
                )

            with col2:
                st.metric(
                    "Average Dynamic Price",
                    f"₹{df['dynamic_price'].mean():,.2f}"
                )

            st.divider()

            selected_hotel = st.selectbox(
                "Filter by Hotel",
                ["All Hotels"] + sorted(
                    df["hotel_name"].dropna().unique().tolist()
                )
            )

            if selected_hotel != "All Hotels":

                df = df[
                    df["hotel_name"] == selected_hotel
                ]

            st.subheader("Pricing Records")

            st.dataframe(
                df,
                width="stretch",
                hide_index=True
            )

            st.divider()

            st.subheader("Base Price vs Dynamic Price")

            fig = px.scatter(
                df.head(300),
                x="base_price",
                y="dynamic_price",
                color="hotel_name",
                hover_data=[
                    "room_number",
                    "room_type",
                    "effective_date"
                ],
                title="Room Price Comparison"
            )

            fig.update_layout(
                margin=dict(l=15, r=15, t=60, b=15)
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

            st.info(
                "Pricing records are generated using synthetic "
                "project data, not live hotel market rates."
            )

    except Exception as e:

        show_error(
            "Unable to load dynamic pricing records.",
            e
        )


# ============================================================
# 13. ANALYTICS
# ============================================================

elif page == "Analytics":

    page_header(
        "Hotel Analytics",
        "Understand property performance, occupancy, "
        "booking activity and revenue.",
        "📊"
    )

    try:

        df = load_data("""
            SELECT
                h.hotel_id,
                h.hotel_name,
                h.city,

                COUNT(DISTINCT r.room_id)
                    AS total_rooms,

                COUNT(DISTINCT b.booking_id)
                    AS total_bookings,

                COUNT(DISTINCT CASE
                    WHEN b.status IN (
                        'confirmed',
                        'checked_in',
                        'checked_out'
                    )
                    THEN b.booking_id
                END) AS successful_bookings,

                COUNT(DISTINCT CASE
                    WHEN b.status = 'cancelled'
                    THEN b.booking_id
                END) AS cancelled_bookings,

                COALESCE(
                    SUM(
                        CASE
                            WHEN b.status IN (
                                'confirmed',
                                'checked_in',
                                'checked_out'
                            )
                            THEN b.total_price
                            ELSE 0
                        END
                    ),
                    0
                ) AS total_revenue,

                ROUND(
                    100.0 *
                    COUNT(DISTINCT CASE
                        WHEN b.status IN (
                            'confirmed',
                            'checked_in',
                            'checked_out'
                        )
                        AND b.check_in <= CURRENT_DATE
                        AND b.check_out > CURRENT_DATE
                        THEN b.room_id
                    END)
                    /
                    NULLIF(COUNT(DISTINCT r.room_id), 0),
                    2
                ) AS current_occupancy_percentage

            FROM hotels h

            LEFT JOIN rooms r
                ON h.hotel_id = r.hotel_id

            LEFT JOIN bookings b
                ON r.room_id = b.room_id

            GROUP BY
                h.hotel_id,
                h.hotel_name,
                h.city

            ORDER BY total_revenue DESC
        """)

        st.subheader("Property Performance")

        st.dataframe(
            df,
            width="stretch",
            hide_index=True
        )

        total_bookings = int(
            df["total_bookings"].sum()
        )

        total_revenue = float(
            df["total_revenue"].sum()
        )

        total_cancelled = int(
            df["cancelled_bookings"].sum()
        )

        cancellation_rate = (
            total_cancelled / total_bookings * 100
            if total_bookings > 0 else 0
        )

        st.divider()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Total Bookings",
                total_bookings
            )

        with col2:
            st.metric(
                "Cancelled Bookings",
                total_cancelled
            )

        with col3:
            st.metric(
                "Cancellation Rate",
                f"{cancellation_rate:.2f}%"
            )

        st.divider()

        st.subheader("Hotel Revenue Comparison")

        fig1 = px.bar(
            df.nlargest(10, "total_revenue"),
            x="hotel_name",
            y="total_revenue",
            color="city",
            title="Top 10 Hotels by Revenue"
        )

        st.plotly_chart(
            fig1,
            width="stretch"
        )

        st.subheader("Booking Comparison")

        fig2 = px.bar(
            df.nlargest(10, "total_bookings"),
            x="hotel_name",
            y="total_bookings",
            color="city",
            title="Top 10 Hotels by Booking Count"
        )

        st.plotly_chart(
            fig2,
            width="stretch"
        )

        st.subheader("Current Occupancy")

        fig3 = px.bar(
            df.nlargest(
                10,
                "current_occupancy_percentage"
            ),
            x="hotel_name",
            y="current_occupancy_percentage",
            color="city",
            title="Current Occupancy Percentage"
        )

        fig3.update_layout(
            yaxis_title="Occupancy (%)"
        )

        st.plotly_chart(
            fig3,
            width="stretch"
        )

    except Exception as e:

        show_error(
            "Unable to load analytics.",
            e
        )


# ============================================================
# 14. FOOTER
# ============================================================

st.markdown(
    """
    <div style="
        text-align: center;
        padding: 25px 10px 10px 10px;
        color: #8090a8;
        font-size: 12px;
        border-top: 1px solid #e3eaf4;
        margin-top: 35px;
    ">
        Hotel Multi-Property Booking & Dynamic Pricing Analyzer
        <br>
        Built with Python · PostgreSQL · SQLAlchemy · Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
