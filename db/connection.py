import logging

import pymysql


class DatabaseConnector:
    """
    A class to manage MySQL database connections.

    If the specified database does not exist, it creates the database and then establishes the connection.
    """

    def __init__(self, host, port, user, password, database):
        """
        Initializes the DatabaseConnector instance with connection details.
        The connection is established immediately.
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        if not self.logger.handlers:
            self.logger.addHandler(ch)

        self.connection = None

        self.connect()

    def connect(self):
        """
        Connects to the MySQL server.

        First, it connects to the server without specifying a database to check if the database exists.
        If the database does not exist, it creates it, then connects to the database.
        """
        try:
            self.logger.info("Connecting to MySQL server at %s:%s...", self.host, self.port)
            temp_conn = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                autocommit=True
            )
            self.logger.info("Connected to MySQL server successfully.")

            if not self._database_exists(temp_conn):
                self.logger.info("Database '%s' does not exist. Creating it now...", self.database)
                self._create_database(temp_conn)
            temp_conn.close()

            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=True
            )
            self.logger.info("Connected to database: %s", self.database)
        except pymysql.MySQLError as e:
            self.logger.error("Error connecting to MySQL: %s", e)
            raise e

    def _database_exists(self, conn):
        """
        Checks whether the specified database exists.

        Returns:
            bool: True if the database exists, False otherwise.
        """
        try:
            with conn.cursor() as cursor:
                cursor.execute("SHOW DATABASES LIKE %s", (self.database,))
                result = cursor.fetchone()
                exists = result is not None
                self.logger.debug("Database '%s' exists: %s", self.database, exists)
                return exists
        except pymysql.MySQLError as e:
            self.logger.error("Error checking database existence: %s", e)
            raise e

    def _create_database(self, conn):
        """
        Creates the specified database.
        """
        try:
            with conn.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
                self.logger.info("Database '%s' created successfully.", self.database)
        except pymysql.MySQLError as e:
            self.logger.error("Error creating database: %s", e)
            raise e

    def get_connection(self):
        """
        Returns the current database connection.
        If the connection is lost or not established, it reconnects.
        """
        if self.connection is None or not self.connection.open:
            self.logger.info("Re-establishing database connection...")
            self.connect()
        return self.connection
