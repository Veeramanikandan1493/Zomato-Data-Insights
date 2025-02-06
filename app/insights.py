import pandas as pd
import streamlit as st

from insights.insights_manager import InsightsManager


def convert_to_title(snake_str):
    """Convert a snake_case string to Title Case."""
    return ' '.join(word.capitalize() for word in snake_str.split('_'))


def app():
    st.title("Data Insights & Visualisations")

    if "db_connector" not in st.session_state:
        st.error("Database not configured. Please go to 'Database Config' page.")
        return

    connection = st.session_state.db_connector.get_connection()
    insights_manager = InsightsManager(connection)

    insight_options = {
        "Total orders per day": insights_manager.get_insight_total_orders_per_day,
        "Total revenue per day": insights_manager.get_insight_total_revenue_per_day,
        "Average order value per day": insights_manager.get_insight_avg_order_value_per_day,
        "Total orders per month": insights_manager.get_insight_orders_per_month,
        "Total revenue per month": insights_manager.get_insight_revenue_per_month,
        "Top 5 restaurants by order count": insights_manager.get_insight_top_restaurants_by_orders,
        "Top 5 restaurants by revenue": insights_manager.get_insight_top_restaurants_by_revenue,
        "Orders distribution by cuisine type": insights_manager.get_insight_orders_by_cuisine,
        "Average delivery time per restaurant": insights_manager.get_insight_avg_delivery_time_per_restaurant,
        "Delivery status distribution": insights_manager.get_insight_delivery_status_distribution,
        "Average feedback rating per restaurant": insights_manager.get_insight_avg_feedback_rating_per_restaurant,
        "Top 5 customers by order count": insights_manager.get_insight_top_customers_by_orders,
        "Order status distribution": insights_manager.get_insight_order_status_distribution,
        "Average discount per payment mode": insights_manager.get_insight_avg_discount_per_payment_mode,
        "Delivery fee distribution": insights_manager.get_insight_delivery_fee_distribution,
        "Average order value by customer type": insights_manager.get_insight_avg_order_value_by_customer_type,
        "Daily customer sign-ups": insights_manager.get_insight_daily_customer_signups,
        "Orders by payment mode": insights_manager.get_insight_orders_by_payment_mode,
        "Average feedback rating per day": insights_manager.get_insight_avg_feedback_per_day,
        "Orders by customer location": insights_manager.get_insight_orders_by_customer_location,
        "Average delivery distance per order": insights_manager.get_insight_avg_delivery_distance_per_order,
        "Top 5 delivery persons by deliveries": insights_manager.get_insight_top_delivery_persons_by_deliveries,
        "Average feedback rating for delivery persons": insights_manager.get_insight_avg_delivery_rating_for_persons,
        "Order delivery status ratio": insights_manager.get_insight_order_delivery_status_ratio,
        "Average difference between estimated and actual delivery time": insights_manager.get_insight_avg_delivery_time_difference,
        "Total revenue by restaurant cuisine type": insights_manager.get_insight_revenue_by_cuisine,
        "Customer order frequency distribution": insights_manager.get_insight_customer_order_frequency,
        "Correlation between order value and feedback": insights_manager.get_insight_order_value_vs_feedback,
        "Comparison of on-time vs delayed deliveries": insights_manager.get_insight_delivery_success_vs_delay,
        "Daily average delivery time": insights_manager.get_insight_daily_avg_delivery_time
    }

    insight_keys = list(insight_options.keys())
    total_insights = len(insight_keys)

    if "insight_index" not in st.session_state:
        st.session_state.insight_index = 0

    formatted_options = [f"{i + 1}. {insight_keys[i]}" for i in range(total_insights)]
    default_index = st.session_state.insight_index
    selected_option = st.selectbox("Select an Insight", formatted_options, index=default_index)
    st.session_state.insight_index = formatted_options.index(selected_option)
    current_insight = insight_keys[st.session_state.insight_index]
    st.header(f"Insight {st.session_state.insight_index + 1} of {total_insights}: {current_insight}")

    col_prev, col_next = st.columns(2)
    with col_prev:
        if st.button("Previous"):
            st.session_state.insight_index = (st.session_state.insight_index - 1) % total_insights
            st.rerun()
    with col_next:
        if st.button("Next"):
            st.session_state.insight_index = (st.session_state.insight_index + 1) % total_insights
            st.rerun()

    view_options = ["Data Table", "Chart"]
    if "view_option" not in st.session_state:
        st.session_state["view_option"] = view_options[0]

    view_option = st.radio(
        "View Option",
        view_options,
        horizontal=True,
        key="view_option"
    )
    view_option = st.session_state.get("view_option", view_options[0])

    st.write("Current View Option:", view_option)

    try:
        query, default_chart_type, description = insight_options[current_insight]()
        df = pd.read_sql(query, connection)
        st.write(description)
        df.columns = [convert_to_title(col) for col in df.columns]

        if view_option == "Data Table":
            st.dataframe(df)
        else:
            chart_options = []
            if default_chart_type == "line_chart":
                chart_options = ["Line Chart", "Area Chart"]
            elif default_chart_type == "bar_chart":
                chart_options = ["Bar Chart"]
            elif default_chart_type == "scatter_plot":
                chart_options = ["Scatter Chart"]
            else:
                chart_options = [default_chart_type]

            default_chart = st.session_state.get("selected_chart", chart_options[0])
            if default_chart not in chart_options:
                default_chart = chart_options[0]

            selected_chart = st.radio("Select Chart Type", chart_options, index=chart_options.index(default_chart), horizontal=True,
                                      key="chart_type")
            st.session_state.selected_chart = selected_chart

            df_indexed = df.set_index(df.columns[0])
            if selected_chart == "Line Chart":
                st.line_chart(df_indexed)
            elif selected_chart == "Area Chart":
                st.area_chart(df_indexed)
            elif selected_chart == "Bar Chart":
                st.bar_chart(df_indexed)
            elif selected_chart == "Scatter Chart":
                st.scatter_chart(df)
            else:
                st.write("Chart type not recognized by Streamlit's built-in charts.")
    except Exception as e:
        st.error(f"Error executing insight: {e}")
