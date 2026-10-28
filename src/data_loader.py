"""
OpsIQ - Business Operations Intelligence Platform

Module: data_loader.py

Purpose:
    Load order data from a CSV file into Python.

What this module does:
    1. Opens the Olist orders dataset.
    2. Reads each row as a dictionary.
    3. Stores all order records in a list.
    4. Displays diagnostic information when run directly.

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


if __name__ == "__main__":
    # Load the order records when this file is run directly.
    orders = open_order()

    # Display diagnostic information.
    print("Total orders loaded:", len(orders))

    if orders:
        print("Column names:", orders[0].keys())
        print("First order record:", orders[0])
    else:
        print("The CSV file contains no order records.")
