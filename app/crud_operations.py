import json
from ast import literal_eval
from decimal import Decimal

import pandas as pd
import streamlit as st

from app.insights import convert_to_title
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
        st.header("Create a New Record")

        # Toggle between JSON and Form input
        input_mode = st.radio("Input Mode", ["Form Input", "JSON Input"], horizontal=True)

        if input_mode == "Form Input":
            columns = schema_manager.get_table_columns(table_name)
            column_data = {}

            for col in columns:
                col_name = col['Field']
                col_type = col['Type']
                is_nullable = col['Null'] == 'NO'
                col_label = convert_to_title(f"{col_name} *" if is_nullable else col_name)

                # Exclude primary key
                if col['Key'] == 'PRI':
                    continue

                # Determine input type
                if "tinyint" in col_type or "bool" in col_type or "enum" in col_type:
                    column_data[col_name] = st.radio(col_label, ["Yes", "No"])
                    column_data[col_name] = 1 if column_data[col_name] == 'Yes' or column_data[col_name] == '1' else 0
                elif "int" in col_type or "decimal" in col_type or "float" in col_type:
                    column_data[col_name] = st.number_input(col_label, value=0)
                else:
                    column_data[col_name] = st.text_input(col_label)

            if st.button("Create Record"):
                try:
                    crud_handler = CRUDHandler(connection, table_name)
                    crud_handler.create_record(column_data)
                    st.success("Record created successfully!")
                except Exception as e:
                    st.error(f"Error creating record: {e}")

        else:  # JSON Input Mode
            st.markdown("Enter the new record as JSON. For example:")
            st.code(
                '{"name": "John Doe", "email": "john@example.com", "phone": "1234567890", "location": "City", "signup_date": "2023-01-01", "is_premium": false, "preferred_cuisine": "Italian", "total_orders": 0, "average_rating": 0.0}')
            json_input = st.text_area("Enter JSON data", value="{}")
            if st.button("Create Record"):
                try:
                    record_data = literal_eval(json_input)  # Convert string to dictionary
                    crud_handler = CRUDHandler(connection, table_name)
                    crud_handler.create_record(record_data)
                    st.success("Record created successfully!")
                except Exception as e:
                    st.error(f"Error creating record: {e}")

    elif operation == "Update Record":
        st.header("Update an Existing Record")

        id_columns = schema_manager.get_primary_keys(table_name)
        if not id_columns:
            st.error("No primary key found for this table. Updates require a primary key.")
            return

        id_column = id_columns[0]

        primary_key_value = st.text_input(f"Enter the record identifier ({id_column}) to be updated")
        if not primary_key_value:
            return

        # Fetch existing record
        crud_handler = CRUDHandler(connection, table_name)
        record = crud_handler.read_record(primary_key_value, id_column)
        if not record:
            st.error("Record not found!")
            return

        # Toggle between JSON and Form input
        input_mode = st.radio("Input Mode", ["Form Input", "JSON Input"], horizontal=True)

        updated_data = {}

        if input_mode == "Form Input":
            columns = schema_manager.get_table_columns(table_name)

            for col in columns:
                col_name = col['Field']
                col_type = col['Type']
                is_nullable = col['Null'] == 'NO'
                col_label = f"{col_name} *" if is_nullable else col_name

                # Exclude primary key
                if col['Key'] == 'PRI':
                    continue

                # Display existing values in the form
                existing_value = record.get(col_name, "")

                # Inside data_operations_page()
                if isinstance(existing_value, Decimal):
                    existing_value = float(existing_value)  # Convert Decimal to float

                if "tinyint" in col_type or "bool" in col_type or "enum" in col_type:
                    new_value = st.radio(col_label, ["Yes", "No"], index=0 if existing_value == "Yes" else 1)
                elif "int" in col_type or "decimal" in col_type or "float" in col_type:
                    new_value = st.number_input(col_label, value=existing_value if existing_value is not None else 0.0)
                else:
                    new_value = st.text_input(col_label, value=str(existing_value))

                # Add only changed values
                if str(new_value) != str(existing_value):
                    updated_data[col_name] = new_value
                    if "tinyint" in col_type or "bool" in col_type or "enum" in col_type:
                        updated_data[col_name] = 1 if new_value == 'Yes' or new_value == '1' else 0

        else:  # JSON Input Mode
            json_input = st.text_area("Enter JSON data", value=json.dumps(record, default=str, indent=2))
            try:
                updated_data = literal_eval(json_input)  # Convert string to dictionary
            except:
                st.error("Invalid JSON format.")

        if st.button("Update Record"):
            if not updated_data:
                st.warning("No changes detected!")
            else:
                crud_handler = CRUDHandler(connection, table_name)
                rows_affected = crud_handler.update_record(primary_key_value, updated_data, id_column=id_column)
                if rows_affected:
                    st.success("Record updated successfully.")
                else:
                    st.warning("No record was updated. Please check the identifier.")
    elif operation == "Delete Record":
        st.header("Delete Record")
        primary_keys = schema_manager.get_primary_keys(table_name)
        id_column = primary_keys[0] if len(primary_keys) else ''
        record_id = st.text_input(f"Enter the record identifier ({id_column}) to delete")
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
    # Input Mode Toggle
    if operation == "Create Table":
        st.header("Create a New Table")

        table_name = st.text_input("Table Name")

        input_mode = st.radio("Input Mode", ["Form Input", "JSON Input"], horizontal=True)

        if input_mode == "Form Input":
            st.subheader("Define Columns")

            if "create_table_columns" not in st.session_state:
                st.session_state.create_table_columns = [
                    {"name": "", "type": "VARCHAR(255)", "is_primary": False, "auto_increment": False,
                     "not_null": False}]
                st.rerun()

            column_data = []
            for idx, col in enumerate(st.session_state.create_table_columns):
                col1, col2, col3, col4, col5 = st.columns(5)

                col["name"] = col1.text_input(f"Column Name {idx + 1}", key=f"col_name_{idx}")
                col["type"] = col2.selectbox(f"Type {idx + 1}", ["INT", "VARCHAR(255)", "TEXT", "DATE", "BOOLEAN"],
                                             key=f"col_type_{idx}")
                col["is_primary"] = col3.checkbox("Primary Key", key=f"pk_{idx}")
                col["auto_increment"] = col4.checkbox("Auto Increment", key=f"ai_{idx}")
                col["not_null"] = col5.checkbox("Not Null", key=f"nn_{idx}")

                column_data.append(col)

            # Add/Delete Rows Dynamically
            if st.button("➕ Add New Column"):
                st.session_state.create_table_columns.append(
                    {"name": "", "type": "VARCHAR(255)", "is_primary": False, "auto_increment": False,
                     "not_null": False})
                st.rerun()
            if len(st.session_state.create_table_columns) > 1 and st.button("➖ Remove Last Column"):
                st.session_state.create_table_columns.pop()
                st.rerun()

            if st.button("Create Table"):
                if table_name and column_data:
                    schema_manager.create_table(table_name, column_data)
                    st.success(f"Table '{table_name}' created successfully!")

        else:  # JSON Input Mode
            json_input = st.text_area("Enter JSON data", value=json.dumps({"table_name": "", "columns": []}, indent=2))
            if st.button("Create Table from JSON"):
                try:
                    table_data = json.loads(json_input)
                    schema_manager.create_table(table_data["table_name"], json.loads(table_data["columns"]))
                    st.success(f"Table '{table_data['table_name']}' created successfully!")
                except Exception as e:
                    st.error(f"Invalid JSON format: {e}")

    else:
        if operation == "Add Column":
            tables = schema_manager.list_tables()
            table_name = st.selectbox("Table name", options=tables)

            st.header("Add Column to Existing Table")

            input_mode = st.radio("Input Mode", ["Form Input", "JSON Input"], horizontal=True)

            if input_mode == "Form Input":
                st.subheader("Define New Columns")

                if "add_columns" not in st.session_state:
                    st.session_state.add_columns = [
                        {"name": "id", "type": "INT", "is_primary": False, "auto_increment": False,
                         "not_null": False}]
                    st.rerun()

                new_columns = []
                for idx, col in enumerate(st.session_state.add_columns):
                    # col1, col2, col3, col4, col5 = st.columns(5)
                    col1, col2, col3 = st.columns(3)

                    col["name"] = col1.text_input(f"Column Name {idx + 1}", key=f"add_col_name_{idx}")
                    col["type"] = col2.selectbox(f"Type {idx + 1}", ["INT", "VARCHAR(255)", "TEXT", "DATE", "BOOLEAN"],
                                                 key=f"add_col_type_{idx}")
                    # col["is_primary"] = col3.checkbox("Primary Key", key=f"add_pk_{idx}")
                    # col["auto_increment"] = col4.checkbox("Auto Increment", key=f"add_ai_{idx}")
                    col["not_null"] = col3.checkbox("Not Null", key=f"add_nn_{idx}")

                    new_columns.append(col)

                # Add/Delete Rows Dynamically
                if st.button("➕ Add New Column"):
                    st.session_state.add_columns.append(
                        {"name": "", "type": "VARCHAR(255)", "is_primary": False, "auto_increment": False,
                         "not_null": False})
                    st.rerun()
                if len(st.session_state.add_columns) > 1 and st.button("➖ Remove Last Column"):
                    st.session_state.add_columns.pop()
                    st.rerun()

                if st.button("Add Columns from Form"):
                    try:
                        schema_manager.add_column(table_name, new_columns)
                        st.success(f"Columns added successfully to '{table_name}'!")
                    except Exception as e:
                        st.error(f"Invalid JSON format: {e}")

            else:  # JSON Input Mode
                json_input = st.text_area("Enter JSON data",
                                          value=json.dumps({"table_name": "", "columns": []}, indent=2))
                if st.button("Add Columns from JSON"):
                    try:
                        column_data = json.loads(json_input)
                        schema_manager.add_column(column_data["table_name"], json.loads(column_data["columns"]))
                        st.success(f"Columns added successfully to '{column_data['table_name']}'!")
                    except Exception as e:
                        st.error(f"Invalid JSON format: {e}")

        elif operation == "Modify Column":
            tables = schema_manager.list_tables()
            # Detect Table Change
            previous_table = st.session_state.get("selected_table", None)
            table_name = st.selectbox("Select Table", tables,
                                      index=0 if previous_table is None else tables.index(previous_table))

            if "selected_table" not in st.session_state or previous_table != table_name:
                st.session_state.selected_table = table_name
                st.session_state.modify_columns = []  # Reset columns when table changes
                st.rerun()  #

            st.header("Modify Columns in Existing Table")

            input_mode = st.radio("Input Mode", ["Form Input", "JSON Input"], horizontal=True)

            updated_columns = []
            if input_mode == "Form Input":
                # Fetch columns from the selected table
                columns = schema_manager.get_table_columns(table_name)

                if not columns:
                    st.warning("No columns found in this table.")
                    return

                # Initialize modify_columns if not set
                if "modify_columns" not in st.session_state or not st.session_state.modify_columns:
                    st.session_state.modify_columns = [
                        {**col, "new_name": col["Field"], "new_type": col["Type"], "not_null": col["Null"] == "NO"}
                        for col in columns
                    ]

                updated_columns = []
                for idx, col in enumerate(st.session_state.modify_columns):
                    col1, col2, col3 = st.columns(3)

                    if "Field" not in col.keys():
                        col["Field"] = ""

                    if "Type" not in col.keys():
                        col["Type"] = ""

                    if "Null" not in col.keys():
                        col["Null"] = False

                    if "Key" not in col.keys():
                        col["Key"] = ""

                    old_col_name = col["Field"]
                    new_col_name = col1.text_input(f"New Column Name ({old_col_name})", value=col["new_name"], key=f"mod_col_name_{idx}")
                    new_col_type = col2.selectbox(f"New Type ({old_col_name})", ["INT", "VARCHAR(255)", "TEXT", "DATE", "BOOLEAN"], index=0 if "int" in col["Type"] else 1, key=f"mod_col_type_{idx}")
                    not_null = col3.checkbox("Not Null", value=col["not_null"], key=f"mod_nn_{idx}")

                    # Only update if there are changes
                    if new_col_name != col["Field"] or new_col_type != col["Type"] or not_null != (col["Null"] == "NO"):
                        if col["Key"] != "PRI":
                            updated_columns.append({
                                "old_name": col["Field"],
                                "new_name": new_col_name,
                                "type": new_col_type,
                                "not_null": not_null
                            })

                # Add or Remove Columns Dynamically
                col1, col2 = st.columns(2)
                if col1.button("➕ Add New Column"):
                    st.session_state.modify_columns.append(
                        {"new_name": "", "new_type": "VARCHAR(255)", "not_null": False,
                         "Field": "", "Type": "VARCHAR(255)", "Null": False, "Key": ""})
                    st.rerun()

                # **Remove only non-empty column entries**
                non_empty_columns = [col for col in st.session_state.modify_columns if
                                     col["Field"] == ""]
                if len(non_empty_columns) > 0 and col2.button("➖ Remove Last Column"):
                    st.session_state.modify_columns.pop()
                    st.rerun()

                if st.button("Modify Columns from Form") and updated_columns:
                    schema_manager.modify_column(table_name, updated_columns)
                    st.success(f"Modified {len(updated_columns)} columns in '{table_name}' successfully!")
                    st.session_state.selected_table = table_name
                    st.session_state.modify_columns = []  # Reset columns when table changes
            # JSON Input Mode
            elif input_mode == "JSON Input":
                json_input = st.text_area("Enter JSON data", value=json.dumps({"table_name": table_name, "columns": updated_columns}, indent=2))
                if st.button("Modify Columns from JSON"):
                    try:
                        modified_data = json.loads(json_input)
                        schema_manager.modify_column(modified_data["table_name"], modified_data["columns"])
                        st.success(f"Modified columns in '{modified_data['table_name']}' successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Invalid JSON format: {e}")

        elif operation == "Drop Column":
            tables = schema_manager.list_tables()
            table_name = st.selectbox("Table name", options=tables)

            st.header("Drop Column")
            if table_name:
                columns = schema_manager.get_table_columns(table_name)
                drop_col = st.selectbox("Column Name to Drop", options=[c["Field"] for c in columns])
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
            tables = schema_manager.list_tables()
            table_name = st.selectbox("Table name", options=tables)

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
            tables = schema_manager.list_tables()
            table_name = st.selectbox("Table name", options=tables)

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
            tables = schema_manager.list_tables()
            table_name = st.selectbox("Table name", options=tables)

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
