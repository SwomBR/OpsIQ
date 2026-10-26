# OpsIQ — AI-Powered Business Operations Intelligence Platform

> Transforming raw e-commerce data into actionable business insights using Python, data quality checks, delivery performance analysis, and automated testing.

## 1. Project Overview

**OpsIQ** is a business operations analytics project designed to analyze e-commerce orders, evaluate delivery performance, identify delayed orders, and generate business-friendly reports.

The project uses real-world e-commerce order data to demonstrate how raw data can be transformed into meaningful operational insights.

The goal is to build a practical business intelligence platform while learning Python, data analysis, software testing, and reporting through hands-on development.

**Project status:** In development.

## 2. Business Problem

E-commerce businesses process thousands of orders and need to understand whether orders are being delivered as expected.

Without structured analysis, it can be difficult to answer questions such as:

- How many orders were received and delivered?
- What percentage of orders were delivered?
- How often did deliveries arrive later than estimated?
- How many days late were delayed orders?
- Which orders experienced the longest delays?
- Which delivery exceptions should be investigated first?

OpsIQ addresses these questions by analyzing order records and presenting the results in a structured report.

## 3. Project Objectives

The main objectives are to:

- Load order data from CSV files.
- Inspect data quality and identify missing or duplicate identifiers.
- Summarize order volumes and order statuses.
- Compare estimated and actual delivery dates.
- Calculate on-time and late delivery metrics.
- Identify and rank delayed orders.
- Generate a combined business summary report.
- Validate application logic using automated tests.
- Develop a foundation for future dashboards and cloud-based reporting.

## 4. Dataset

This project uses the Olist Brazilian e-commerce dataset.

The primary input file is:

`data/raw/olist_orders_dataset.csv`

The order dataset contains **99,441 order records**.

Important fields include:

| Column | Description |
|---|---|
| `order_id` | Unique identifier for an order |
| `customer_id` | Identifier for the customer associated with an order |
| `order_status` | Current or recorded order status |
| `order_purchase_timestamp` | Timestamp when the order was placed |
| `order_approved_at` | Timestamp when the order was approved |
| `order_delivered_carrier_date` | Timestamp when the order was handed to the carrier |
| `order_delivered_customer_date` | Timestamp when the order reached the customer |
| `order_estimated_delivery_date` | Estimated delivery date |

**Data handling note:** Missing delivery dates do not automatically indicate bad data. Some orders may not have completed delivery, while other records may require further investigation.

## 5. Features Implemented

### 5.1 Data Loading

**File:** `src/data_loader.py`

- Loads order records from a CSV file.
- Uses Python's CSV module to read structured records.
- Makes the data available to other application components.

### 5.2 Data Quality Validation

**File:** `src/data_validator.py`

- Counts missing values by column.
- Checks for missing order identifiers.
- Identifies duplicate order identifiers.

### 5.3 Order Analysis

**File:** `src/data_analyzer.py`

- Calculates total order volume.
- Counts orders by status.
- Calculates the percentage of orders marked as delivered.
- Handles an empty dataset.

### 5.4 Delivery Performance Analysis

**File:** `src/delivery_analyzer.py`

- Compares actual and estimated delivery dates.
- Counts on-time and late deliveries.
- Calculates on-time and late delivery percentages.
- Calculates average delay among late orders.
- Identifies the maximum recorded delivery delay.
- Counts orders delayed by more than three and seven days.

### 5.5 Delivery Exception Detection

**File:** `src/delivery_exceptions.py`

- Identifies delivered orders that arrived after their estimated dates.
- Calculates the delay duration for each order.
- Records the order ID and relevant delivery dates.
- Sorts exceptions from the longest delay to the shortest.
- Displays the most delayed orders for investigation.

### 5.6 Business Summary Report

**File:** `src/business_report.py`

- Combines order-level and delivery-performance insights.
- Summarizes key business metrics.
- Displays the five most delayed orders.
- Presents the results in a readable terminal report.

### 5.7 Automated Testing

The project uses Python's built-in `unittest` framework.

Current test coverage includes:

- Order count calculations.
- Delivered order calculations.
- Empty dataset handling.
- On-time and late delivery classification.
- Delay duration calculations.
- Missing and invalid delivery dates.
- Ignoring orders that have not been delivered.
- Delivery exception sorting.
- Business summary calculations.

**Latest confirmed result:** 15 automated tests passed.

## 6. Key Findings

The current analysis produced the following results:

