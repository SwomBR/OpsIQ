# OpsIQ — AI-Powered Business Operations Intelligence Platform

> Transforming raw e-commerce data into actionable business insights using Python, data quality checks, delivery, sales, product, and customer analysis, and automated testing.

## 1. Project Overview

**OpsIQ** is a business operations analytics project designed to analyze e-commerce orders, evaluate delivery performance, identify delayed orders, check data quality, and generate business-friendly reports.

The project uses real-world e-commerce data to demonstrate how raw data can be transformed into meaningful operational insights.

The goal is to build a practical business intelligence platform while learning Python, data analysis, software testing, and reporting through hands-on development.

**Project status:** Working command-line analytics application (version 1). Further features are planned; see [Future Roadmap](#12-future-roadmap).

**About the name:** "AI-Powered" describes the long-term vision for the platform. The current version does **not** use artificial intelligence or machine learning. All results come from plain, rule-based Python calculations.

## 2. Business Problem

E-commerce businesses process thousands of orders and need to understand whether orders are being delivered as expected, where revenue comes from, and who their customers are.

Without structured analysis, it can be difficult to answer questions such as:

- How many orders were received and delivered?
- How often did deliveries arrive later than estimated, and by how many days?
- Which delayed orders should be investigated first?
- How much product revenue and freight was recorded, and how did customers pay?
- Which product categories and products sell the most?
- How many customers return to buy again, and where are customers located?
- Is the data itself reliable enough to trust these numbers?

OpsIQ addresses these questions by analyzing the dataset and presenting the results in structured terminal reports.

## 3. Main Features

| Feature | Module | What it does |
|---|---|---|
| Data loading | `src/data_loader.py` | Loads the orders CSV file into a list of dictionaries. |
| Data quality validation | `src/data_validator.py` | Checks for missing, duplicate, invalid, and inconsistent order data. |
| Order analysis | `src/data_analyzer.py` | Counts orders by status and calculates the delivered percentage. |
| Delivery performance | `src/delivery_analyzer.py` | Measures on-time and late deliveries and delay durations. |
| Delivery exceptions | `src/delivery_exceptions.py` | Lists late orders, ranked from the longest delay. |
| Sales and payments | `src/sales_analyzer.py` | Calculates product revenue, freight, average order value, and payment totals by method. |
| Product performance | `src/product_analyzer.py` | Ranks categories by revenue and products by quantity sold. |
| Customer analytics | `src/customer_analyzer.py` | Counts unique and repeat customers, top spenders, and customers by state. |
| Business report | `src/business_report.py` | Combines all of the above into one report. |

## 4. Dataset

This project uses the public **Olist Brazilian E-Commerce** dataset, available on Kaggle:
<https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce>

The CSV files are **not included in this repository** (they are listed in `.gitignore`). Download them and place them in `data/raw/`.

The application uses these files:

| File | Used for |
|---|---|
| `olist_orders_dataset.csv` | Orders, statuses, and delivery dates (99,441 records) |
| `olist_order_items_dataset.csv` | Product prices and freight charges |
| `olist_order_payments_dataset.csv` | Payment methods and values |
| `olist_products_dataset.csv` | Product categories |
| `olist_customers_dataset.csv` | Customer identities and states |
| `product_category_name_translation.csv` | English category names |

Important order fields include:

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

## 5. Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Data processing and analysis |
| `csv` module | Reading CSV files |
| `datetime` module | Comparing dates and calculating delays |
| `pathlib` module | Locating the data folder on any computer |
| `collections` module | Grouping and totalling values |
| `unittest` module | Automated testing |
| Visual Studio Code | Development environment |
| Git and GitHub | Version control and project sharing |

OpsIQ uses **only the Python standard library**. There are no external packages to install, so no `requirements.txt` file is needed.

## 6. Project Structure

```text
OpsIQ/
│
├── data/
│   ├── raw/                  # Olist CSV files go here (not committed)
│   └── processed/            # Reserved for future processed data
│
├── docs/
│   └── AI_Powered_Business_Operations_Intelligence_Platform_Master_Plan_v1.docx
│
├── src/
│   ├── data_loader.py
│   ├── data_validator.py
│   ├── data_analyzer.py
│   ├── delivery_analyzer.py
│   ├── delivery_exceptions.py
│   ├── sales_analyzer.py
│   ├── product_analyzer.py
│   ├── customer_analyzer.py
│   └── business_report.py
│
├── tests/
│   ├── test_business_report.py
│   ├── test_customer_analyzer.py
│   ├── test_data_analyzer.py
│   ├── test_data_loader.py
│   ├── test_data_validator.py
│   ├── test_delivery_analyzer.py
│   ├── test_delivery_exceptions.py
│   ├── test_product_analyzer.py
│   └── test_sales_analyzer.py
│
├── .gitignore
└── README.md
```

## 7. Setup on a New Machine

### Prerequisites

- Python 3.10 or later. The project has been developed and tested with Python 3.14.6.
- Git (optional, for cloning the repository).

Check your Python version:

```powershell
python --version
```

### Step 1: Get the project

```powershell
git clone <repository-url>
cd OpsIQ
```

### Step 2: Add the dataset

1. Download the Olist dataset from Kaggle (link in [Section 4](#4-dataset)).
2. Extract the ZIP file.
3. Copy the CSV files into the `data/raw/` folder inside the project.

If a file is missing, the business report prints which file it could not find and where it expected it.

No other installation is needed.

## 8. How to Run the Project

**Run every command from the project root folder** (the `OpsIQ` folder that contains `src/` and `tests/`).

Modules are run with `python -m src.<module_name>`. This lets Python find the `src` package, which all modules import from.

### Full business report (main entry point)

```powershell
python -m src.business_report
```

### Data quality report

```powershell
python -m src.data_validator
```

### Individual reports

```powershell
python -m src.delivery_exceptions
python -m src.delivery_analyzer
python -m src.data_analyzer
python -m src.sales_analyzer
python -m src.product_analyzer
python -m src.customer_analyzer
```

**Note:** Running a file directly, for example `python src/business_report.py`, does **not** work. Python then cannot find the `src` package and reports `ModuleNotFoundError: No module named 'src'`. Use the `python -m` commands above instead.

## 9. How to Run the Tests

```powershell
python -m unittest discover -s tests -v
```

The tests use small, hand-written sample records, so they **do not need the Olist dataset**.

**Latest confirmed result:** 54 tests ran, 54 passed, 0 failed.

Test coverage includes:

- Order counts, delivered counts, and empty datasets.
- Correct dataset location and CSV loading.
- On-time and late delivery classification, delay durations, and missing or invalid dates.
- Delivery exception detection and sorting.
- Sales revenue, freight, average order value, and payment totals.
- Product category revenue, quantities, translations, and missing categories.
- Unique and repeat customers, combined spending, and customers by state.
- Every data quality check, including whitespace-only values, status capitalisation and spacing, missing middle dates, unreadable dates, and records with missing fields.
- The combined business report output.

## 10. What the Business Report Contains

`python -m src.business_report` prints these sections, in order:

1. **Order summary:** total orders, delivered orders, delivered percentage, late-delivered orders.
2. **Delivery performance details:** on-time and late counts and percentages, average and maximum delay, orders delayed by more than 3 and 7 days.
3. **Highest-priority delivery exceptions:** the five most delayed orders.
4. **Sales and payment analytics:** product revenue, freight charges, orders with item records, average product value per order, payment totals by method.
5. **Product performance:** catalog size, products missing a category, top 5 categories by revenue, top 5 products by quantity sold.
6. **Customer analytics:** unique customers, repeat customers and percentage, top 5 customers by product spending, top 10 states by customer count.

The report ends with the line `END OF OPSIQ REPORT`.

### Key results from the current dataset

| Metric | Result |
|---|---:|
| Total orders | 99,441 |
| Orders marked as delivered | 96,478 (97.02%) |
| Delivered orders analyzed for timeliness | 96,470 |
| On-time delivery percentage | 91.89% |
| Late-delivered orders | 7,826 (8.11%) |
| Average delay among late orders | 9.55 days |
| Maximum recorded delivery delay | 188.98 days |
| Orders delayed more than 3 days | 5,164 |
| Orders delayed more than 7 days | 3,345 |
| Total product revenue | 13,591,643.70 |
| Total freight charges | 2,251,909.54 |
| Average product value per order | 137.75 |
| Top category by revenue | health_beauty (1,258,681.34) |
| Unique customers | 96,096 |
| Repeat customers | 2,997 (3.12%) |

Monetary values are in Brazilian reais (BRL), as recorded in the dataset.

### Metric definitions

- **Delivered order percentage** = orders marked as delivered ÷ all order records.
- **On-time delivery percentage** = delivered orders that arrived on or before the estimated date and time ÷ delivered orders with valid dates.
- **Late delivery percentage** = delivered orders that arrived after the estimated date and time ÷ delivered orders with valid dates.
- **Average product value per order** = total product revenue ÷ orders that have item records. Freight is not included.
- **Repeat customer** = a unique customer (`customer_unique_id`) with more than one order.

### Business interpretation

Most orders were delivered, but the analysis still identified thousands of late deliveries, some of them months late. The most delayed orders are listed individually to support investigation.

These findings describe the supplied dataset. They do not, by themselves, establish the causes of delivery delays or prove that the recorded dates are correct.

## 11. Data Quality Checks

`python -m src.data_validator` checks the orders dataset for:

| Check | What it looks for |
|---|---|
| Missing values | Empty or whitespace-only values in each column |
| Missing order IDs | Records without an `order_id` |
| Duplicate order IDs | The same `order_id` appearing more than once |
| Invalid order statuses | Statuses outside the 8 known Olist statuses (case and extra spaces are ignored) |
| Invalid date formats | Non-empty dates that are not in `YYYY-MM-DD HH:MM:SS` format |
| Inconsistent processing timestamps | Steps recorded out of order, for example handed to the carrier before approval (missing steps are skipped) |
| Delivered orders missing delivery dates | Orders marked delivered with no customer delivery date |

On the current dataset, the validator found **1,382 orders with out-of-order processing timestamps** and **8 delivered orders without a delivery date**. It found no missing or duplicate order IDs, invalid statuses, or invalid date formats.

## 12. Known Limitations and Assumptions

- **Command-line only.** Results are printed to the terminal. There is no dashboard, web interface, API, database, or cloud deployment.
- **Run from the project root** with `python -m src.<module>`. Running files directly does not work (see [Section 8](#8-how-to-run-the-project)).
- **Late means after the estimated timestamp.** Every estimated delivery date in the dataset is at midnight (`00:00:00`). An order delivered later on the estimated day therefore counts as late. 1,292 of the 7,826 late orders fall into this group.
- **Missing or unreadable delivery dates are skipped** in delivery calculations (8 delivered orders), and may need separate investigation.
- **Delivery analysis identifies delays but not their causes.**
- **Categories:** products without a category are reported as `unknown`, and two categories have no English translation in the dataset, so they appear in Portuguese.
- **Customers by state:** 39 customers appear in more than one state, so the state counts add up to slightly more than the number of unique customers.
- **Payment totals** include all payment records (including vouchers and instalment amounts), so they do not exactly equal product revenue plus freight.
- **Data is loaded fully into memory**, which works well for this dataset size but would need a different approach for much larger data.
- **Automated tests use small sample records.** They cover the core rules but not every possible input.
- **No continuous integration** is set up yet.

## 13. Future Roadmap

Planned development follows the learning cycle:

**Learn → Build → Test → Explain → Document → Move on**

Potential next stages include:

1. Investigate extreme delivery delays and the data-quality exceptions found by the validator.
2. Decide whether "late" should compare calendar dates instead of timestamps.
3. Separate business calculations from report presentation.
4. Save report results to files (for example CSV) in `data/processed/`.
5. Add SQL-based data storage and querying.
6. Develop interactive business dashboards (for example Power BI).
7. Explore API integration and automation.
8. Introduce continuous integration.
9. Evaluate cloud deployment options.
10. Explore AI-assisted insights, in line with the long-term vision.

These are planned enhancements and should not be interpreted as already completed.

## 14. Learning Outcomes

Through this project, the developer is practising:

- Python fundamentals and modular programming.
- Reading and processing CSV data.
- Working with dictionaries, lists, sets, loops, and functions.
- Date parsing and duration calculations.
- Data quality checks.
- Business metric calculations.
- Exception identification and prioritization.
- Automated testing and debugging.
- Version control with Git.
- Writing technical documentation.
- Translating business questions into analytical requirements.

## 15. Project Purpose

OpsIQ is being developed as a hands-on learning and portfolio project to demonstrate the process of transforming raw operational data into tested, interpretable business insights.

The long-term objective is to extend the initial analytics pipeline into a more complete business operations intelligence platform.

---

**Project:** OpsIQ — AI-Powered Business Operations Intelligence Platform

**Status:** Version 1 — working command-line analytics application

**Primary language:** Python
