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

    customers_columns = """
        customer_id INT PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(255),
        email VARCHAR(255),
        phone VARCHAR(50),
        location VARCHAR(255),
        signup_date DATE,
        is_premium BOOLEAN,
        preferred_cuisine VARCHAR(100),
        total_orders INT,
        average_rating DECIMAL(3,2)
    """
    restaurants_columns = """
        restaurant_id INT PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(255),
        cuisine_type VARCHAR(100),
        location VARCHAR(255),
        owner_name VARCHAR(255),
        average_delivery_time INT,
        contact_number VARCHAR(50),
        rating DECIMAL(3,2),
        total_orders INT,
        is_active BOOLEAN
    """
    orders_columns = """
        order_id INT PRIMARY KEY AUTO_INCREMENT,
        customer_id INT,
        restaurant_id INT,
        order_date DATETIME,
        delivery_time DATETIME,
        status VARCHAR(50),
        total_amount DECIMAL(10,2),
        payment_mode VARCHAR(50),
        discount_applied DECIMAL(10,2),
        feedback_rating DECIMAL(3,2),
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id)
    """
    deliveries_columns = """
        delivery_id INT PRIMARY KEY AUTO_INCREMENT,
        order_id INT,
        delivery_person_id INT,
        delivery_status VARCHAR(50),
        distance DECIMAL(5,2),
        delivery_time INT,
        estimated_time INT,
        delivery_fee DECIMAL(5,2),
        vehicle_type VARCHAR(50),
        FOREIGN KEY (order_id) REFERENCES orders(order_id)
    """
    delivery_persons_columns = """
        delivery_person_id INT PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(255),
        contact_number VARCHAR(50),
        vehicle_type VARCHAR(50),
        total_deliveries INT,
        average_rating DECIMAL(3,2),
        location VARCHAR(255)
    """

    try:
        schema_manager.create_table("customers", customers_columns)
        schema_manager.create_table("restaurants", restaurants_columns)
        schema_manager.create_table("orders", orders_columns)
        schema_manager.create_table("deliveries", deliveries_columns)
        schema_manager.create_table("delivery_persons", delivery_persons_columns)
        st.success("Initial tables created successfully.")
    except Exception as e:
        st.error(f"Error creating initial tables: {e}")
