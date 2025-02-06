import json

import pandas as pd
import streamlit as st

from crud.crud_handler import CRUDHandler
from db.schema_manager import SchemaManager


def data_operations_page(schema_manager, connection, operation):
    """Display content for table CRUD operations."""
    st.subheader("Data Operations")
    tables = schema_manager.list_tables()
    table_name = st.selectbox("Table name", options=tables)
    if operation == "Read Records":
        st.header("View Records")
        per_page = st.number_input("Records per page", min_value=1, value=10)
        page = st.number_input("Page number", min_value=1, value=1)
        if st.button("Load Records"):
            try:
                crud_handler = CRUDHandler(connection, table_name)
                offset = (page - 1) * per_page
                records, columns = crud_handler.read_records(limit=per_page, offset=offset)
                if records:
                    df = pd.DataFrame(records, columns=columns)
                    st.dataframe(df)
                else:
                    st.info("No records found.")
            except Exception as e:
                st.error(f"Error loading records: {e}")

    elif operation == "Create Record":
        st.header("Create Record")
        st.markdown("Enter the new record as JSON. For example:")
        st.code('{"customer_id": 101, "name": "John Doe", "email": "john@example.com", "phone": "1234567890", "location": "City", "signup_date": "2023-01-01", "is_premium": false, "preferred_cuisine": "Italian", "total_orders": 0, "average_rating": 0.0}')
        record_data = st.text_area("Record Data (JSON)")
        if st.button("Create Record"):
            try:
                data_dict = json.loads(record_data)
                crud_handler = CRUDHandler(connection, table_name)
                rows_affected = crud_handler.create_record(data_dict)
                if rows_affected:
                    st.success("Record created successfully.")
                else:
                    st.warning("No record was created.")
            except Exception as e:
                st.error(f"Error creating record: {e}")

    elif operation == "Update Record":
        st.header("Update Record")
        record_id = st.text_input("Enter the record identifier (value of the ID column)")
        update_data = st.text_area("Update Data as JSON (e.g., {\"name\": \"Jane Doe\"})")
        primary_keys = schema_manager.get_primary_keys(table_name)
        id_column = st.text_input("Identifier Column Name", value=primary_keys[0] if len(primary_keys) else "")
        if st.button("Update Record"):
            try:
                data_dict = json.loads(update_data)
                crud_handler = CRUDHandler(connection, table_name)
                rows_affected = crud_handler.update_record(record_id, data_dict, id_column=id_column)
                if rows_affected:
                    st.success("Record updated successfully.")
                else:
                    st.warning("No record was updated. Please check the identifier.")
            except Exception as e:
                st.error(f"Error updating record: {e}")

    elif operation == "Delete Record":
        st.header("Delete Record")
        record_id = st.text_input("Enter the record identifier to delete")
        primary_keys = schema_manager.get_primary_keys(table_name)
        id_column = st.text_input("Identifier Column Name", value=primary_keys[0] if len(primary_keys) else "")
        if st.button("Delete Record"):
            try:
                crud_handler = CRUDHandler(connection, table_name)
                rows_affected = crud_handler.delete_record(record_id, id_column=id_column)
                if rows_affected:
                    st.success("Record deleted successfully.")
                else:
                    st.warning("No record was deleted. Please check the identifier.")
            except Exception as e:
                st.error(f"Error deleting record: {e}")

