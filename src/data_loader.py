"""
OpsIQ - Business Operations Intelligence Platform

Module: data_loader.py

Purpose:
    Load order data from a CSV file into Python.

What this module does:
    1. Opens the Olist orders dataset.
    2. Reads each row as a dictionary.
    3. Stores all order records in a list.
    4. Displays the number of records loaded.
    5. Displays the column names and the first order.

Why it is needed:
    OpsIQ needs to load business data before it can inspect,
    validate, analyze, and report on that data.
"""

import csv


def open_order():
    """
    Load order records from the Olist orders CSV file.

    Returns:
        list[dict[str, str]]:
            A list of dictionaries, where each dictionary
            represents one order record.
    """

    file_path = (
        r"C:\Users\Swom.ECPL\Desktop\Sowm\personal"
        r"\my projects\OpsIQ\data\raw"
        r"\olist_orders_dataset.csv"
    )

    with open(
        file_path,
        mode="r",
        newline="",
        encoding="utf-8-sig",
    ) as file:

        reader = csv.DictReader(file)

        orders = list(reader)

        return orders


# Load the order records by calling the function.
orders = open_order()

# Display the total number of records loaded.
print("Total orders loaded:", len(orders))

# Display the column names from the first order.
if orders:
    print("Column names:", orders[0].keys())

    # Display the first order so we can inspect its values.
    print("First order record:", orders[0])
else:
    print("The CSV file contains no order records.")
