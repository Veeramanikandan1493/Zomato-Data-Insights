import logging

import pymysql


class SchemaManager:
    """
    Handles dynamic schema operations including retrieving, creating, modifying, and deleting tables and columns.
    """

    def __init__(self, connection):
        """
        Initializes the SchemaManager with an active MySQL database connection.

        Args:
            connection (pymysql.connections.Connection): Active connection to the MySQL database.
        """
        self.connection = connection
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def list_tables(self):
        """
        Retrieves a list of all tables in the current database.

        Returns:
            list: A list containing the names of the tables.
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SHOW TABLES;")
                result = cursor.fetchall()
                tables = [row[0] for row in result]
                self.logger.debug("Retrieved tables: %s", tables)
                return tables
        except pymysql.MySQLError as e:
            self.logger.error("Error listing tables: %s", e)
            raise e

    def get_table_columns(self, table_name):
        """
        Retrieves details about the columns of a specific table.

        Args:
            table_name (str): The name of the table.

        Returns:
            list: A list of tuples with column details.
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"DESCRIBE {table_name};")
                columns = cursor.fetchall()
                # Convert tuple results to list of dictionaries
                column_names = [desc[0] for desc in cursor.description]  # Get column headers
                column_dicts = [dict(zip(column_names, col, strict=False)) for col in columns]
                return column_dicts  # Now a list of dictionaries
        except pymysql.MySQLError as e:
            self.logger.error("Error retrieving columns for table '%s': %s", table_name, e)
            raise e
        return []

    def get_primary_keys(self, table_name):
        """
        Retrieves the primary key column(s) for the specified table.

        Args:
            table_name (str): The name of the table.

        Returns:
            list: A list of primary key column names.
        """
        try:
            columns = self.get_table_columns(table_name)
            primary_keys = [col["Field"] for col in columns if col["Key"].upper() == "PRI"]
            self.logger.debug("Primary keys for table '%s': %s", table_name, primary_keys)
            return primary_keys
        except Exception as e:
            self.logger.error("Error retrieving primary keys for table '%s': %s", table_name, e)
            raise e

    @staticmethod
    def format_column_definition(col):
        """
        Given a tuple representing column details from DESCRIBE in the order:
        (Field, Type, Null, Key, Default, Extra),
        returns a formatted string:
        """
        keys = ["Field", "Type", "Null", "Key", "Default", "Extra"]
        col_dict = dict(zip(keys, col, strict=False))

        field = col_dict.get("Field")
        type_ = col_dict.get("Type")
        null = col_dict.get("Null")
        key = col_dict.get("Key")
        default = col_dict.get("Default")
        extra = col_dict.get("Extra")

        definition = f"{field} {type_.upper()}"
        if key and key.upper() == "PRI":
            definition += " PRIMARY KEY"
        if extra and extra.lower() == "auto_increment":
            definition += " AUTO_INCREMENT"
        if (null and null.upper() == "YES") and (default is None or default == ""):
            definition += " DEFAULT NULL"

        return definition

    def create_table(self, table_name, columns):
        """
        Creates a new table with the given columns definition.

        Args:
            table_name (str): The name of the new table.
            columns (list): List of dictionaries containing column definitions.
        """
        try:
            with self.connection.cursor() as cursor:
                column_definitions = []
                primary_keys = []

                for col in columns:
                    col_def = f"{col['name']} {col['type']}"

                    if col.get("auto_increment"):
                        col_def += " AUTO_INCREMENT"

                    if col.get("not_null"):
                        col_def += " NOT NULL"

                    if col.get("is_primary"):
                        primary_keys.append(col["name"])

                    column_definitions.append(col_def)

                # Add primary key constraint
                if primary_keys:
                    column_definitions.append(f"PRIMARY KEY ({', '.join(list(set(primary_keys)))})")

                sql = f"CREATE TABLE {table_name} ({', '.join(column_definitions)});"
                cursor.execute(sql)
                self.connection.commit()
                self.logger.info("Table '%s' created successfully.", table_name)
        except pymysql.MySQLError as e:
            self.logger.error("Error creating table '%s': %s", table_name, e)
            raise e

    def drop_table(self, table_name):
        """
        Drops an existing table from the database.

        Args:
            table_name (str): The name of the table to drop.
        """
        try:
            with self.connection.cursor() as cursor:
                sql = f"DROP TABLE IF EXISTS {table_name};"
                self.logger.debug("Executing SQL: %s", sql)
                cursor.execute(sql)
                self.connection.commit()
                self.logger.info("Table '%s' dropped successfully.", table_name)
        except pymysql.MySQLError as e:
            self.logger.error("Error dropping table '%s': %s", table_name, e)
            raise e

    def add_column(self, table_name, columns):
        """
        Adds multiple new columns to an existing table.

        Args:
            table_name (str): The name of the table.
            columns (list): List of dictionaries containing column details.

        Returns:
            bool: True if columns added successfully, False otherwise.
        """
        try:
            with self.connection.cursor() as cursor:
                alter_statements = []

                for col in columns:
                    col_def = f"{col['name']} {col['type']}"

                    if col.get("auto_increment"):
                        col_def += " AUTO_INCREMENT"

                    if col.get("not_null"):
                        col_def += " NOT NULL"

                    alter_statements.append(f"ADD COLUMN {col_def}")

                if alter_statements:
                    sql = f"ALTER TABLE {table_name} {', '.join(alter_statements)};"
                    cursor.execute(sql)
                    self.connection.commit()
        except pymysql.MySQLError as e:
            self.logger.error("Error adding column to table '%s': %s", table_name, e)
            raise e

    def modify_column(self, table_name, modified_columns):
        """
        Modifies multiple columns in an existing table.

        Args:
            table_name (str): The name of the table.
            modified_columns (list): List of dictionaries containing updated column details.

        Returns:
            bool: True if columns modified successfully, False otherwise.
        """
        try:
            with self.connection.cursor() as cursor:
                alter_statements = []

                for col in modified_columns:
                    alter_def = f"{col['old_name']} {col['new_name']} {col['type']}"
                    if col.get("not_null"):
                        alter_def += " NOT NULL"
                    alter_statements.append(f"CHANGE COLUMN {alter_def}")

                if alter_statements:
                    sql = f"ALTER TABLE {table_name} {', '.join(alter_statements)};"
                    cursor.execute(sql)
                    self.connection.commit()
        except pymysql.MySQLError as e:
            self.logger.error("Error modifying columns in table '%s': %s", table_name, e)
            raise e

    def drop_column(self, table_name, column_name):
        """
        Drops a column from an existing table.

        Args:
            table_name (str): The name of the table.
            column_name (str): The name of the column to drop.
        """
        try:
            with self.connection.cursor() as cursor:
                sql = f"ALTER TABLE {table_name} DROP COLUMN {column_name};"
                self.logger.debug("Executing SQL: %s", sql)
                cursor.execute(sql)
                self.connection.commit()
                self.logger.info("Dropped column '%s' from table '%s'.", column_name, table_name)
        except pymysql.MySQLError as e:
            self.logger.error("Error dropping column '%s' from table '%s': %s", column_name, table_name, e)
            raise e

    def rename_table(self, old_table_name, new_table_name):
        """
        Renames an existing table.

        Args:
            old_table_name (str): The current table name.
            new_table_name (str): The new table name.
        """
        try:
            with self.connection.cursor() as cursor:
                sql = f"RENAME TABLE {old_table_name} TO {new_table_name};"
                self.logger.debug("Executing SQL: %s", sql)
                cursor.execute(sql)
                self.connection.commit()
                self.logger.info("Renamed table from '%s' to '%s'.", old_table_name, new_table_name)
        except pymysql.MySQLError as e:
            self.logger.error("Error renaming table '%s' to '%s': %s", old_table_name, new_table_name, e)
            raise e

    def truncate_table(self, table_name):
        """
        Truncates (empties) an existing table.

        Args:
            table_name (str): The name of the table to truncate.
        """
        try:
            with self.connection.cursor() as cursor:
                sql = f"TRUNCATE TABLE {table_name};"
                self.logger.debug("Executing SQL: %s", sql)
                cursor.execute(sql)
                self.connection.commit()
                self.logger.info("Table '%s' truncated successfully.", table_name)
        except pymysql.MySQLError as e:
            self.logger.error("Error truncating table '%s': %s", table_name, e)
            raise e
