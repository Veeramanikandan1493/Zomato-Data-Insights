import streamlit as st

from db.connection import DatabaseConnector


def app():
    expanded_state = not st.session_state.db_connected

    with st.sidebar.expander("Database Configuration", expanded=expanded_state):
        st.markdown("### Configure Your Database Connection")

        col1, col2, col3 = st.columns(3)
        with col1:
            host = st.text_input("MySQL Host", "localhost", key="host")
        with col2:
            port = st.number_input("Port", min_value=1, value=3306, key="port")
        with col3:
            user = st.text_input("Username", "root", key="user")

        col4, col5 = st.columns(2)
        with col4:
            password = st.text_input("Password", type="password", key="password")
        with col5:
            database = st.text_input("Database Name", "zomato_db", key="database")

        if st.button("Connect", key="connect_button"):
            try:
                db_connector = DatabaseConnector(host, port, user, password, database)
                st.session_state.db_connector = db_connector
                st.session_state.db_connected = True
                st.success("Connected to database!")
                st.rerun()
            except Exception as e:
                st.session_state.db_connected = False
                st.error(f"Connection failed: {e}")

    if st.session_state.db_connected:
        st.sidebar.markdown(
            '<p style="color:green; font-weight:bold;">Database Connected</p>',
            unsafe_allow_html=True,
        )
    else:
        st.sidebar.markdown(
            '<p style="color:red; font-weight:bold;">Database Disconnected</p>',
            unsafe_allow_html=True,
        )
