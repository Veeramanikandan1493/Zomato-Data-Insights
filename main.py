import streamlit as st


def load_page(page):
    if page == "Database Config":
        import app.db_config as db_config
        db_config.app()
    elif page == "Data Generation":
        import app.data_generation as data_generation
        data_generation.app()
    elif page == "CRUD Operations":
        import app.crud_operations as crud_operations
        crud_operations.app()
    elif page == "Data Insights":
        import app.insights as insights
        insights.app()

def main():
    st.set_page_config(layout="wide")
    if "db_connected" not in st.session_state:
        st.session_state.db_connected = False

    st.sidebar.title("Zomato Data Analysis")
    page = st.sidebar.radio(
        "Select a page",
        ["Data Generation", "CRUD Operations", "Data Insights"]
    )
    if st.session_state.db_connected:
        load_page(page)
    else:
        st.error("Database not configured. Please use the 'Database Configuration' in the side menu.")
    load_page("Database Config")

if __name__ == "__main__":
    main()
