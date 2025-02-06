import logging


class InsightsManager:
    def __init__(self, connection):
        """
        Initialize the insights manager with an active database connection.
        """
        self.connection = connection
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    # 1. Total orders per day
    def get_insight_total_orders_per_day(self):
        query = """
            SELECT DATE(order_date) AS order_day, COUNT(*) AS total_orders
            FROM orders
            GROUP BY DATE(order_date)
            ORDER BY order_day;
        """
        # For a trend over time, we use a line chart.
        chart_type = "line_chart"
        description = "Total number of orders per day."
        return query, chart_type, description

    # 2. Total revenue per day
    def get_insight_total_revenue_per_day(self):
        query = """
            SELECT DATE(order_date) AS order_day, SUM(total_amount) AS total_revenue
            FROM orders
            GROUP BY DATE(order_date)
            ORDER BY order_day;
        """
        chart_type = "line_chart"
        description = "Total revenue per day."
        return query, chart_type, description

    # 3. Average order value per day
    def get_insight_avg_order_value_per_day(self):
        query = """
            SELECT DATE(order_date) AS order_day, AVG(total_amount) AS avg_order_value
            FROM orders
            GROUP BY DATE(order_date)
            ORDER BY order_day;
        """
        chart_type = "line_chart"
        description = "Average order value per day."
        return query, chart_type, description

    # 4. Total orders per month
    def get_insight_orders_per_month(self):
        query = """
            SELECT DATE_FORMAT(order_date, '%Y-%m') AS order_month, COUNT(*) AS total_orders
            FROM orders
            GROUP BY DATE_FORMAT(order_date, '%Y-%m')
            ORDER BY order_month;
        """
        chart_type = "bar_chart"
        description = "Total orders per month."
        return query, chart_type, description

    # 5. Total revenue per month
    def get_insight_revenue_per_month(self):
        query = """
            SELECT DATE_FORMAT(order_date, '%Y-%m') AS order_month, SUM(total_amount) AS total_revenue
            FROM orders
            GROUP BY DATE_FORMAT(order_date, '%Y-%m')
            ORDER BY order_month;
        """
        chart_type = "bar_chart"
        description = "Total revenue per month."
        return query, chart_type, description

    # 6. Top 5 restaurants by order count
    def get_insight_top_restaurants_by_orders(self):
        query = """
            SELECT restaurant_id, COUNT(*) AS orders_count
            FROM orders
            GROUP BY restaurant_id
            ORDER BY orders_count DESC
            LIMIT 5;
        """
        chart_type = "bar_chart"
        description = "Top 5 restaurants by order count."
        return query, chart_type, description

    # 7. Top 5 restaurants by revenue
    def get_insight_top_restaurants_by_revenue(self):
        query = """
            SELECT restaurant_id, SUM(total_amount) AS revenue
            FROM orders
            GROUP BY restaurant_id
            ORDER BY revenue DESC
            LIMIT 5;
        """
        chart_type = "bar_chart"
        description = "Top 5 restaurants by revenue."
        return query, chart_type, description

    # 8. Orders distribution by cuisine type
    def get_insight_orders_by_cuisine(self):
        query = """
            SELECT r.cuisine_type, COUNT(*) AS orders_count
            FROM orders o
            JOIN restaurants r ON o.restaurant_id = r.restaurant_id
            GROUP BY r.cuisine_type;
        """
        chart_type = "bar_chart"
        description = "Orders distribution by cuisine type."
        return query, chart_type, description

    # 9. Average delivery time per restaurant
    def get_insight_avg_delivery_time_per_restaurant(self):
        query = """
            SELECT restaurant_id, AVG(TIMESTAMPDIFF(MINUTE, order_date, delivery_time)) AS avg_delivery_time
            FROM orders
            WHERE status = 'delivered'
            GROUP BY restaurant_id;
        """
        chart_type = "bar_chart"
        description = "Average delivery time per restaurant (in minutes)."
        return query, chart_type, description

    # 10. Delivery status distribution
    def get_insight_delivery_status_distribution(self):
        query = """
            SELECT delivery_status, COUNT(*) AS count
            FROM deliveries
            GROUP BY delivery_status;
        """
        chart_type = "bar_chart"
        description = "Distribution of delivery statuses."
        return query, chart_type, description

    # 11. Average feedback rating per restaurant
    def get_insight_avg_feedback_rating_per_restaurant(self):
        query = """
            SELECT restaurant_id, AVG(feedback_rating) AS avg_feedback
            FROM orders
            GROUP BY restaurant_id;
        """
        chart_type = "bar_chart"
        description = "Average feedback rating per restaurant."
        return query, chart_type, description

    # 12. Top 5 customers by order count
    def get_insight_top_customers_by_orders(self):
        query = """
            SELECT customer_id, COUNT(*) AS orders_count
            FROM orders
            GROUP BY customer_id
            ORDER BY orders_count DESC
            LIMIT 5;
        """
        chart_type = "bar_chart"
        description = "Top 5 customers by order count."
        return query, chart_type, description

    # 13. Order status distribution
    def get_insight_order_status_distribution(self):
        query = """
            SELECT status, COUNT(*) AS count
            FROM orders
            GROUP BY status;
        """
        chart_type = "bar_chart"
        description = "Order status distribution."
        return query, chart_type, description

    # 14. Average discount per payment mode
    def get_insight_avg_discount_per_payment_mode(self):
        query = """
            SELECT payment_mode, AVG(discount_applied) AS avg_discount
            FROM orders
            GROUP BY payment_mode;
        """
        chart_type = "bar_chart"
        description = "Average discount per payment mode."
        return query, chart_type, description

    # 15. Delivery fee distribution
    def get_insight_delivery_fee_distribution(self):
        query = """
            SELECT delivery_fee, COUNT(*) AS frequency
            FROM deliveries
            GROUP BY delivery_fee
            ORDER BY delivery_fee;
        """
        chart_type = "bar_chart"
        description = "Delivery fee distribution."
        return query, chart_type, description

    # 16. Average order value by customer type (premium vs non-premium)
    def get_insight_avg_order_value_by_customer_type(self):
        query = """
            SELECT c.is_premium, AVG(o.total_amount) AS avg_order_value
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            GROUP BY c.is_premium;
        """
        chart_type = "bar_chart"
        description = "Average order value by customer type (premium vs non-premium)."
        return query, chart_type, description

    # 17. Daily customer sign-ups
    def get_insight_daily_customer_signups(self):
        query = """
            SELECT DATE(signup_date) AS signup_day, COUNT(*) AS signups
            FROM customers
            GROUP BY DATE(signup_date)
            ORDER BY signup_day;
        """
        chart_type = "line_chart"
        description = "Daily customer sign-ups."
        return query, chart_type, description

    # 18. Orders by payment mode
    def get_insight_orders_by_payment_mode(self):
        query = """
            SELECT payment_mode, COUNT(*) AS orders_count
            FROM orders
            GROUP BY payment_mode;
        """
        chart_type = "bar_chart"
        description = "Orders by payment mode."
        return query, chart_type, description

    # 19. Average feedback rating per day
    def get_insight_avg_feedback_per_day(self):
        query = """
            SELECT DATE(order_date) AS order_day, AVG(feedback_rating) AS avg_feedback
            FROM orders
            GROUP BY DATE(order_date)
            ORDER BY order_day;
        """
        chart_type = "line_chart"
        description = "Average feedback rating per day."
        return query, chart_type, description

    # 20. Orders by customer location
    def get_insight_orders_by_customer_location(self):
        query = """
            SELECT c.location, COUNT(*) AS orders_count
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            GROUP BY c.location
            ORDER BY orders_count DESC;
        """
        chart_type = "bar_chart"
        description = "Orders by customer location."
        return query, chart_type, description

    # 21. Average delivery distance per order
    def get_insight_avg_delivery_distance_per_order(self):
        query = """
            SELECT order_id, AVG(distance) AS avg_distance
            FROM deliveries
            GROUP BY order_id;
        """
        chart_type = "line_chart"
        description = "Average delivery distance per order."
        return query, chart_type, description

    # 22. Top 5 delivery persons by number of deliveries
    def get_insight_top_delivery_persons_by_deliveries(self):
        query = """
            SELECT delivery_person_id, COUNT(*) AS total_deliveries
            FROM deliveries
            GROUP BY delivery_person_id
            ORDER BY total_deliveries DESC
            LIMIT 5;
        """
        chart_type = "bar_chart"
        description = "Top 5 delivery persons by number of deliveries."
        return query, chart_type, description

    # 23. Average feedback rating for delivery persons
    def get_insight_avg_delivery_rating_for_persons(self):
        query = """
            SELECT d.delivery_person_id, AVG(o.feedback_rating) AS avg_rating
            FROM deliveries d
            JOIN orders o ON d.order_id = o.order_id
            GROUP BY d.delivery_person_id;
        """
        chart_type = "bar_chart"
        description = "Average feedback rating for delivery persons."
        return query, chart_type, description

    # 24. Order delivery status ratio
    def get_insight_order_delivery_status_ratio(self):
        query = """
            SELECT status, COUNT(*) AS count
            FROM orders
            GROUP BY status;
        """
        chart_type = "bar_chart"
        description = "Order delivery status ratio."
        return query, chart_type, description

    # 25. Average difference between estimated and actual delivery time
    def get_insight_avg_delivery_time_difference(self):
        query = """
            SELECT order_id, (SUM(estimated_time) - SUM(delivery_time)) AS time_diff
            FROM deliveries
            GROUP BY order_id;
        """
        chart_type = "line_chart"
        description = "Average difference (in minutes) between estimated and actual delivery time."
        return query, chart_type, description

    # 26. Total revenue by restaurant cuisine type
    def get_insight_revenue_by_cuisine(self):
        query = """
            SELECT r.cuisine_type, SUM(o.total_amount) AS total_revenue
            FROM orders o
            JOIN restaurants r ON o.restaurant_id = r.restaurant_id
            GROUP BY r.cuisine_type;
        """
        chart_type = "bar_chart"
        description = "Total revenue by restaurant cuisine type."
        return query, chart_type, description

    # 27. Customer order frequency distribution
    def get_insight_customer_order_frequency(self):
        query = """
            SELECT customer_id, total_orders
            FROM customers
            ORDER BY total_orders DESC;
        """
        chart_type = "histogram"
        description = "Customer order frequency distribution."
        return query, chart_type, description

    # 28. Correlation between order value and feedback
    def get_insight_order_value_vs_feedback(self):
        query = """
            SELECT total_amount, feedback_rating
            FROM orders
            WHERE feedback_rating IS NOT NULL;
        """
        chart_type = "scatter_chart"
        description = "Correlation between order value and feedback rating (Scatter Chart)."
        return query, chart_type, description

    # 29. Comparison of on-time vs delayed deliveries
    def get_insight_delivery_success_vs_delay(self):
        query = """
            SELECT 
                CASE 
                    WHEN TIMESTAMPDIFF(MINUTE, order_date, delivery_time) <= 60 THEN 'On Time'
                    ELSE 'Delayed'
                END AS delivery_performance,
                COUNT(*) AS count
            FROM orders
            WHERE status = 'delivered'
            GROUP BY delivery_performance;
        """
        chart_type = "bar_chart"
        description = "Comparison of on-time versus delayed deliveries."
        return query, chart_type, description

    # 30. Daily average delivery time
    def get_insight_daily_avg_delivery_time(self):
        query = """
            SELECT DATE(order_date) AS order_day, AVG(TIMESTAMPDIFF(MINUTE, order_date, delivery_time)) AS avg_delivery_time
            FROM orders
            WHERE status = 'delivered'
            GROUP BY DATE(order_date)
            ORDER BY order_day;
        """
        chart_type = "line_chart"
        description = "Daily average delivery time."
        return query, chart_type, description
