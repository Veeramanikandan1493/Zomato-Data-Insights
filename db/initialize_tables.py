import streamlit as st

from db.schema_manager import SchemaManager


def create_initial_tables():
    """
    Creates the initial set of tables using the current database connection stored in session state.
    This function relies on the DatabaseConnector (stored as st.session_state.db_connector)
    and uses SchemaManager to execute the table creation statements.
    """
    if "db_connector" not in st.session_state:
        st.error("Database not configured. Please go to 'Database Config' page.")
        return

    connection = st.session_state.db_connector.get_connection()
    schema_manager = SchemaManager(connection)

    # Customers Table Schema
    customers_schema = [
        {"name": "customer_id", "type": "INT", "is_primary": True, "auto_increment": True, "not_null": True},
        {"name": "name", "type": "VARCHAR(255)", "not_null": False},
        {"name": "email", "type": "VARCHAR(255)", "not_null": False},
        {"name": "phone", "type": "VARCHAR(255)", "not_null": False},
        {"name": "location", "type": "VARCHAR(255)", "not_null": False},
        {"name": "signup_date", "type": "DATE", "not_null": False},
        {"name": "is_premium", "type": "BOOLEAN", "not_null": False},
        {"name": "preferred_cuisine", "type": "VARCHAR(255)", "not_null": False},
        {"name": "total_orders", "type": "INT", "not_null": False},
        {"name": "average_rating", "type": "FLOAT", "not_null": False}
    ]

    # Restaurants Table Schema
    restaurants_schema = [
        {"name": "restaurant_id", "type": "INT", "is_primary": True, "auto_increment": True, "not_null": True},
        {"name": "name", "type": "VARCHAR(255)", "not_null": False},
        {"name": "cuisine_type", "type": "VARCHAR(255)", "not_null": False},
        {"name": "location", "type": "VARCHAR(255)", "not_null": False},
        {"name": "owner_name", "type": "VARCHAR(255)", "not_null": False},
        {"name": "average_delivery_time", "type": "INT", "not_null": False},
        {"name": "contact_number", "type": "VARCHAR(255)", "not_null": False},
        {"name": "rating", "type": "FLOAT", "not_null": False},
        {"name": "total_orders", "type": "INT", "not_null": False},
        {"name": "is_active", "type": "BOOLEAN", "not_null": False}
    ]

    # Orders Table Schema
    orders_schema = [
        {"name": "order_id", "type": "INT", "is_primary": True, "auto_increment": True, "not_null": True},
        {"name": "customer_id", "type": "INT", "foreign_key": "customers(customer_id)", "not_null": False},
        {"name": "restaurant_id", "type": "INT", "foreign_key": "restaurants(restaurant_id)", "not_null": False},
        {"name": "order_date", "type": "DATETIME", "not_null": False},
        {"name": "delivery_time", "type": "DATETIME", "not_null": False},
        {"name": "status", "type": "VARCHAR(255)", "not_null": False},
        {"name": "total_amount", "type": "FLOAT", "not_null": False},
        {"name": "payment_mode", "type": "VARCHAR(255)", "not_null": False},
        {"name": "discount_applied", "type": "FLOAT", "not_null": False},
        {"name": "feedback_rating", "type": "FLOAT", "not_null": False}
    ]

    # Deliveries Table Schema
    deliveries_schema = [
        {"name": "delivery_id", "type": "INT", "is_primary": True, "auto_increment": True, "not_null": True},
        {"name": "order_id", "type": "INT", "foreign_key": "orders(order_id)", "not_null": False},
        {"name": "delivery_person_id", "type": "INT", "foreign_key": "delivery_persons(delivery_person_id)",
         "not_null": False},
        {"name": "delivery_status", "type": "VARCHAR(255)", "not_null": False},
        {"name": "distance", "type": "FLOAT", "not_null": False},
        {"name": "delivery_time", "type": "INT", "not_null": False},
        {"name": "estimated_time", "type": "INT", "not_null": False},
        {"name": "delivery_fee", "type": "FLOAT", "not_null": False},
        {"name": "vehicle_type", "type": "VARCHAR(255)", "not_null": False}
    ]

    # Delivery Persons Table Schema
    delivery_persons_schema = [
        {"name": "delivery_person_id", "type": "INT", "is_primary": True, "auto_increment": True, "not_null": True},
        {"name": "name", "type": "VARCHAR(255)", "not_null": False},
        {"name": "contact_number", "type": "VARCHAR(255)", "not_null": False},
        {"name": "vehicle_type", "type": "VARCHAR(255)", "not_null": False},
        {"name": "total_deliveries", "type": "INT", "not_null": False},
        {"name": "average_rating", "type": "FLOAT", "not_null": False},
        {"name": "location", "type": "VARCHAR(255)", "not_null": False}
    ]

    try:
        schema_manager.create_table("delivery_persons", delivery_persons_schema)
        schema_manager.create_table("customers", customers_schema)
        schema_manager.create_table("restaurants", restaurants_schema)
        schema_manager.create_table("orders", orders_schema)
        schema_manager.create_table("deliveries", deliveries_schema)
        st.success("Initial tables created successfully.")
    except Exception as e:
        st.error(f"Error creating initial tables: {e}")
