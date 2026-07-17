import json
import unittest

from career_compass import create_app
from career_compass.models import db, User


class CareerCompassApiTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            user = User(full_name="Test User", email="test@example.com", role="student")
            user.set_password("TestPass123")
            db.session.add(user)
            db.session.commit()
            self.user_id = user.id

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def login_and_get_token(self):
        response = self.client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "TestPass123"},
        )
        self.assertEqual(response.status_code, 200)
        return response.get_json()["token"]

    def test_register_endpoint(self):
        response = self.client.post(
            "/api/auth/register",
            json={
                "full_name": "Jane Doe",
                "email": "jane@example.com",
                "password": "StrongPass123",
                "confirm_password": "StrongPass123",
            },
        )
        self.assertEqual(response.status_code, 201)
        payload = response.get_json()
        self.assertIn("token", payload)
        self.assertEqual(payload["user"]["email"], "jane@example.com")

    def test_login_endpoint(self):
        token = self.login_and_get_token()
        self.assertTrue(token)

    def test_resume_analysis_endpoint(self):
        token = self.login_and_get_token()
        response = self.client.post(
            "/api/resume/analyze",
            json={"resume_text": "Managed product launches and increased revenue by 30%."},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("analysis", payload)
        self.assertIn("score", payload["analysis"])

    def test_chat_ask_endpoint(self):
        token = self.login_and_get_token()
        response = self.client.post(
            "/api/chat/ask",
            json={"question": "How do I improve my resume?"},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("answer", payload)


if __name__ == "__main__":
    unittest.main()
