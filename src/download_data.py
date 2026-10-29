"""
OpsIQ - Business Operations Intelligence Platform

Module: download_data.py

Purpose:
    Download the public Olist dataset from Kaggle and extract the CSV
    files OpsIQ uses. Hosting services run this during the build,
    because the CSV files are not stored in the Git repository.

Usage (from the project root):
    python -m src.download_data                  Into data/raw/
    python -m src.download_data --data-dir DIR   Into another folder
    python -m src.download_data --force          Replace existing files

The dataset is published by Olist on Kaggle under the CC BY-NC-SA 4.0
licence: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
"""

import argparse
import os
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path

from src.data_loader import RAW_DATA_DIR

DATASET_URL = (
    "https://www.kaggle.com/api/v1/datasets/download/olistbr/brazilian-ecommerce"
)

# Only these files are extracted. The archive also holds geolocation,
# reviews, and sellers files, which the analytics and API do not need.
REQUIRED_FILES = [
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_products_dataset.csv",
    "olist_customers_dataset.csv",
    "product_category_name_translation.csv",
]

# Also needed by the optional SQLite database (python -m src.database).
DATABASE_FILES = ["olist_sellers_dataset.csv"]


def missing_files(data_dir, file_names):
    """Return the names in file_names that are not in data_dir."""

    return [name for name in file_names if not (data_dir / name).exists()]


def extract_files(archive_path, data_dir, file_names):
    """Copy file_names out of the zip archive into data_dir.

    Files are looked up by their exact names, so nothing else in the
    archive can be written anywhere.
    """

    data_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(archive_path) as archive:
        available = set(archive.namelist())
        absent = [name for name in file_names if name not in available]

        if absent:
            raise ValueError(
                f"The downloaded archive is missing: {', '.join(absent)}"
            )

        for name in file_names:
            with archive.open(name) as source, open(data_dir / name, "wb") as target:
                shutil.copyfileobj(source, target)


def download_dataset(data_dir=RAW_DATA_DIR, force=False, include_database=False):
    """Download and extract the dataset unless the files already exist.

    Returns:
        list[str]: The files that were extracted (empty when none were
        needed).
    """

    data_dir = Path(data_dir)
    file_names = REQUIRED_FILES + (DATABASE_FILES if include_database else [])

    if not force and not missing_files(data_dir, file_names):
        return []

    with tempfile.TemporaryDirectory() as temp_dir:
        archive_path = Path(temp_dir) / "olist.zip"
        request = urllib.request.Request(
            DATASET_URL, headers={"User-Agent": "OpsIQ data download"}
        )

        with urllib.request.urlopen(request, timeout=120) as response:
            with open(archive_path, "wb") as file:
                shutil.copyfileobj(response, file)

        extract_files(archive_path, data_dir, file_names)

    return file_names


def main(arguments=None):
    parser = argparse.ArgumentParser(
        prog="python -m src.download_data",
        description="Download the Olist CSV files that OpsIQ uses.",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        # The backend reads OPSIQ_DATA_DIR, so use the same folder.
        default=Path(os.environ.get("OPSIQ_DATA_DIR", RAW_DATA_DIR)),
    )
    parser.add_argument("--force", action="store_true",
                        help="Download even if the files already exist.")
    parser.add_argument("--with-database-files", action="store_true",
                        help="Also extract the sellers file for the SQL database.")
    args = parser.parse_args(arguments)

    try:
        extracted = download_dataset(
            args.data_dir, args.force, args.with_database_files
        )
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        print(f"Download failed: {error}")
        print(
            "Download the dataset manually from "
            "https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce "
            f"and place the CSV files in {args.data_dir}"
        )
        return 1

    if extracted:
        print(f"Extracted {len(extracted)} files into {args.data_dir}")
    else:
        print(f"All files are already in {args.data_dir}; nothing to do.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
