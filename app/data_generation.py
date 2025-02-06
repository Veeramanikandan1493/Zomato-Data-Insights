import streamlit as st

from data.data_generator import DataGenerator
from db.initialize_tables import create_initial_tables
from db.schema_manager import SchemaManager


def app():
    st.title("Data Generation & Ingestion")
    if "db_connector" not in st.session_state:
        st.error("Database not configured. Please use the 'Database Configuration' in the side menu.")
        return

    connection = st.session_state.db_connector.get_connection()
    schema_manager = SchemaManager(connection)

    tables = schema_manager.list_tables()

    st.header("Initialize Tables")
    st.markdown("Click the button below to create the initial set of tables required for the application.")
    if st.button("Create Initial Tables", disabled=True if len(tables) > 0 else False):
        try:
            create_initial_tables()
        except Exception as e:
            st.error(f"Error initializing tables: {e}")
    if len(tables):
        st.markdown("Tables already initialized")

    st.markdown("---")

    record_count = st.number_input("Records per table", min_value=1, value=100)
    if st.button("Generate and Insert Data"):
        try:
            connection = st.session_state.db_connector.get_connection()
            generator = DataGenerator(record_count=record_count)
            generator.insert_data(connection)
            st.success("Data generated and inserted successfully!")
        except Exception as e:
            st.error(f"Error generating data: {e}")