| Metric | Result |
|---|---:|
| Total orders | 99,441 |
| Orders marked as delivered | 96,478 |
| Delivered order percentage | 97.02% |
| Late-delivered orders identified | 7,826 |
| Delivered orders analyzed for timeliness | 96,470 |
| On-time delivery percentage | 91.89% |
| Late delivery percentage | 8.11% |
| Average delay among late orders | 9.55 days |
| Maximum recorded delivery delay | 188.98 days |
| Orders delayed more than 3 days | 5,164 |
| Orders delayed more than 7 days | 3,345 |

### Business Interpretation

The analysis indicates that most orders were marked as delivered. However, the delivery analysis also identified thousands of late deliveries.

The most delayed orders can be examined individually to support further investigation.

These findings describe the supplied dataset. They do not, by themselves, establish the causes of delivery delays or prove that the recorded dates are correct.

**Metric definitions:**

- Delivered order percentage = orders marked as delivered divided by all order records.
- On-time delivery percentage = orders delivered on or before the estimated date divided by delivered orders with valid delivery dates.
- Late delivery percentage = late deliveries divided by delivered orders with valid delivery dates.

The delivery analysis skipped eight delivered records because their dates were missing or invalid. Therefore, the number of delivered orders used for the timeliness calculations differs from the total number marked as delivered.

## 7. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data processing and analysis |
| Python CSV module | Reading CSV files |
| `datetime` | Comparing delivery dates and calculating delays |
| `unittest` | Automated testing |
| Visual Studio Code | Development environment |
| Git and GitHub | Version control and project sharing |
| Power BI | Potential future visualization layer |

Power BI dashboard integration and cloud deployment are future development goals, not completed features.

## 8. Project Structure

```text
OpsIQ/
│
├── data/
│   └── raw/
│       └── olist_orders_dataset.csv
│
├── docs/
│
├── src/
│   ├── data_loader.py
│   ├── data_validator.py
│   ├── data_analyzer.py
│   ├── delivery_analyzer.py
│   ├── delivery_exceptions.py
│   └── business_report.py
│
├── tests/
│   ├── test_data_analyzer.py
│   ├── test_delivery_analyzer.py
│   ├── test_delivery_exceptions.py
│   └── test_business_report.py
│
└── README.md
```

## 9. How to Run the Project

### Prerequisites

- Python 3.10 or later.
- Visual Studio Code or another Python-compatible editor.
- The order dataset in the expected project directory.

The project has been developed and tested using Python 3.14.6.

### Step 1: Open the project directory

Open the OpsIQ root directory in your terminal.

### Step 2: Run the business summary report

```powershell
python src/business_report.py
```

This loads the order dataset and generates the combined business summary.

### Step 3: Run the delivery exception report

```powershell
python src/delivery_exceptions.py
```

This identifies late-delivered orders and displays the most delayed records.

### Step 4: Run the automated tests

```powershell
python -m unittest discover -s tests -v
```

The command discovers and runs the automated tests in the `tests` directory.

## 10. Current Limitations

The current version is an early-stage, command-line analytics application.

Known limitations include:

- The analysis currently focuses primarily on the order dataset.
- Missing dates are skipped in delivery calculations and may need additional investigation.
- Delivery delay analysis identifies patterns but does not determine their causes.
- Results are printed to the terminal rather than presented in an interactive dashboard.
- The application does not yet provide a web interface or API.
- Automated tests cover selected behaviours rather than every possible input.
- Cloud deployment and continuous integration are not yet implemented.

## 11. Future Roadmap

Planned development follows the learning cycle:

**Learn → Build → Test → Explain → Document → Move on**

Potential next stages include:

1. Improve error handling and data validation.
2. Expand automated test coverage.
3. Investigate extreme delivery delays and data-quality exceptions.
4. Separate business calculations from report presentation.
5. Add SQL-based data storage and querying.
6. Develop interactive business dashboards.
7. Explore API integration and automation.
8. Introduce continuous integration and deployment.
9. Evaluate cloud deployment options.
10. Document system architecture and testing decisions.

These are planned enhancements and should not be interpreted as already completed.

## 12. Learning Outcomes

Through this project, the developer is practising:

- Python fundamentals and modular programming.
- Reading and processing CSV data.
- Working with dictionaries, lists, loops, and functions.
- Date parsing and duration calculations.
- Data quality checks.
- Business metric calculations.
- Exception identification and prioritization.
- Automated testing and debugging.
- Writing technical documentation.
- Translating business questions into analytical requirements.

## 13. Project Purpose

OpsIQ is being developed as a hands-on learning and portfolio project to demonstrate the process of transforming raw operational data into tested, interpretable business insights.

The long-term objective is to extend the initial analytics pipeline into a more complete business operations intelligence platform.

---

**Project:** OpsIQ — AI-Powered Business Operations Intelligence Platform  
**Status:** In development  
**Primary language:** Python