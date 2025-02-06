# Zomato-Data-Insights

This project is a data insights application for Zomato—a food delivery platform—built with Python, MySQL, and Streamlit.
The application generates synthetic data, stores it in a MySQL database, and provides interactive visualizations via a
multipage Streamlit web app. Users can configure the database connection, manage the database schema and data (CRUD),
generate synthetic data, and explore 30 different insights with multiple chart options using Streamlit's built-in chart
functions.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
    - [1. Clone the Repository](#1-clone-the-repository)
    - [2. Create and Activate a Virtual Environment](#2-create-and-activate-a-virtual-environment)
    - [3. Install Dependencies](#3-install-dependencies)
    - [4. Configure the MySQL Database](#4-configure-the-mysql-database)
    - [5. Generate Synthetic Data](#5-generate-synthetic-data)
    - [6. CRUD Operations & Schema Management](#6-crud-operations--schema-management)
    - [7. Viewing Data Insights](#7-viewing-data-insights)
- [Running the Application](#running-the-application)
- [Code Quality](#code-quality)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Database Configuration:**  
  Configure your MySQL connection via a collapsible form in the sidebar. The app automatically creates the database if
  it does not exist.


- **Data Generation:**  
  Generate synthetic data for tables such as `customers`, `orders`, `restaurants`, `deliveries`, and `delivery_persons`
  using Python's Faker library and insert it into MySQL.


- **CRUD Operations:**  
  Perform Create, Read, Update, and Delete operations on data records via a dedicated user interface.

- Create initial tables (using snake_case names), list tables, and perform dynamic operations such as adding, modifying,
  or dropping columns and tables.


- **Data Insights:**  
  Explore 30 different insights with multiple chart options. Navigate insights using Next/Previous buttons and toggle
  between a raw data table view and a chart view. Chart labels are automatically converted from snake_case to Title Case
  for readability.

## Project Structure

```
zomato_data_insights/
├── app/
│   ├── __init__.py
│   ├── db_config.py           # Database configuration UI (in sidebar, collapsible)
│   ├── crud_operations.py     # CRUD operations & Schema management UI
│   ├── insights.py            # Data insights UI using Streamlit's built-in chart functions
├── crud/
│   └── crud_handler.py        # CRUD operations backend
├── db/
│   ├── __init__.py
│   ├── connection.py          # Database connection class
│   └── schema_manager.py      # Schema management backend
├── data/
│   └── data_generator.py      # Synthetic data generator using Faker
├── insights/
│   └── new_insights_manager.py# Contains 30 insight methods
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation (this file)
└── main.py                    # Main entry point for the multipage Streamlit app
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository_url>
cd zomato_data_insights
```

### 2. Create and Activate a Virtual Environment

**On Windows:**

```powershell
python -m venv venv
.\venv\Scripts\activate
```

**On macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the MySQL Database

- Ensure that MySQL is installed and running.
- Launch the application and navigate to the **Database Config** page (accessible via the sidebar).
- Enter your MySQL host, port, username, password, and desired database name. The app will create the database if it
  does not exist.

### 5. Generate Synthetic Data

- Navigate to the **Data Generation** page.
- Use the provided interface to generate synthetic data for all necessary tables.
- The synthetic data is generated using the Faker library and is inserted into the MySQL database.

### 6. CRUD Operations & Schema Management

- **CRUD Operations:**  
  Use the **CRUD Operations** page to perform Create, Read, Update, and Delete operations on your data.

- **Schema Management:**  
  Use the **Schema Management** page to initialize default tables, list existing tables, and perform dynamic schema
  modifications (e.g., adding, modifying, or dropping columns or tables).

### 7. Viewing Data Insights

- Navigate to the **Data Insights** page.
- Select one of the 30 insights from the dropdown list. Each insight is prefixed with a serial number.
- Use the Next/Previous buttons to navigate through the insights sequentially.
- Toggle between "Data Table" and "Chart" views using the horizontal radio button.
- For chart view, choose the desired chart type from the provided options. Chart labels are automatically converted from
  snake_case to Title Case for readability.

## Running the Application

From the project root, run:

```bash
streamlit run main.py
```

*Note:* Ensure that `st.set_page_config(layout="wide")` is the very first Streamlit command in your `main.py`.

## Code Quality

- **Formatting:** The code is formatted using [Black](https://github.com/psf/black).
- **Linting:** Code linting is enforced using [Ruff](https://github.com/charliermarsh/ruff).
- **Modular Design:** The project is organized into clear, modular packages following object-oriented principles.

## License

This project is licensed under the MIT License.
