import streamlit as st
import pandas as pd
import plotly.express as px

from sqlalchemy import create_engine, text


# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Hotel Booking Analyzer",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =====================================================
# 2. DATABASE CONNECTION
# =====================================================

@st.cache_resource
def get_engine():

    database_url = st.secrets["NEON_DATABASE_URL"]

    if database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://",
            "postgresql+psycopg2://",
            1
        )

    engine = create_engine(
        database_url,
        pool_pre_ping=True
    )

    return engine


# =====================================================
# 3. DATABASE QUERY FUNCTION
# =====================================================

def load_data(query, params=None):

    engine = get_engine()

    with engine.connect() as connection:

        df = pd.read_sql(
            text(query),
            connection,
            params=params or {}
        )

    return df


# =====================================================
# 4. APPLICATION HEADER
# =====================================================

st.sidebar.title("🏨 Hotel Analyzer")

st.sidebar.caption(
    "Multi-Property Booking & Dynamic Pricing System"
)

page = st.sidebar.radio(
    "Navigation",
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

st.sidebar.info(
    "Database: Neon PostgreSQL"
)


# =====================================================
# 5. DATABASE CONNECTION CHECK
# =====================================================

try:

    engine = get_engine()

    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    database_connected = True

except Exception as e:

    database_connected = False

    st.error(
        "Database connection failed. "
        "Check your Streamlit Secrets and Neon database."
    )

    st.code(str(e))

if not database_connected:
    st.stop()


# =====================================================
# 6. DASHBOARD
# =====================================================

if page == "Dashboard":

    st.title("🏨 Hotel Booking Dashboard")

    st.write(
        "Monitor hotel properties, room inventory, "
        "customers, bookings and revenue."
    )

    try:

        hotels = load_data(
            "SELECT COUNT(*) AS total FROM hotels"
        )

        rooms = load_data(
            "SELECT COUNT(*) AS total FROM rooms"
        )

        customers = load_data(
            "SELECT COUNT(*) AS total FROM customers"
        )

        bookings = load_data(
            "SELECT COUNT(*) AS total FROM bookings"
        )

        revenue = load_data("""
            SELECT COALESCE(SUM(total_price), 0) AS total
            FROM bookings
            WHERE status IN (
                'confirmed',
                'checked_in',
                'checked_out'
            )
        """)

        total_hotels = int(hotels.iloc[0]["total"])
        total_rooms = int(rooms.iloc[0]["total"])
        total_customers = int(customers.iloc[0]["total"])
        total_bookings = int(bookings.iloc[0]["total"])
        total_revenue = float(revenue.iloc[0]["total"])

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Hotels", total_hotels)
        col2.metric("Total Rooms", total_rooms)
        col3.metric("Total Customers", total_customers)

        col4, col5 = st.columns(2)

        col4.metric("Total Bookings", total_bookings)

        col5.metric(
            "Booking Revenue",
            f"₹{total_revenue:,.2f}"
        )

        st.divider()

        st.subheader("Database Status")

        st.success(
            "Connected successfully to Neon PostgreSQL!"
        )

    except Exception as e:

        st.error(f"Dashboard error: {e}")


# =====================================================
# 7. HOTEL MANAGEMENT
# =====================================================

elif page == "Hotel Management":

    st.title("🏨 Hotel Management")

    st.write("View all registered hotel properties.")

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

        st.metric("Total Hotels", len(df))

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Hotels by City")

        city_data = df.groupby("city").size().reset_index(
            name="hotel_count"
        )

        fig = px.bar(
            city_data,
            x="city",
            y="hotel_count",
            title="Number of Hotels by City",
            text="hotel_count"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    except Exception as e:

        st.error(f"Hotel management error: {e}")


# =====================================================
# 8. ROOM MANAGEMENT
# =====================================================

elif page == "Room Management":

    st.title("🛏️ Room Management")

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

        city_filter = st.selectbox(
            "Filter by City",
            ["All Cities"] + sorted(
                df["city"].dropna().unique().tolist()
            )
        )

        if city_filter != "All Cities":

            df = df[df["city"] == city_filter]

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Room Types")

        room_types = df.groupby(
            "room_type"
        ).size().reset_index(
            name="total_rooms"
        )

        fig = px.pie(
            room_types,
            names="room_type",
            values="total_rooms",
            title="Room Type Distribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    except Exception as e:

        st.error(f"Room management error: {e}")


# =====================================================
# 9. CUSTOMER MANAGEMENT
# =====================================================

elif page == "Customer Management":

    st.title("👥 Customer Management")

    try:

        df = load_data("""
            SELECT
                customer_id,
                customer_name,
                email,
                phone
            FROM customers
            ORDER BY customer_id
        """)

        st.metric("Total Customers", len(df))

        search = st.text_input(
            "Search Customer by Name or Email"
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
            use_container_width=True,
            hide_index=True
        )

    except Exception as e:

        st.error(f"Customer management error: {e}")


# =====================================================
# 10. BOOKING MANAGEMENT
# =====================================================

elif page == "Booking Management":

    st.title("📅 Booking Management")

    try:

        df = load_data("""
            SELECT
                b.booking_id,
                h.hotel_name,
                h.city,
                r.room_number,
                r.room_type,
                c.customer_name,
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

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Bookings", len(df))

        col2.metric(
            "Confirmed",
            int((df["status"] == "confirmed").sum())
        )

        col3.metric(
            "Cancelled",
            int((df["status"] == "cancelled").sum())
        )

        status_filter = st.selectbox(
            "Filter Booking Status",
            [
                "All",
                "confirmed",
                "pending",
                "cancelled",
                "checked_in",
                "checked_out"
            ]
        )

        if status_filter != "All":

            df = df[df["status"] == status_filter]

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "This page currently displays existing bookings. "
            "Booking creation and cancellation will be added "
            "with transactional validation."
        )

    except Exception as e:

        st.error(f"Booking management error: {e}")


# =====================================================
# 11. DYNAMIC PRICING
# =====================================================

elif page == "Dynamic Pricing":

    st.title("💰 Dynamic Pricing Analyzer")

    st.write(
        "Explore room prices calculated using occupancy, "
        "booking demand and weekend adjustments."
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

            st.warning(
                "No dynamic pricing records found."
            )

        else:

            col1, col2 = st.columns(2)

            col1.metric(
                "Pricing Records",
                len(df)
            )

            average_price = df["dynamic_price"].mean()

            col2.metric(
                "Average Dynamic Price",
                f"₹{average_price:,.2f}"
            )

            selected_hotel = st.selectbox(
                "Select Hotel",
                ["All Hotels"] + sorted(
                    df["hotel_name"].dropna().unique().tolist()
                )
            )

            if selected_hotel != "All Hotels":

                df = df[
                    df["hotel_name"] == selected_hotel
                ]

            st.subheader("Dynamic Pricing Records")

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            st.subheader("Base Price vs Dynamic Price")

            if not df.empty:

                comparison = df.head(100)

                fig = px.scatter(
                    comparison,
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

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            st.info(
                "Prices are generated from synthetic project data, "
                "not live hotel market rates."
            )

    except Exception as e:

        st.error(f"Dynamic pricing error: {e}")


# =====================================================
# 12. ANALYTICS
# =====================================================

elif page == "Analytics":

    st.title("📊 Hotel Booking Analytics")

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

        st.subheader("Hotel Performance")

        st.dataframe(
            df,
            use_container_width=True,
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

        total_rooms = int(
            df["total_rooms"].sum()
        )

        cancellation_rate = (
            total_cancelled / total_bookings * 100
            if total_bookings > 0 else 0
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Bookings",
            total_bookings
        )

        col2.metric(
            "Total Revenue",
            f"₹{total_revenue:,.2f}"
        )

        col3.metric(
            "Cancelled Bookings",
            total_cancelled
        )

        col4.metric(
            "Cancellation Rate",
            f"{cancellation_rate:.2f}%"
        )

        st.divider()

        # Revenue Chart

        st.subheader("Top 10 Hotels by Revenue")

        top_hotels = df.nlargest(
            10,
            "total_revenue"
        )

        fig1 = px.bar(
            top_hotels,
            x="hotel_name",
            y="total_revenue",
            color="city",
            title="Hotel Revenue Comparison",
            labels={
                "hotel_name": "Hotel",
                "total_revenue": "Revenue (₹)"
            }
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

        # Booking Chart

        st.subheader("Bookings by Hotel")

        fig2 = px.bar(
            df.sort_values(
                "total_bookings",
                ascending=False
            ).head(10),
            x="hotel_name",
            y="total_bookings",
            color="city",
            title="Top 10 Hotels by Booking Count"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

        # Occupancy Chart

        st.subheader("Current Hotel Occupancy")

        fig3 = px.bar(
            df.sort_values(
                "current_occupancy_percentage",
                ascending=False
            ).head(10),
            x="hotel_name",
            y="current_occupancy_percentage",
            color="city",
            title="Current Occupancy Percentage",
            labels={
                "current_occupancy_percentage": "Occupancy (%)"
            }
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

        st.caption(
            f"Total rooms across all properties: {total_rooms}"
        )

    except Exception as e:

        st.error(f"Analytics error: {e}")


# =====================================================
# 13. FOOTER
# =====================================================

st.sidebar.divider()

st.sidebar.caption(
    "Hotel Multi-Property Booking & Dynamic Pricing Analyzer"
)

st.sidebar.caption(
    "Developed using Python, PostgreSQL and Streamlit"
)
