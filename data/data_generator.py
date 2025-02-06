import logging
import random
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st
from faker import Faker


class DataGenerator:
    """
    Generates synthetic data for the Zomato project using Faker and Pandas.
    Supports data generation for Customers, Restaurants, Delivery Persons, Orders, and Deliveries.
    """

    def __init__(self, record_count=100):
        """
        Initializes the DataGenerator with the default record count and date range.

        Args:
            record_count (int): Number of records to generate per table.
        """
        self.record_count = record_count
        self.fake = Faker()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        if not self.logger.handlers:
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

        self.customers = None
        self.restaurants = None
        self.delivery_persons = None
        self.orders = None
        self.deliveries = None

        self.end_date = datetime.now()
        self.start_date = self.end_date - timedelta(days=2*365)

    def generate_customers(self):
        """Generates synthetic data for the Customers table."""
        self.logger.info("Generating customers data...")
        data = []
        cuisines = ["Italian", "Chinese", "Indian", "Mexican", "American"]
        for i in range(1, self.record_count + 1):
            customer = {
                "name": self.fake.name(),
                "email": self.fake.email(),
                "phone": self.fake.phone_number(),
                "location": self.fake.city(),
                "signup_date": self.fake.date_between_dates(date_start=self.start_date, date_end=self.end_date),
                "is_premium": random.choice([True, False]),
                "preferred_cuisine": random.choice(cuisines),
                "total_orders": random.randint(0, 50),
                "average_rating": round(random.uniform(1, 5), 2)
            }
            data.append(customer)
        self.customers = pd.DataFrame(data)
        self.logger.info("Generated %d customers.", len(self.customers))
        return self.customers

    def generate_restaurants(self):
        """Generates synthetic data for the Restaurants table."""
        self.logger.info("Generating restaurants data...")
        data = []
        cuisines = ["Italian", "Chinese", "Indian", "Mexican", "American"]
        for i in range(1, self.record_count + 1):
            restaurant = {
                "name": self.fake.company(),
                "cuisine_type": random.choice(cuisines),
                "location": self.fake.city(),
                "owner_name": self.fake.name(),
                "average_delivery_time": random.randint(20, 60),
                "contact_number": self.fake.phone_number(),
                "rating": round(random.uniform(1, 5), 2),
                "total_orders": random.randint(0, 100),
                "is_active": random.choice([True, False])
            }
            data.append(restaurant)
        self.restaurants = pd.DataFrame(data)
        self.logger.info("Generated %d restaurants.", len(self.restaurants))
        return self.restaurants

    def generate_delivery_persons(self):
        """Generates synthetic data for the Delivery Persons table."""
        self.logger.info("Generating delivery persons data...")
        data = []
        vehicle_types = ["Bike", "Car"]
        for i in range(1, self.record_count + 1):
            delivery_person = {
                "name": self.fake.name(),
                "contact_number": self.fake.phone_number(),
                "vehicle_type": random.choice(vehicle_types),
                "total_deliveries": random.randint(0, 200),
                "average_rating": round(random.uniform(1, 5), 2),
                "location": self.fake.city()
            }
            data.append(delivery_person)
        self.delivery_persons = pd.DataFrame(data)
        self.logger.info("Generated %d delivery persons.", len(self.delivery_persons))
        return self.delivery_persons

    def generate_orders(self, customer_id_list, restaurants_id_list):
        """Generates synthetic data for the Orders table."""
        self.logger.info("Generating orders data...")
        data = []
        statuses = ["Pending", "Delivered", "Cancelled"]
        payment_modes = ["Credit Card", "Cash", "UPI"]
        for i in range(1, self.record_count + 1):
            order_date = self.fake.date_time_between_dates(datetime_start=self.start_date, datetime_end=self.end_date)
            delivery_delay = timedelta(minutes=random.randint(20, 90))
            delivery_time = order_date + delivery_delay
            order = {
                "customer_id": random.choice(customer_id_list),
                "restaurant_id": random.choice(restaurants_id_list),
                "order_date": order_date,
                "delivery_time": delivery_time,
                "status": random.choice(statuses),
                "total_amount": round(random.uniform(5, 100), 2),
                "payment_mode": random.choice(payment_modes),
                "discount_applied": round(random.uniform(0, 20), 2),
                "feedback_rating": round(random.uniform(1, 5), 2)
            }
            data.append(order)
        self.orders = pd.DataFrame(data)
        self.logger.info("Generated %d orders.", len(self.orders))
        return self.orders

    def generate_deliveries(self, order_id_list, delivery_person_id_list):
        """Generates synthetic data for the Deliveries table."""
        self.logger.info("Generating deliveries data...")
        data = []
        delivery_statuses = ["On the way", "Delivered"]
        vehicle_types = ["Bike", "Car"]
        for i in range(1, self.record_count + 1):
            order_id = random.choice(order_id_list)
            delivery_person_id = random.choice(delivery_person_id_list)
            actual_delivery_time = random.randint(20, 90)
            estimated_time = actual_delivery_time + random.randint(-5, 5)
            delivery = {
                "order_id": order_id,
                "delivery_person_id": delivery_person_id,
                "delivery_status": random.choice(delivery_statuses),
                "distance": round(random.uniform(1, 20), 2),
                "delivery_time": actual_delivery_time,
                "estimated_time": estimated_time,
                "delivery_fee": round(random.uniform(1, 10), 2),
                "vehicle_type": random.choice(vehicle_types)
            }
            data.append(delivery)
        self.deliveries = pd.DataFrame(data)
        self.logger.info("Generated %d deliveries.", len(self.deliveries))
        return self.deliveries

    def generate_all_data(self, generation_type="primary"):
        """
        Generates data for all tables and returns a dictionary of DataFrames.

        Returns:
            dict: Contains DataFrames for 'customers', 'restaurants', 'delivery_persons', 'orders', and 'deliveries'.
        """
        if generation_type == "primary":
            return {
                "customers": self.generate_customers(),
                "restaurants": self.generate_restaurants(),
                "delivery_persons": self.generate_delivery_persons()
            }
        if generation_type == "secondary":
            connection = st.session_state.db_connector.get_connection()
            with connection.cursor() as cursor:
                query = "SELECT customer_id FROM customers"
                cursor.execute(query)
                data = cursor.fetchall()
                customer_id_list = [d[0] for d in data]

                query = "SELECT restaurant_id FROM restaurants"
                cursor.execute(query)
                data = cursor.fetchall()
                restaurants_id_list = [d[0] for d in data]
                return {
                    "orders": self.generate_orders(customer_id_list, restaurants_id_list)
                }
        if generation_type == "tertiary":
            connection = st.session_state.db_connector.get_connection()
            with connection.cursor() as cursor:
                query = "SELECT order_id FROM orders"
                cursor.execute(query)
                data = cursor.fetchall()
                order_id_list = [d[0] for d in data]

                query = "SELECT delivery_person_id FROM delivery_persons"
                cursor.execute(query)
                data = cursor.fetchall()
                delivery_person_id_list = [d[0] for d in data]
                return {
                    "deliveries": self.generate_deliveries(order_id_list, delivery_person_id_list)
                }
        return {}

    def insert_data(self, connection):
        """
        Inserts the generated data into the corresponding database tables.

        Assumes that the tables have already been created.

        Args:
            connection (pymysql.connections.Connection): Active database connection.
        """
        data_dict = self.generate_all_data()
        with connection.cursor() as cursor:
            self.logger.info("Inserting customers into database...")
            customer_query = """
                INSERT INTO customers (name, email, phone, location, signup_date, is_premium, preferred_cuisine, total_orders, average_rating)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            customers = data_dict["customers"]
            customer_values = customers.values.tolist()
            cursor.executemany(customer_query, customer_values)

            self.logger.info("Inserting restaurants into database...")
            restaurant_query = """
                INSERT INTO restaurants (name, cuisine_type, location, owner_name, average_delivery_time, contact_number, rating, total_orders, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            restaurants = data_dict["restaurants"]
            restaurant_values = restaurants.values.tolist()
            cursor.executemany(restaurant_query, restaurant_values)

            self.logger.info("Inserting delivery persons into database...")
            dp_query = """
                INSERT INTO delivery_persons (name, contact_number, vehicle_type, total_deliveries, average_rating, location)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            dps = data_dict["delivery_persons"]
            dp_values = dps.values.tolist()
            cursor.executemany(dp_query, dp_values)

        data_dict = self.generate_all_data(generation_type="secondary")
        with connection.cursor() as cursor:

            self.logger.info("Inserting orders into database...")
            orders_query = """
                INSERT INTO orders (customer_id, restaurant_id, order_date, delivery_time, status, total_amount, payment_mode, discount_applied, feedback_rating)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            orders = data_dict["orders"]
            orders['order_date'] = orders['order_date'].astype(str)
            orders['delivery_time'] = orders['delivery_time'].astype(str)
            order_values = orders.values.tolist()
            cursor.executemany(orders_query, order_values)

        data_dict = self.generate_all_data(generation_type="tertiary")
        with connection.cursor() as cursor:

            self.logger.info("Inserting deliveries into database...")
            deliveries_query = """
                INSERT INTO deliveries (order_id, delivery_person_id, delivery_status, distance, delivery_time, estimated_time, delivery_fee, vehicle_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            deliveries = data_dict["deliveries"]
            delivery_values = deliveries.values.tolist()
            cursor.executemany(deliveries_query, delivery_values)

            connection.commit()
            self.logger.info("Data insertion complete.")
