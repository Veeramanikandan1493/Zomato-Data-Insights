import logging

import pymysql


class CRUDHandler:
    """
    A generic CRUD handler for performing Create, Read, Update, and Delete operations
    on any given table in the MySQL database.
    """

    def __init__(self, connection, table_name):
        """
        Initializes the CRUDHandler with an active MySQL connection and the target table name.

        Args:
            connection (pymysql.connections.Connection): Active MySQL database connection.
            table_name (str): Name of the table on which to perform CRUD operations.
        """
        self.connection = connection
        self.table_name = table_name
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def create_record(self, data: dict):
        """
        Inserts a new record into the table.

        Args:
            data (dict): Dictionary where keys are column names and values are the corresponding values.

        Returns:
            int: The number of affected rows.
        """
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        sql = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders});"
        values = list(data.values())

        try:
            with self.connection.cursor() as cursor:
                self.logger.debug("Executing SQL: %s with values %s", sql, values)
                cursor.execute(sql, values)
            self.connection.commit()
            self.logger.info("Record inserted into table '%s'", self.table_name)
            return cursor.rowcount
        except pymysql.MySQLError as e:
            self.logger.error("Error inserting record into table '%s': %s", self.table_name, e)
            raise e

    def read_records(self, limit: int = 10, offset: int = 0):
        """
        Retrieves records from the table with pagination support.

        Args:
            limit (int): Number of records per page.
            offset (int): Number of records to skip.

        Returns:
            tuple: A tuple containing:
                - list of fetched records.
                - list of column names.
        """
        sql = f"SELECT * FROM {self.table_name} LIMIT %s OFFSET %s;"
        try:
            with self.connection.cursor() as cursor:
                self.logger.debug("Executing SQL: %s with limit=%s and offset=%s", sql, limit, offset)
                cursor.execute(sql, (limit, offset))
                records = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
            self.logger.info("Fetched %d records from table '%s'", len(records), self.table_name)
            return records, columns
        except pymysql.MySQLError as e:
            self.logger.error("Error fetching records from table '%s': %s", self.table_name, e)
            raise e

    def update_record(self, record_id, data: dict, id_column: str = "id"):
        """
        Updates a record in the table.

        Args:
            record_id: The primary key or unique identifier of the record to update.
            data (dict): Dictionary of column names and their new values.
            id_column (str): The name of the column used as the identifier (default is "id").

        Returns:
            int: The number of affected rows.
        """
        set_clause = ", ".join([f"{col} = %s" for col in data.keys()])
        sql = f"UPDATE {self.table_name} SET {set_clause} WHERE {id_column} = %s;"
        values = list(data.values()) + [record_id]

        try:
            with self.connection.cursor() as cursor:
                self.logger.debug("Executing SQL: %s with values %s", sql, values)
                cursor.execute(sql, values)
            self.connection.commit()
            self.logger.info("Updated record '%s' in table '%s'", record_id, self.table_name)
            return cursor.rowcount
        except pymysql.MySQLError as e:
            self.logger.error("Error updating record '%s' in table '%s': %s", record_id, self.table_name, e)
            raise e

    def delete_record(self, record_id, id_column: str = "id"):
        """
        Deletes a record from the table.

        Args:
            record_id: The primary key or unique identifier of the record to delete.
            id_column (str): The name of the column used as the identifier (default is "id").

        Returns:
            int: The number of affected rows.
        """
        sql = f"DELETE FROM {self.table_name} WHERE {id_column} = %s;"
        try:
            with self.connection.cursor() as cursor:
                self.logger.debug("Executing SQL: %s with record_id=%s", sql, record_id)
                cursor.execute(sql, (record_id,))
            self.connection.commit()
            self.logger.info("Deleted record '%s' from table '%s'", record_id, self.table_name)
            return cursor.rowcount
        except pymysql.MySQLError as e:
            self.logger.error("Error deleting record '%s' from table '%s': %s", record_id, self.table_name, e)
            raise e

    def read_record(self, record_id, id_column: str = "id"):
        """
        Retrieves a record from the table as a dictionary.

        Args:
            record_id: The primary key or unique identifier of the record to fetch.
            id_column (str): The name of the column used as the identifier (default is "id").

        Returns:
            dict: A dictionary containing the record data if found, otherwise None.
        """
        sql = f"SELECT * FROM {self.table_name} WHERE {id_column} = %s;"
        try:
            with self.connection.cursor() as cursor:
                self.logger.debug("Executing SQL: %s with record_id=%s", sql, record_id)
                cursor.execute(sql, (record_id,))
                record = cursor.fetchone()

                if record:
                    # Fetch column names
                    column_names = [desc[0] for desc in cursor.description]
                    return dict(zip(column_names, record, strict=False))  # Convert tuple to dict
                return None  # No record found
        except pymysql.MySQLError as e:
            self.logger.error("Error reading record '%s' from table '%s': %s", record_id, self.table_name, e)
            raise e
