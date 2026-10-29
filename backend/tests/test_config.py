"""Tests for the settings module and the CORS configuration."""

import unittest

from fastapi.testclient import TestClient

from app.config import PROJECT_ROOT, load_settings, settings
from app.main import app

HEALTH_URL = "/api/v1/health"


class TestLoadSettings(unittest.TestCase):

    def test_defaults_work_for_local_development(self):
        defaults = load_settings({})

        self.assertEqual(defaults.environment, "development")
        self.assertEqual(defaults.data_dir, PROJECT_ROOT / "data" / "raw")
        self.assertEqual(
            defaults.cors_origins,
            ["http://localhost:5173", "http://127.0.0.1:5173"],
        )
        self.assertEqual(defaults.log_level, "INFO")
        self.assertTrue(defaults.preload_data)

    def test_origins_are_split_and_cleaned(self):
        custom = load_settings({
            "OPSIQ_CORS_ORIGINS": " https://a.example/ , https://b.example,,",
        })

        self.assertEqual(
            custom.cors_origins,
            ["https://a.example", "https://b.example"],
        )

    def test_relative_data_dir_starts_at_project_root(self):
        custom = load_settings({"OPSIQ_DATA_DIR": "data/sample"})

        self.assertEqual(custom.data_dir, PROJECT_ROOT / "data" / "sample")

    def test_absolute_data_dir_is_kept(self):
        absolute = (PROJECT_ROOT / "elsewhere").resolve()

        custom = load_settings({"OPSIQ_DATA_DIR": str(absolute)})

        self.assertEqual(custom.data_dir, absolute)

    def test_log_level_is_upper_case(self):
        self.assertEqual(
            load_settings({"OPSIQ_LOG_LEVEL": "debug"}).log_level, "DEBUG"
        )

    def test_preload_can_be_turned_off(self):
        for value in ["false", "0", "no", "off", " FALSE "]:
            with self.subTest(value=value):
                custom = load_settings({"OPSIQ_PRELOAD_DATA": value})
                self.assertFalse(custom.preload_data)


class TestCors(unittest.TestCase):
    """The browser may only read responses for the allowed origins."""

    def setUp(self):
        self.client = TestClient(app)
        self.allowed_origin = settings.cors_origins[0]

    def test_allowed_origin_receives_cors_header(self):
        response = self.client.get(
            HEALTH_URL, headers={"Origin": self.allowed_origin}
        )

        self.assertEqual(
            response.headers.get("access-control-allow-origin"),
            self.allowed_origin,
        )

    def test_other_origin_receives_no_cors_header(self):
        response = self.client.get(
            HEALTH_URL, headers={"Origin": "https://not-allowed.example"}
        )

        self.assertNotIn("access-control-allow-origin", response.headers)

    def test_preflight_allows_get(self):
        response = self.client.options(
            HEALTH_URL,
            headers={
                "Origin": self.allowed_origin,
                "Access-Control-Request-Method": "GET",
            },
        )

        self.assertEqual(response.status_code, 200)

    def test_preflight_rejects_other_methods(self):
        response = self.client.options(
            HEALTH_URL,
            headers={
                "Origin": self.allowed_origin,
                "Access-Control-Request-Method": "DELETE",
            },
        )

        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
