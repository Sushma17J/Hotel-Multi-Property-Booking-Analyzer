import streamlit as st
import pandas as pd
import plotly.express as px

from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from datetime import date, timedelta


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Hotel Analyzer",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# 2. CUSTOM CSS
# ============================================================

st.markdown("""
<style>

/* Main background */
.stApp {
    background-color: #e8eef7;
    color: #172033;
}

[data-testid="stAppViewContainer"] {
    background-color: #e8eef7;
}

[data-testid="stHeader"] {
    background-color: #e8eef7;
}

/* Sidebar */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div:first-child {
    background-color: #101d35 !important;
}

/* Sidebar text */
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {
    color: #ffffff !important;
}

/* Sidebar navigation */
[data-testid="stSidebar"] .stRadio > div {
    gap: 10px;
}

[data-testid="stSidebar"] .stRadio label {
    background-color: #1c2d4b;
    color: #ffffff !important;
    padding: 12px 14px;
    border-radius: 9px;
    border: 1px solid #354966;
    font-size: 15px;
    font-weight: 600;
    transition: 0.2s ease;
}
/* Navigation hover */
[data-testid="stSidebar"] .stRadio label:hover {
    background-color: #29466e;
    border-color: #60a5fa;
}

/* Selected navigation */
[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background-color: #2563eb;
    border: 1px solid #60a5fa;
}

/* Sidebar divider */
[data-testid="stSidebar"] hr {
    border-color: #40516d;
}

/* Main headings */
h1, h2, h3, h4 {
    color: #14213d !important;
}

/* Main text */
.stMarkdown p {
    color: #26344d;
}

/* Metric cards */
[data-testid="stMetric"] {
    background-color: #ffffff;
    border: 1px solid #cbd8e8;
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0 3px 10px rgba(15, 35, 65, 0.07);
}

[data-testid="stMetricLabel"] {
    color: #52627a !important;
}

[data-testid="stMetricValue"] {
    color: #14213d !important;
}

/* Buttons */
.stButton > button,
.stFormSubmitButton > button {
    background-color: #2563eb;
    color: #ffffff !important;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 8px 18px;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background-color: #1d4ed8;
    color: #ffffff !important;
}

/* Input fields */
input, textarea {
    color: #172033 !important;
}

/* Select boxes */
[data-baseweb="select"] {
    color: #172033 !important;
}

/* Tables */
[data-testid="stDataFrame"] {
    background-color: #ffffff;
    border-radius: 10px;
}

/* Dividers */
hr {
    border-color: #cbd8e8;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# 3. DATABASE CONNECTION
# ============================================================

@st.cache_resource
def get_engine():

    database_url = st.secrets["NEON_DATABASE_URL"]

    database_url = database_url.replace(
        "postgresql://",
        "postgresql+psycopg2://",
        1
    )

    return create_engine(
        database_url,
        pool_pre_ping=True
    )


engine = get_engine()


# ============================================================
# 4. DATABASE HELPER FUNCTIONS
# ============================================================

def read_data(query, params=None):

    with engine.connect() as connection:

        return pd.read_sql(
            text(query),
            connection,
            params=params or {}
        )


def execute_query(query, params=None):

    with engine.begin() as connection:

        connection.execute(
            text(query),
            params or {}
        )


def format_currency(value):

    if pd.isna(value):
        return "₹0"

    return "₹{:,.2f}".format(float(value))


def page_header(title, subtitle):

    st.markdown(
        f"""
        <div style="
            color: #14213d;
            font-size: 29px;
            font-weight: 750;
            margin-top: 8px;
            margin-bottom: 5px;
        ">
            {title}
        </div>

        <div style="
            color: #52627a;
            font-size: 15px;
            margin-top: 8px;
            margin-bottom: 22px;
        ">
            {subtitle}
        </div>
        """,
        unsafe_allow_html=True
    )


def load_hotels():

    return read_data("""
        SELECT
            hotel_id,
            hotel_name,
            city,
            address,
            star_rating
        FROM hotels
        ORDER BY hotel_name
    """)


def load_rooms():

    return read_data("""
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


def load_customers():

    return read_data("""
        SELECT
            customer_id,
            customer_name,
            email,
            phone
        FROM customers
        ORDER BY customer_id DESC
    """)


def load_bookings():

    return read_data("""
        SELECT
            b.booking_id,
            h.hotel_name,
            r.room_number,
            r.room_type,
            c.customer_name,
            c.email,
            b.check_in,
            b.check_out,
            b.total_price,
            b.status
        FROM bookings b
        JOIN rooms r
            ON b.room_id = r.room_id
        JOIN hotels h
            ON r.hotel_id = h.hotel_id
        JOIN customers c
            ON b.customer_id = c.customer_id
        ORDER BY b.booking_id DESC
    """)


# ============================================================
# 5. SIDEBAR NAVIGATION
# ============================================================

st.sidebar.markdown("""
<div style="
    font-size: 25px;
    font-weight: 800;
    color: #ffffff;
    padding: 12px 0 5px 0;
">
    🏨 Hotel Analyzer
</div>

<div style="
    font-size: 12px;
    color: #cbd5e1;
    margin-bottom: 25px;
">
    Multi-Property Booking System
</div>
""", unsafe_allow_html=True)


page = st.sidebar.radio(
    "",
    [
        "Dashboard",
        "Hotel Management",
        "Room Management",
        "Customer Management",
        "Booking Management",
        "Dynamic Pricing",
        "Analytics"
    ],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")

st.sidebar.caption(
    "Hotel Multi-Property Booking & Dynamic Pricing Analyzer"
)


# ============================================================
# 6. DASHBOARD
# ============================================================

if page == "Dashboard":

    page_header(
        "🏨 Welcome to Hotel Analyzer",
        "Manage hotels, rooms, customers and reservations from one centralized dashboard."
    )

    hotels = load_hotels()
    rooms = load_rooms()
    customers = load_customers()
    bookings = load_bookings()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🏨 Total Hotels", len(hotels))
    col2.metric("🛏️ Total Rooms", len(rooms))
    col3.metric("👥 Total Customers", len(customers))
    col4.metric("📅 Total Bookings", len(bookings))

    confirmed = 0
    pending = 0
    cancelled = 0

    if not bookings.empty:

        statuses = bookings["status"].astype(str).str.lower()

        confirmed = (statuses == "confirmed").sum()
        pending = (statuses == "pending").sum()
        cancelled = (statuses == "cancelled").sum()

    st.markdown("---")

    st.subheader("Booking Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Confirmed Bookings", int(confirmed))
    col2.metric("Pending Bookings", int(pending))
    col3.metric("Cancelled Bookings", int(cancelled))

    st.markdown("---")

    left, right = st.columns(2)

    with left:

        st.subheader("Hotels by City")

        if not hotels.empty:

            city_data = (
                hotels.groupby("city")
                .size()
                .reset_index(name="Hotels")
            )

            fig = px.bar(
                city_data,
                x="city",
                y="Hotels",
                color="city",
                title="Property Distribution by City"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info("No hotel records available.")

    with right:

        st.subheader("Booking Status")

        if not bookings.empty:

            status_data = (
                bookings["status"]
                .astype(str)
                .value_counts()
                .reset_index()
            )

            status_data.columns = ["Status", "Bookings"]

            fig = px.pie(
                status_data,
                names="Status",
                values="Bookings",
                hole=0.45
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info("No booking records available.")

    st.subheader("Recent Bookings")

    if not bookings.empty:

        st.dataframe(
            bookings.head(10),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No bookings available yet.")


# ============================================================
# 7. HOTEL MANAGEMENT
# ============================================================

elif page == "Hotel Management":

    page_header(
        "🏨 Hotel Management",
        "View and manage hotel properties, locations and hotel information."
    )

    hotels = load_hotels()

    if not hotels.empty:

        star_ratings = pd.to_numeric(
            hotels["star_rating"],
            errors="coerce"
        ).dropna()

        average_rating = (
            f"{star_ratings.mean():.1f} / 5"
            if not star_ratings.empty
            else "Not Available"
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Hotels",
            len(hotels)
        )

        col2.metric(
            "Cities Covered",
            hotels["city"].nunique()
        )

        col3.metric(
            "Average Star Rating",
            average_rating
        )

        st.markdown("---")

        st.subheader("Hotel Records")

        city_options = ["All Cities"] + sorted(
            hotels["city"].dropna().unique().tolist()
        )

        selected_city = st.selectbox(
            "Filter by City",
            city_options
        )

        filtered_hotels = hotels.copy()

        if selected_city != "All Cities":

            filtered_hotels = filtered_hotels[
                filtered_hotels["city"] == selected_city
            ]

        st.dataframe(
            filtered_hotels,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Hotels by City")

        city_chart = (
            hotels.groupby("city")
            .size()
            .reset_index(name="Number of Hotels")
        )

        fig = px.bar(
            city_chart,
            x="city",
            y="Number of Hotels",
            color="city",
            title="Hotel Distribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.warning("No hotel records found.")


# ============================================================
# 8. ROOM MANAGEMENT
# ============================================================

elif page == "Room Management":

    page_header(
        "🛏️ Room Management",
        "Manage room details, room types, capacity and room information."
    )

    rooms = load_rooms()

    if not rooms.empty:

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Rooms", len(rooms))

        col2.metric(
            "Room Types",
            rooms["room_type"].nunique()
        )

        col3.metric(
            "Average Base Price",
            format_currency(rooms["base_price"].mean())
        )

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:

            hotel_options = ["All Hotels"] + sorted(
                rooms["hotel_name"].dropna().unique().tolist()
            )

            selected_hotel = st.selectbox(
                "Filter by Hotel",
                hotel_options
            )

        with col2:

            type_options = ["All Types"] + sorted(
                rooms["room_type"].dropna().unique().tolist()
            )

            selected_type = st.selectbox(
                "Filter by Room Type",
                type_options
            )

        filtered_rooms = rooms.copy()

        if selected_hotel != "All Hotels":

            filtered_rooms = filtered_rooms[
                filtered_rooms["hotel_name"] == selected_hotel
            ]

        if selected_type != "All Types":

            filtered_rooms = filtered_rooms[
                filtered_rooms["room_type"] == selected_type
            ]

        st.subheader("Room Records")

        st.dataframe(
            filtered_rooms,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Room Type Distribution")

        room_chart = (
            rooms.groupby("room_type")
            .size()
            .reset_index(name="Number of Rooms")
        )

        fig = px.pie(
            room_chart,
            names="room_type",
            values="Number of Rooms",
            hole=0.4
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.warning("No room records found.")


# ============================================================
# 9. CUSTOMER MANAGEMENT
# ============================================================

elif page == "Customer Management":

    page_header(
        "👥 Customer Management",
        "Select a hotel to view its customers, search records and register new customers."
    )

    hotels = load_hotels()

    if hotels.empty:

        st.warning("Please add hotel records before managing customers.")

    else:

        hotel_options = {
            "All Hotels": None
        }

        for _, hotel in hotels.iterrows():

            label = (
                f"{hotel['hotel_name']} - {hotel['city']}"
            )

            hotel_options[label] = int(hotel["hotel_id"])

        selected_hotel_label = st.selectbox(
            "🏨 Choose Hotel",
            list(hotel_options.keys()),
            key="customer_hotel_filter"
        )

        selected_hotel_id = hotel_options[
            selected_hotel_label
        ]

        if selected_hotel_id is None:

            customers = read_data("""
                SELECT
                    customer_id,
                    customer_name,
                    email,
                    phone
                FROM customers
                ORDER BY customer_id DESC
            """)

        else:

            customers = read_data(
                """
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
                """,
                {"hotel_id": selected_hotel_id}
            )

        col1, col2 = st.columns(2)

        col1.metric(
            "Customers Displayed",
            len(customers)
        )

        all_customers = load_customers()

        col2.metric(
            "Total Registered Customers",
            len(all_customers)
        )

        st.markdown("---")

        st.subheader("Search Customers")

        search = st.text_input(
            "Search by customer name or email",
            placeholder="Enter customer name or email"
        )

        filtered_customers = customers.copy()

        if search:

            filtered_customers = filtered_customers[
                filtered_customers["customer_name"]
                .astype(str)
                .str.contains(search, case=False, na=False)
                |
                filtered_customers["email"]
                .astype(str)
                .str.contains(search, case=False, na=False)
            ]

        st.dataframe(
            filtered_customers,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        st.subheader("➕ Register New Customer")

        with st.form("register_customer_form"):

            customer_name = st.text_input(
                "Customer Name"
            )

            customer_email = st.text_input(
                "Email Address"
            )

            customer_phone = st.text_input(
                "Phone Number"
            )

            submit_customer = st.form_submit_button(
                "Register Customer",
                type="primary"
            )

            if submit_customer:

                if not customer_name.strip():

                    st.error("Please enter the customer name.")

                elif not customer_email.strip():

                    st.error("Please enter the email address.")

                elif "@" not in customer_email:

                    st.error("Please enter a valid email address.")

                else:

                    try:

                        execute_query(
                            """
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
                            """,
                            {
                                "name": customer_name.strip(),
                                "email": customer_email.strip().lower(),
                                "phone": customer_phone.strip()
                            }
                        )

                        st.success(
                            "Customer registration completed. "
                            "If the email already existed, the existing record was kept."
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Unable to register customer: {e}"
                        )

        st.caption(
            "Hotel-specific customer records are based on booking history. "
            "A customer appears under a particular hotel after making a booking there."
        )


# ============================================================
# 10. BOOKING MANAGEMENT
# ============================================================

elif page == "Booking Management":

    page_header(
        "📅 Booking Management",
        "Create reservations, check room availability and manage customer bookings."
    )

    bookings = load_bookings()

    if not bookings.empty:

        confirmed_count = (
            bookings["status"].astype(str).str.lower()
            == "confirmed"
        ).sum()

        cancelled_count = (
            bookings["status"].astype(str).str.lower()
            == "cancelled"
        ).sum()

    else:

        confirmed_count = 0
        cancelled_count = 0

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Bookings", len(bookings))
    col2.metric("Confirmed", int(confirmed_count))
    col3.metric("Cancelled", int(cancelled_count))

    st.markdown("---")

    st.subheader("➕ Create a New Booking")

    hotels = load_hotels()

    if hotels.empty:

        st.warning("No hotels available.")

    else:

        hotel_labels = {
            f"{row['hotel_name']} - {row['city']}":
            int(row["hotel_id"])
            for _, row in hotels.iterrows()
        }

        selected_hotel = st.selectbox(
            "Select Hotel",
            list(hotel_labels.keys()),
            key="booking_hotel"
        )

        hotel_id = hotel_labels[selected_hotel]

        col1, col2 = st.columns(2)

        with col1:

            check_in = st.date_input(
                "Check-in Date",
                value=date.today() + timedelta(days=1),
                min_value=date.today(),
                key="booking_checkin"
            )

        with col2:

            check_out = st.date_input(
                "Check-out Date",
                value=date.today() + timedelta(days=2),
                min_value=date.today() + timedelta(days=1),
                key="booking_checkout"
            )

        available_rooms = pd.DataFrame()

        if check_out <= check_in:

            st.error(
                "Check-out date must be after check-in date."
            )

        else:

            available_rooms = read_data(
                """
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
                    AND daterange(
                        b.check_in,
                        b.check_out,
                        '[)'
                    ) &&
                    daterange(
                        :check_in,
                        :check_out,
                        '[)'
                    )
                )
                ORDER BY r.room_number
                """,
                {
                    "hotel_id": hotel_id,
                    "check_in": check_in,
                    "check_out": check_out
                }
            )

        if not available_rooms.empty:

            room_options = {}

            for _, room in available_rooms.iterrows():

                label = (
                    f"Room {room['room_number']} | "
                    f"{room['room_type']} | "
                    f"₹{float(room['base_price']):,.2f} per night"
                )

                room_options[label] = room

            selected_room_label = st.selectbox(
                "Select Available Room",
                list(room_options.keys())
            )

            selected_room = room_options[selected_room_label]

            nights = (check_out - check_in).days

            estimated_price = (
                float(selected_room["base_price"]) * nights
            )

            st.info(
                f"Stay: {nights} night(s) | "
                f"Estimated booking amount: {format_currency(estimated_price)}"
            )

            st.markdown("---")

            st.subheader("Customer Details")

            with st.form("create_booking_form"):

                booking_customer_name = st.text_input(
                    "Customer Name"
                )

                booking_customer_email = st.text_input(
                    "Customer Email"
                )

                booking_customer_phone = st.text_input(
                    "Customer Phone Number"
                )

                submit_booking = st.form_submit_button(
                    "Confirm Booking",
                    type="primary"
                )

                if submit_booking:

                    if not booking_customer_name.strip():

                        st.error("Enter customer name.")

                    elif not booking_customer_email.strip():

                        st.error("Enter customer email.")

                    elif "@" not in booking_customer_email:

                        st.error("Enter a valid customer email.")

                    else:

                        try:

                            with engine.begin() as connection:

                                # Lock the selected room row.
                                room_check = connection.execute(
                                    text("""
                                        SELECT room_id, base_price
                                        FROM rooms
                                        WHERE room_id = :room_id
                                        FOR UPDATE
                                    """),
                                    {
                                        "room_id": int(
                                            selected_room["room_id"]
                                        )
                                    }
                                ).mappings().first()

                                if room_check is None:

                                    raise ValueError(
                                        "Selected room no longer exists."
                                    )

                                # Recheck overlapping bookings.
                                overlap = connection.execute(
                                    text("""
                                        SELECT booking_id
                                        FROM bookings
                                        WHERE room_id = :room_id
                                        AND status <> 'cancelled'
                                        AND daterange(
                                            check_in,
                                            check_out,
                                            '[)'
                                        ) &&
                                        daterange(
                                            :check_in,
                                            :check_out,
                                            '[)'
                                        )
                                        LIMIT 1
                                    """),
                                    {
                                        "room_id": int(
                                            selected_room["room_id"]
                                        ),
                                        "check_in": check_in,
                                        "check_out": check_out
                                    }
                                ).first()

                                if overlap:

                                    raise ValueError(
                                        "This room has already been booked "
                                        "for the selected dates. Please choose another room."
                                    )

                                # Find existing customer or create a new one.
                                customer_id = connection.execute(
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
                                            phone =
                                                EXCLUDED.phone
                                        RETURNING customer_id
                                    """),
                                    {
                                        "name": booking_customer_name.strip(),
                                        "email": booking_customer_email.strip().lower(),
                                        "phone": booking_customer_phone.strip()
                                    }
                                ).scalar_one()

                                # Calculate final price.
                                final_price = (
                                    float(room_check["base_price"])
                                    * nights
                                )

                                # Insert booking.
                                booking_id = connection.execute(
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
                                        "room_id": int(
                                            selected_room["room_id"]
                                        ),
                                        "customer_id": customer_id,
                                        "check_in": check_in,
                                        "check_out": check_out,
                                        "total_price": final_price
                                    }
                                ).scalar_one()

                            st.success(
                                f"Booking confirmed successfully! "
                                f"Booking ID: {booking_id}"
                            )

                            st.info(
                                f"Total booking amount: "
                                f"{format_currency(final_price)}"
                            )

                            st.rerun()

                        except IntegrityError:

                            st.error(
                                "Booking rejected by the database. "
                                "This room is already booked for overlapping dates."
                            )

                        except Exception as e:

                            st.error(
                                f"Booking failed: {e}"
                            )

        elif check_out > check_in:

            st.warning(
                "No rooms are available for these dates at this hotel."
            )

    st.markdown("---")

    st.subheader("Existing Bookings")

    bookings = load_bookings()

    if not bookings.empty:

        search_booking = st.text_input(
            "Search by customer name or hotel",
            key="booking_search"
        )

        filtered_bookings = bookings.copy()

        if search_booking:

            filtered_bookings = filtered_bookings[
                filtered_bookings["customer_name"]
                .astype(str)
                .str.contains(
                    search_booking,
                    case=False,
                    na=False
                )
                |
                filtered_bookings["hotel_name"]
                .astype(str)
                .str.contains(
                    search_booking,
                    case=False,
                    na=False
                )
            ]

        st.dataframe(
            filtered_bookings,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No bookings available.")


# ============================================================
# 11. DYNAMIC PRICING
# ============================================================

elif page == "Dynamic Pricing":

    page_header(
        "💰 Dynamic Pricing",
        "Analyze room prices and understand how demand, occupancy and weekends affect pricing."
    )

    pricing = read_data("""
        SELECT
            p.price_id,
            h.hotel_name,
            h.city,
            r.room_number,
            r.room_type,
            p.price,
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

    if not pricing.empty:

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Pricing Records Displayed",
            len(pricing)
        )

        col2.metric(
            "Average Room Price",
            format_currency(pricing["price"].mean())
        )

        col3.metric(
            "Hotels Covered",
            pricing["hotel_name"].nunique()
        )

        st.markdown("---")

        st.subheader("Filter Pricing Records")

        hotel_options = ["All Hotels"] + sorted(
            pricing["hotel_name"].dropna().unique().tolist()
        )

        selected_hotel = st.selectbox(
            "Select Hotel",
            hotel_options,
            key="pricing_hotel"
        )

        filtered_pricing = pricing.copy()

        if selected_hotel != "All Hotels":

            filtered_pricing = filtered_pricing[
                filtered_pricing["hotel_name"] == selected_hotel
            ]

        st.dataframe(
            filtered_pricing,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Room Price Analysis")

        fig = px.scatter(
            filtered_pricing,
            x="effective_date",
            y="price",
            color="room_type",
            hover_data=[
                "hotel_name",
                "room_number",
                "pricing_reason"
            ],
            title="Room Prices Over Time"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.caption(
            "These are synthetic demonstration prices generated "
            "by the project's dynamic pricing logic, not live hotel rates."
        )

    else:

        st.warning(
            "No pricing history found. Please check the pricing_history table."
        )


# ============================================================
# 12. ANALYTICS - NO REVENUE
# ============================================================

elif page == "Analytics":

    page_header(
        "📊 Hotel Analytics",
        "Analyze hotel performance, booking trends and current room occupancy."
    )

    # Booking analysis
    analytics = read_data("""
        SELECT
            h.hotel_name,
            h.city,
            COUNT(b.booking_id) AS total_bookings
        FROM hotels h
        LEFT JOIN rooms r
            ON h.hotel_id = r.hotel_id
        LEFT JOIN bookings b
            ON r.room_id = b.room_id
        GROUP BY h.hotel_id, h.hotel_name, h.city
        ORDER BY total_bookings DESC
    """)

    # Total rooms per hotel
    room_counts = read_data("""
        SELECT
            h.hotel_name,
            COUNT(r.room_id) AS total_rooms
        FROM hotels h
        LEFT JOIN rooms r
            ON h.hotel_id = r.hotel_id
        GROUP BY h.hotel_id, h.hotel_name
    """)

    # Rooms occupied today
    occupancy = read_data("""
        SELECT
            h.hotel_name,
            COUNT(DISTINCT b.room_id) AS booked_rooms
        FROM hotels h
        LEFT JOIN rooms r
            ON h.hotel_id = r.hotel_id
        LEFT JOIN bookings b
            ON r.room_id = b.room_id
            AND b.status IN (
                'confirmed',
                'checked_in'
            )
            AND CURRENT_DATE >= b.check_in
            AND CURRENT_DATE < b.check_out
        GROUP BY h.hotel_id, h.hotel_name
    """)

    if not analytics.empty:

        # Summary metrics
        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Bookings",
            int(analytics["total_bookings"].sum())
        )

        col2.metric(
            "Hotels Analyzed",
            len(analytics)
        )

        col3.metric(
            "Cities Covered",
            analytics["city"].nunique()
        )

        st.markdown("---")

        # Hotel booking performance
        st.subheader("🏨 Hotel Booking Performance")

        st.dataframe(
            analytics,
            use_container_width=True,
            hide_index=True
        )

        # Booking chart
        st.subheader("📅 Bookings by Hotel")

        fig = px.bar(
            analytics.sort_values(
                "total_bookings",
                ascending=False
            ),
            x="hotel_name",
            y="total_bookings",
            color="city",
            title="Booking Distribution Across Hotels",
            labels={
                "hotel_name": "Hotel",
                "total_bookings": "Number of Bookings",
                "city": "City"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.markdown("---")

        # Occupancy calculation
        st.subheader("🛏️ Current Room Occupancy")

        occupancy_report = room_counts.merge(
            occupancy,
            on="hotel_name",
            how="left"
        )

        occupancy_report["booked_rooms"] = (
            occupancy_report["booked_rooms"].fillna(0)
        )

        occupancy_report["occupancy_percentage"] = (
            occupancy_report["booked_rooms"]
            / occupancy_report["total_rooms"].replace(0, pd.NA)
            * 100
        ).fillna(0)

        occupancy_report["occupancy_percentage"] = (
            occupancy_report["occupancy_percentage"].round(2)
        )

        st.dataframe(
            occupancy_report,
            use_container_width=True,
            hide_index=True
        )

        # Occupancy chart
        fig = px.bar(
            occupancy_report,
            x="hotel_name",
            y="occupancy_percentage",
            color="hotel_name",
            title="Current Occupancy Percentage by Hotel",
            labels={
                "hotel_name": "Hotel",
                "occupancy_percentage": "Occupancy (%)"
            }
        )

        fig.update_layout(
            yaxis_title="Occupancy (%)",
            yaxis_range=[0, 100],
            showlegend=False
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.caption(
            "Occupancy represents rooms with active bookings today."
        )

    else:

        st.warning("No analytics data available.")


# ============================================================
# 13. FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    """
    <div style="
        text-align: center;
        color: #52627a;
        font-size: 12px;
        padding: 10px;
    ">
        🏨 Hotel Multi-Property Booking & Dynamic Pricing Analyzer
        <br>
        Built using Python, Streamlit and PostgreSQL
    </div>
    """,
    unsafe_allow_html=True
)
