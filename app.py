
import re
from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError


# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Hotel Analyzer",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# 2. MODERN DESIGN - READABLE COLOURS AND TEXT
# =========================================================

st.markdown("""
<style>

/* Main page */
.stApp {
    background-color: #f5f7fb;
    color: #172b4d;
    font-family: "Segoe UI", Arial, sans-serif;
}

.block-container {
    max-width: 1500px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Make main page text readable */
.stApp,
.stApp p,
.stApp label,
.stApp span,
.stApp div[data-testid="stMarkdownContainer"] p,
.stApp div[data-testid="stMarkdownContainer"] li {
    color: #26364f;
}

/* Headings */
h1, h2, h3, h4 {
    color: #142b50 !important;
    font-weight: 750 !important;
}

h1 {
    font-size: 32px !important;
}

h2 {
    font-size: 25px !important;
}

h3 {
    font-size: 20px !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #14213d;
    border-right: 1px solid #263b5b;
}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div {
    color: #f1f5ff;
}

section[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 8px;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label {
    background: #1d3153;
    border: 1px solid #33496d;
    border-radius: 10px;
    padding: 10px 12px;
    margin-bottom: 3px;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: #2b4773;
}

/* Sidebar radio text */
section[data-testid="stSidebar"] div[role="radiogroup"] label p {
    color: #ffffff !important;
    font-size: 14px;
    font-weight: 600;
}

/* Metric cards */
div[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #dce5f1;
    border-radius: 15px;
    padding: 19px;
    min-height: 115px;
    box-shadow: 0 4px 14px rgba(20, 43, 80, 0.06);
}

div[data-testid="stMetricLabel"],
div[data-testid="stMetricLabel"] p {
    color: #52647e !important;
    font-size: 14px !important;
    font-weight: 650 !important;
}

div[data-testid="stMetricValue"],
div[data-testid="stMetricValue"] div {
    color: #174a88 !important;
    font-size: 28px !important;
    font-weight: 750 !important;
}

/* Inputs */
.stTextInput label,
.stSelectbox label,
.stDateInput label,
.stNumberInput label,
.stTextArea label {
    color: #253b5b !important;
    font-weight: 650 !important;
    font-size: 14px !important;
}

.stTextInput input,
.stNumberInput input,
.stDateInput input {
    background: #ffffff !important;
    color: #172b4d !important;
    border: 1px solid #cbd7e6 !important;
    border-radius: 9px !important;
}

/* Select boxes */
.stSelectbox div[data-baseweb="select"] {
    background: #ffffff !important;
    border-radius: 9px !important;
}

.stSelectbox div[data-baseweb="select"] * {
    color: #172b4d !important;
}

/* Forms */
div[data-testid="stForm"] {
    background: #ffffff;
    padding: 24px;
    border: 1px solid #dce5f1;
    border-radius: 16px;
    box-shadow: 0 4px 15px rgba(20, 43, 80, 0.05);
}

/* Buttons */
.stButton > button,
.stFormSubmitButton > button {
    background: #2459a6 !important;
    color: #ffffff !important;
    border: 1px solid #2459a6 !important;
    border-radius: 10px !important;
    padding: 10px 18px !important;
    font-weight: 700 !important;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: #173f7b !important;
    border-color: #173f7b !important;
    color: #ffffff !important;
}

/* Tables */
div[data-testid="stDataFrame"] {
    background: #ffffff;
    border: 1px solid #dce5f1;
    border-radius: 12px;
    overflow: hidden;
}

/* Alerts */
div[data-testid="stAlert"] {
    border-radius: 12px;
}

/* Dividers */
hr {
    border-color: #dce5f1;
    margin-top: 22px;
    margin-bottom: 22px;
}

/* Hide Streamlit branding */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

/* Mobile */
@media (max-width: 768px) {
    .block-container {
        padding: 1rem;
    }

    h1 {
        font-size: 26px !important;
    }

    div[data-testid="stMetric"] {
        padding: 12px;
    }
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# 3. DATABASE CONNECTION
# =========================================================

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
        pool_pre_ping=True
    )


def load_data(query, params=None):

    with get_engine().connect() as connection:
        return pd.read_sql(
            text(query),
            connection,
            params=params or {}
        )


# =========================================================
# 4. COMMON UI FUNCTIONS
# =========================================================

def page_header(title, subtitle, icon="🏨"):

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(115deg, #142b50, #2459a6);
            padding: 28px 30px;
            border-radius: 16px;
            margin-bottom: 25px;
        ">
            <div style="
                color: #d4e5ff;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 2px;
            ">
                HOTEL MANAGEMENT PLATFORM
            </div>

            <div style="
                color: #ffffff;
                font-size: 29px;
                font-weight: 750;
                margin-top: 8px;
            ">
                {icon} {title}
            </div>

            <div style="
                color: #f0f5ff;
                font-size: 15px;
                margin-top: 8px;
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


# =========================================================
# 5. SIDEBAR
# =========================================================

st.sidebar.markdown("""
<div style="padding: 12px 5px 20px 5px;">
    <div style="font-size: 32px;">🏨</div>
    <div style="
        font-size: 21px;
        font-weight: 750;
        color: #ffffff;
    ">
        HOTEL ANALYZER
    </div>
    <div style="
        font-size: 11px;
        color: #d4e5ff;
        letter-spacing: 1px;
    ">
        MANAGEMENT PLATFORM
    </div>
</div>
""", unsafe_allow_html=True)

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

st.sidebar.markdown("""
<div style="
    background: #1d3153;
    border: 1px solid #40577c;
    border-radius: 10px;
    padding: 13px;
">
    <div style="color: white; font-weight: 700;">
        Database Status
    </div>
    <div style="color: #a7f3d0; font-size: 13px;">
        ● Neon PostgreSQL
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.divider()

st.sidebar.caption("Python | PostgreSQL | Streamlit")


# =========================================================
# 6. DATABASE CHECK
# =========================================================

try:

    engine = get_engine()

    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

except Exception as e:

    show_error(
        "Database connection failed. Check Streamlit Secrets.",
        e
    )

    st.stop()


# =========================================================
# 7. DASHBOARD
# =========================================================

if page == "Dashboard":

    page_header(
        "Welcome to Hotel Analyzer",
        "Manage hotels, rooms, customers and reservations "
        "from one centralized dashboard.",
        "🏨"
    )

    try:

        total_hotels = load_data(
            "SELECT COUNT(*) AS total FROM hotels"
        ).iloc[0]["total"]

        total_rooms = load_data(
            "SELECT COUNT(*) AS total FROM rooms"
        ).iloc[0]["total"]

        total_customers = load_data(
            "SELECT COUNT(*) AS total FROM customers"
        ).iloc[0]["total"]

        total_bookings = load_data(
            "SELECT COUNT(*) AS total FROM bookings"
        ).iloc[0]["total"]

        confirmed = load_data("""
            SELECT COUNT(*) AS total
            FROM bookings
            WHERE status = 'confirmed'
        """).iloc[0]["total"]

        pending = load_data("""
            SELECT COUNT(*) AS total
            FROM bookings
            WHERE status = 'pending'
        """).iloc[0]["total"]

        cancelled = load_data("""
            SELECT COUNT(*) AS total
            FROM bookings
            WHERE status = 'cancelled'
        """).iloc[0]["total"]

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

        st.subheader("Booking Status")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Confirmed", f"{int(confirmed):,}")

        with col2:
            st.metric("Pending", f"{int(pending):,}")

        with col3:
            st.metric("Cancelled", f"{int(cancelled):,}")

        st.divider()

        st.subheader("Recent Bookings")

        recent = load_data("""
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
            JOIN customers c ON b.customer_id = c.customer_id
            JOIN rooms r ON b.room_id = r.room_id
            JOIN hotels h ON r.hotel_id = h.hotel_id
            ORDER BY b.booking_id DESC
            LIMIT 8
        """)

        if recent.empty:
            st.info("No bookings found.")

        else:
            st.dataframe(
                recent,
                use_container_width=True,
                hide_index=True
            )

    except Exception as e:
        show_error("Unable to load dashboard.", e)


# =========================================================
# 8. HOTEL MANAGEMENT
# =========================================================

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
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader("Hotels by City")

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
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        show_error("Unable to load hotels.", e)


# =========================================================
# 9. ROOM MANAGEMENT
# =========================================================

elif page == "Room Management":

    page_header(
        "Room Management",
        "Explore room inventory, categories and base prices.",
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
            JOIN hotels h ON r.hotel_id = h.hotel_id
            ORDER BY h.hotel_name, r.room_number
        """)

        st.metric("Total Rooms", len(df))

        col1, col2 = st.columns(2)

        with col1:

            cities = ["All Cities"] + sorted(
                df["city"].dropna().unique().tolist()
            )

            city_filter = st.selectbox(
                "Choose City",
                cities
            )

        with col2:

            types = ["All Room Types"] + sorted(
                df["room_type"].dropna().unique().tolist()
            )

            type_filter = st.selectbox(
                "Choose Room Type",
                types
            )

        filtered = df.copy()

        if city_filter != "All Cities":
            filtered = filtered[
                filtered["city"] == city_filter
            ]

        if type_filter != "All Room Types":
            filtered = filtered[
                filtered["room_type"] == type_filter
            ]

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader("Room Type Distribution")

        room_types = (
            filtered.groupby("room_type")
            .size()
            .reset_index(name="total_rooms")
        )

        fig = px.pie(
            room_types,
            names="room_type",
            values="total_rooms",
            hole=0.45
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        show_error("Unable to load rooms.", e)


# =========================================================
# 10. CUSTOMER MANAGEMENT
# =========================================================

elif page == "Customer Management":

    page_header(
        "Customer Management",
        "Select a hotel to view its customers, search records "
        "and register new customers.",
        "👥"
    )

    try:

        # Get hotels for the filter
        hotels_df = load_data("""
            SELECT hotel_id, hotel_name, city
            FROM hotels
            ORDER BY hotel_name
        """)

        # Hotel selection
        st.subheader("Choose Hotel")

        hotel_options = {
            f"{row.hotel_name} — {row.city}": int(row.hotel_id)
            for row in hotels_df.itertuples()
        }

        hotel_labels = ["All Hotels"] + list(hotel_options.keys())

        selected_hotel = st.selectbox(
            "Select Hotel to View Customers",
            hotel_labels,
            key="customer_hotel_filter"
        )

        if selected_hotel == "All Hotels":
            selected_hotel_id = None
        else:
            selected_hotel_id = hotel_options[selected_hotel]

        # Get customers
        if selected_hotel_id is None:

            customers_df = load_data("""
                SELECT
                    customer_id,
                    customer_name,
                    email,
                    phone
                FROM customers
                ORDER BY customer_id DESC
            """)

        else:

            customers_df = load_data("""
                SELECT DISTINCT
                    c.customer_id,
                    c.customer_name,
                    c.email,
                    c.phone
                FROM customers c
                JOIN bookings b
                    ON c.customer_id = b.customer_id
                JOIN rooms r
                    ON b.room_id = r.room_id
                WHERE r.hotel_id = :hotel_id
                ORDER BY c.customer_id DESC
            """, {
                "hotel_id": selected_hotel_id
            })

        # Customer metrics
        st.divider()

        st.subheader("Customer Overview")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Customers Displayed",
                len(customers_df)
            )

        with col2:
            st.metric(
                "Registered Customers",
                int(
                    load_data("""
                        SELECT COUNT(*) AS total
                        FROM customers
                    """).iloc[0]["total"]
                )
            )

        # Search
        st.divider()

        st.subheader("Customer Records")

        search = st.text_input(
            "Search Customer",
            placeholder="Search by name or email..."
        )

        filtered_customers = customers_df.copy()

        if search:

            mask = (
                filtered_customers["customer_name"].str.contains(
                    search,
                    case=False,
                    na=False
                )
                |
                filtered_customers["email"].str.contains(
                    search,
                    case=False,
                    na=False
                )
            )

            filtered_customers = filtered_customers[mask]

        if filtered_customers.empty:
            st.info(
                "No customers found for this hotel. "
                "Customers appear here after making a booking."
            )

        else:

            st.dataframe(
                filtered_customers,
                use_container_width=True,
                hide_index=True
            )

        # Register customer
        st.divider()

        st.subheader("➕ Register New Customer")

        with st.form("new_customer_form"):

            name = st.text_input(
                "Customer Name",
                placeholder="Enter full name"
            )

            email = st.text_input(
                "Email Address",
                placeholder="example@email.com"
            )

            phone = st.text_input(
                "Phone Number",
                placeholder="Enter phone number"
            )

            register = st.form_submit_button(
                "Register Customer",
                use_container_width=True,
                type="primary"
            )

        if register:

            if not name.strip():
                st.error("Enter customer name.")

            elif not re.match(
                r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
                email.strip()
            ):
                st.error("Enter a valid email address.")

            else:

                try:

                    with get_engine().begin() as connection:

                        result = connection.execute(
                            text("""
                                INSERT INTO customers (
                                    customer_name,
                                    email,
                                    phone
                                )
                                VALUES (
                                    :name,
                                    :email,
                                    :phone
                                )
                                ON CONFLICT (email)
                                DO NOTHING
                                RETURNING customer_id
                            """),
                            {
                                "name": name.strip(),
                                "email": email.strip().lower(),
                                "phone": phone.strip() or None
                            }
                        )

                        new_customer_id = result.scalar_one_or_none()

                    if new_customer_id is None:

                        st.warning(
                            "This email address is already registered."
                        )

                    else:

                        st.success(
                            f"Customer registered successfully! "
                            f"Customer ID: {new_customer_id}"
                        )

                        st.rerun()

                except Exception as e:
                    show_error("Customer registration failed.", e)

    except Exception as e:
        show_error("Unable to load customer management.", e)


# =========================================================
# 11. BOOKING MANAGEMENT
# =========================================================

elif page == "Booking Management":

    page_header(
        "Booking Management",
        "Create reservations and manage hotel bookings.",
        "📅"
    )

    # Existing bookings
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
            JOIN customers c ON b.customer_id = c.customer_id
            JOIN rooms r ON b.room_id = r.room_id
            JOIN hotels h ON r.hotel_id = h.hotel_id
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

        st.dataframe(
            bookings_df,
            use_container_width=True,
            hide_index=True
        )

    except Exception as e:
        show_error("Unable to load bookings.", e)


    st.divider()

    st.subheader("Create a New Booking")

    try:

        hotels_df = load_data("""
            SELECT hotel_id, hotel_name, city
            FROM hotels
            ORDER BY hotel_name
        """)

        if hotels_df.empty:

            st.warning("No hotels available.")

        else:

            # Hotel
            hotel_options = {
                f"{row.hotel_name} — {row.city}": int(row.hotel_id)
                for row in hotels_df.itertuples()
            }

            selected_hotel = st.selectbox(
                "Choose Hotel",
                list(hotel_options.keys()),
                key="booking_hotel"
            )

            hotel_id = hotel_options[selected_hotel]

            # Dates
            date_col1, date_col2 = st.columns(2)

            with date_col1:

                check_in = st.date_input(
                    "Check-in",
                    value=date.today(),
                    min_value=date.today(),
                    key="booking_checkin"
                )

            with date_col2:

                check_out = st.date_input(
                    "Check-out",
                    value=date.today() + timedelta(days=1),
                    min_value=date.today() + timedelta(days=1),
                    key="booking_checkout"
                )

            # Search available rooms
            if check_out <= check_in:

                st.warning(
                    "Check-out must be after check-in."
                )

                available_rooms = pd.DataFrame()

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

            st.subheader("Available Rooms")

            if available_rooms.empty:

                st.warning(
                    "No rooms available for these dates."
                )

            else:

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
                        "room_number": row.room_number,
                        "base_price": float(row.base_price)
                    }

                selected_room = st.selectbox(
                    "Choose Room",
                    list(room_options.keys()),
                    key="booking_room"
                )

                room_details = room_options[selected_room]

                nights = (check_out - check_in).days

                total_price = (
                    room_details["base_price"] * nights
                )

                # Summary
                st.divider()

                st.subheader("Booking Summary")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Room Number",
                        room_details["room_number"]
                    )

                with col2:
                    st.metric(
                        "Number of Nights",
                        nights
                    )

                with col3:
                    st.metric(
                        "Total Amount",
                        f"₹{total_price:,.2f}"
                    )

                st.caption(
                    "The booking amount uses the room's base price "
                    "per night. No payment is processed by this form."
                )

                st.divider()

                # Customer details
                st.subheader("Customer Details")

                with st.form("new_booking_form"):

                    customer_name = st.text_input(
                        "Customer Name"
                    )

                    customer_email = st.text_input(
                        "Email Address"
                    )

                    customer_phone = st.text_input(
                        "Phone Number"
                    )

                    submit = st.form_submit_button(
                        "Confirm Booking",
                        use_container_width=True,
                        type="primary"
                    )

                if submit:

                    if not customer_name.strip():

                        st.error("Enter customer name.")

                    elif not re.match(
                        r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
                        customer_email.strip()
                    ):

                        st.error("Enter a valid email address.")

                    else:

                        try:

                            with get_engine().begin() as connection:

                                # Lock room
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
                                        "Selected room does not exist."
                                    )

                                # Final overlap check
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
                                        "booked for these dates."
                                    )

                                # Create or reuse customer
                                customer_result = connection.execute(
                                    text("""
                                        INSERT INTO customers (
                                            customer_name,
                                            email,
                                            phone
                                        )
                                        VALUES (
                                            :name,
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
                                        "name": customer_name.strip(),
                                        "email":
                                            customer_email.strip().lower(),
                                        "phone":
                                            customer_phone.strip() or None
                                    }
                                )

                                customer_id = customer_result.scalar_one()

                                # Create booking
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

                                booking_id = booking_result.scalar_one()

                            st.success(
                                f"Booking confirmed! Booking ID: {booking_id}"
                            )

                            st.rerun()

                        except IntegrityError:
                            st.error(
                                "PostgreSQL rejected this booking "
                                "because it conflicts with an existing booking."
                            )

                        except Exception as e:
                            show_error("Booking failed.", e)

    except Exception as e:
        show_error("Unable to load booking form.", e)


# =========================================================
# 12. DYNAMIC PRICING
# =========================================================

elif page == "Dynamic Pricing":

    page_header(
        "Dynamic Pricing Analyzer",
        "Explore room prices based on occupancy, demand "
        "and weekend adjustments.",
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
            JOIN rooms r ON p.room_id = r.room_id
            JOIN hotels h ON r.hotel_id = h.hotel_id
            ORDER BY p.effective_date DESC
            LIMIT 5000
        """)

        if df.empty:

            st.warning("No pricing records found.")

        else:

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Pricing Records", len(df))

            with col2:
                st.metric(
                    "Average Dynamic Price",
                    f"₹{df['dynamic_price'].mean():,.2f}"
                )

            st.divider()

            hotel_filter = st.selectbox(
                "Choose Hotel",
                ["All Hotels"] + sorted(
                    df["hotel_name"].dropna().unique().tolist()
                )
            )

            if hotel_filter != "All Hotels":
                df = df[df["hotel_name"] == hotel_filter]

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

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
                ]
            )

            st.plotly_chart(fig, use_container_width=True)

            st.info(
                "These are synthetic project prices, not live hotel rates."
            )

    except Exception as e:
        show_error("Unable to load dynamic pricing.", e)


# =========================================================
# 13. ANALYTICS
# =========================================================

elif page == "Analytics":

    page_header(
        "Hotel Analytics",
        "Analyze property performance, bookings, revenue "
        "and occupancy.",
        "📊"
    )

    try:

        df = load_data("""
            SELECT
                h.hotel_id,
                h.hotel_name,
                h.city,

                COUNT(DISTINCT r.room_id) AS total_rooms,

                COUNT(DISTINCT b.booking_id) AS total_bookings,

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

        st.subheader("Hotel Performance")

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        total_bookings = int(df["total_bookings"].sum())

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
            st.metric("Total Bookings", total_bookings)

        with col2:
            st.metric("Cancelled Bookings", total_cancelled)

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

        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("Bookings by Hotel")

        fig2 = px.bar(
            df.nlargest(10, "total_bookings"),
            x="hotel_name",
            y="total_bookings",
            color="city",
            title="Top 10 Hotels by Bookings"
        )

        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Current Occupancy")

        fig3 = px.bar(
            df.nlargest(
                10,
                "current_occupancy_percentage"
            ),
            x="hotel_name",
            y="current_occupancy_percentage",
            color="city",
            title="Current Hotel Occupancy"
        )

        fig3.update_layout(
            yaxis_title="Occupancy (%)"
        )

        st.plotly_chart(fig3, use_container_width=True)

    except Exception as e:
        show_error("Unable to load analytics.", e)


# =========================================================
# 14. FOOTER
# =========================================================

st.markdown("""
<div style="
    text-align: center;
    padding: 25px 10px 10px 10px;
    color: #52647e;
    font-size: 13px;
    border-top: 1px solid #dce5f1;
    margin-top: 35px;
">
    Hotel Multi-Property Booking & Dynamic Pricing Analyzer
    <br>
    Python | PostgreSQL | SQLAlchemy | Streamlit
</div>
""", unsafe_allow_html=True)