def table_operations_page(schema_manager: SchemaManager, operation):
    """Display content for table CRUD operations."""
    st.subheader("Table Operations")
    if operation == "Create Table":
        st.header("Create Table")
        table_name = st.text_input("New Table Name", key="create_table_name")
        columns_def = st.text_area("Columns Definition (e.g., id INT PRIMARY KEY, name VARCHAR(100))", key="create_columns_def")
        if st.button("Create Table", key="create_table_btn"):
            if table_name and columns_def:
                try:
                    schema_manager.create_table(table_name, columns_def)
                    st.success(f"Table '{table_name}' created successfully.")
                except Exception as e:
                    st.error(f"Error creating table: {e}")
            else:
                st.warning("Please provide both table name and column definitions.")
    else:
        tables = schema_manager.list_tables()
        table_name = st.selectbox("Table name", options=tables)

        if operation == "Add Column":
            st.header("Add Column")
            col_def = st.text_input("New Column Definition (e.g., VARCHAR(255))", key="add_column_def")
            if st.button("Add Column", key="add_column_btn"):
                if table_name and col_def:
                    try:
                        schema_manager.add_column(table_name, col_def)
                        st.success(f"Column added to '{table_name}'.")
                    except Exception as e:
                        st.error(f"Error adding column: {e}")
                else:
                    st.warning("Please provide both table name and column definition.")

        elif operation == "Modify Column":
            st.header("Modify Column")
            if table_name:
                columns = schema_manager.get_table_columns(table_name)
                column_names = [col[0] for col in columns]
                selected_column = st.selectbox("Select Column to Modify", options=column_names, key="mod_select")
                selected_col_tuple = next((col for col in columns if col[0] == selected_column), None)
                default_definition = SchemaManager.format_column_definition(selected_col_tuple) if selected_col_tuple else ""
                default_definition = default_definition.replace(f"{selected_column} ", "")
                new_def = st.text_input("New Column Definition", value=default_definition, key="mod_new_def")
                if st.button("Modify Column", key="mod_column_btn"):
                    if table_name and selected_column and new_def:
                        try:
                            schema_manager.modify_column(table_name, selected_column, new_def)
                            st.success(f"Column '{selected_column}' in table '{table_name}' modified successfully.")
                        except Exception as e:
                            st.error(f"Error modifying column: {e}")
                    else:
                        st.warning("Please provide table name, column selection, and new definition.")
            else:
                st.warning("Please enter a table name first.")

        elif operation == "Drop Column":
            st.header("Drop Column")
            if table_name:
                columns = schema_manager.get_table_columns(table_name)
                drop_col = st.selectbox("Column Name to Drop", options=[c[0] for c in columns])
                if st.button("Drop Column", key="drop_column_btn"):
                    if table_name and drop_col:
                        try:
                            schema_manager.drop_column(table_name, drop_col)
                            st.success(f"Column '{drop_col}' dropped from table '{table_name}' successfully.")
                        except Exception as e:
                            st.error(f"Error dropping column: {e}")
                    else:
                        st.warning("Please provide both table name and column name.")

        elif operation == "Rename Table":
            st.header("Rename Table")
            if table_name:
                new_table_name = st.text_input("Table's new name", key="new_table_name")
                if st.button("Rename Table", key="drop_column_btn"):
                    if table_name and new_table_name:
                        try:
                            schema_manager.rename_table(table_name, new_table_name)
                            st.success(f"Table '{table_name}' renamed to table '{new_table_name}' successfully.")
                        except Exception as e:
                            st.error(f"Error renaming column: {e}")
                    else:
                        st.warning("Please provide both table name and new table name.")

        elif operation == "Truncate Table":
            if st.button("Truncate Table", key="table_name_btn"):
                if table_name:
                    try:
                        schema_manager.truncate_table(table_name)
                        st.success(f"Table '{table_name}' truncated successfully.")
                    except Exception as e:
                        st.error(f"Error truncating table: {e}")
                else:
                    st.warning("Please provide a table name to truncate.")

        elif operation == "Drop Table":
            if st.button("Drop Table", key="table_name_btn"):
                if table_name:
                    try:
                        schema_manager.drop_table(table_name)
                        st.success(f"Table '{table_name}' dropped successfully.")
                    except Exception as e:
                        st.error(f"Error dropping table: {e}")
                else:
                    st.warning("Please provide a table name to drop.")

def app():
    st.title("CRUD Operations")
    if "db_connector" not in st.session_state:
        st.error("Database not configured. Please use the 'Database Configuration' in the side menu.")
        return

    connection = st.session_state.db_connector.get_connection()
    schema_manager = SchemaManager(connection)

    operations = [
        "Data: Read Records",
        "Data: Create Record",
        "Data: Update Record",
        "Data: Delete Record",
        "Table: Create Table",
        "Table: Add Column",
        "Table: Modify Column",
        "Table: Drop Column",
        "Table: Rename Table",
        "Table: Truncate Table",
        "Table: Drop Table"
    ]

    st.sidebar.header("CRUD Operations")
    selected_operation = st.sidebar.radio("Select Operation", operations, key="combined_radio")

    if selected_operation.startswith("Data:"):
        data_operations_page(schema_manager, connection, selected_operation.replace("Data: ",""))
    elif selected_operation.startswith("Table:"):
        table_operations_page(schema_manager, selected_operation.replace("Table: ",""))
