"""
OpsIQ - Business Operations Intelligence Platform

Module: test_download_data.py

Purpose:
    Test the dataset download helper without using the network.
    A small zip file stands in for the Kaggle archive.
"""

import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from src import download_data


class TestDownloadData(unittest.TestCase):

    def setUp(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.folder = Path(temp_dir.name)
        self.data_dir = self.folder / "data"

    def make_archive(self, names):
        archive_path = self.folder / "archive.zip"
        with zipfile.ZipFile(archive_path, "w") as archive:
            for name in names:
                archive.writestr(name, f"contents of {name}\n")
        return archive_path

    def test_extracts_only_the_requested_files(self):
        archive = self.make_archive(
            download_data.REQUIRED_FILES + ["olist_geolocation_dataset.csv"]
        )

        download_data.extract_files(
            archive, self.data_dir, download_data.REQUIRED_FILES
        )

        self.assertEqual(
            sorted(path.name for path in self.data_dir.iterdir()),
            sorted(download_data.REQUIRED_FILES),
        )

    def test_entries_outside_the_folder_are_never_written(self):
        archive = self.make_archive(
            download_data.REQUIRED_FILES + ["../escaped.csv"]
        )

        download_data.extract_files(
            archive, self.data_dir, download_data.REQUIRED_FILES
        )

        self.assertFalse((self.folder / "escaped.csv").exists())

    def test_incomplete_archive_raises(self):
        archive = self.make_archive(["olist_orders_dataset.csv"])

        with self.assertRaisesRegex(ValueError, "missing"):
            download_data.extract_files(
                archive, self.data_dir, download_data.REQUIRED_FILES
            )

    def test_does_not_download_when_files_exist(self):
        self.data_dir.mkdir()
        for name in download_data.REQUIRED_FILES:
            (self.data_dir / name).write_text("x", encoding="utf-8")

        with patch.object(download_data.urllib.request, "urlopen") as urlopen:
            extracted = download_data.download_dataset(self.data_dir)

        self.assertEqual(extracted, [])
        urlopen.assert_not_called()

    def test_download_failure_returns_error_code(self):
        with patch.object(
            download_data.urllib.request,
            "urlopen",
            side_effect=OSError("network down"),
        ):
            with patch("sys.stdout"):
                exit_code = download_data.main(["--data-dir", str(self.data_dir)])

        self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()
