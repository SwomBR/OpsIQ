import unittest

from fastapi.testclient import TestClient

from app.main import app


class TestApiEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_returns_200(self):
        response = self.client.get("/api/v1/health")

        self.assertEqual(response.status_code, 200)

    def test_health_returns_app_name_and_status(self):
        response = self.client.get("/api/v1/health")

        self.assertEqual(response.json(), {"app": "OpsIQ", "status": "healthy"})

    def test_root_returns_200(self):
        response = self.client.get("/api/v1/")

        self.assertEqual(response.status_code, 200)

    def test_root_returns_welcome_message_and_docs_link(self):
        response = self.client.get("/api/v1/")
        body = response.json()

        self.assertIn("OpsIQ", body["message"])
        self.assertEqual(body["docs"], "/docs")

    def test_docs_page_is_available(self):
        response = self.client.get("/docs")

        self.assertEqual(response.status_code, 200)

    def test_invalid_path_returns_404(self):
        response = self.client.get("/api/v1/does-not-exist")

        self.assertEqual(response.status_code, 404)

    def test_unknown_top_level_path_returns_404(self):
        response = self.client.get("/not-a-real-page")

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
