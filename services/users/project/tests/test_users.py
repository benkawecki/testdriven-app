# services/users/project/tests/test_users.py


import json
import unittest
from project import db
from project.api.models import User
from project.tests.base import BaseTestCase


def add_user(username, email):
    user = User(username=username, email=email)
    db.session.add(user)
    db.session.commit()
    return user


class TestUserService(BaseTestCase):
    """ Tests for the Users Service"""

    def test_add_user(self):
        """Ensure a new user can be added to the database"""
        with self.client:
            response = self.client.post(
                "/users",
                data=json.dumps({"username": "michael", "email": "michael@herman.org"}),
                content_type="application/json",
            )
            data = json.loads(response.data.decode())
            self.assertTrue(response.status_code, 201)
            self.assertIn("michael@herman.org was added!", data["message"])
            self.assertIn("success", data["status"])

    def test_add_user_invalid_json(self):
        """Ensure error is thrown if json is invalid"""
        with self.client:
            response = self.client.post(
                "/users", data=json.dumps({}), content_type="application/json"
            )
            data = json.loads(response.data.decode())
            self.assertTrue(response.status_code, 400)
            self.assertIn("invalid payload", data["message"])
            self.assertIn("fail", data["status"])
        pass

    def test_add_user_invalid_json_keys(self):
        """Ensure error is thrown is both fields are not included"""
        with self.client:
            response = self.client.post(
                "/users",
                data=json.dumps({"email": "michael@herman.org"}),
                content_type="application/json",
            )
            data = json.loads(response.data.decode())
            self.assertTrue(response.status_code, 400)
            self.assertIn("invalid payload", data["message"])
            self.assertIn("fail", data["status"])

    def test_add_user_duplicate_email(self):
        """Ensure and error is thrown if the user is already in the database"""
        with self.client:
            self.client.post(
                "/users",
                data=json.dumps({"username": "michael", "email": "michael@herman.org"}),
                content_type="application/json",
            )
            response = self.client.post(
                "/users",
                data=json.dumps({"username": "michael", "email": "michael@herman.org"}),
                content_type="application/json",
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Sorry. That email already exists.", data["message"])
            self.assertIn("fail", data["status"])

    def test_add_single_user(self):
        """Ensure get single behaves correctly"""
        user = add_user(username="michael", email="michael@herman.org")

        with self.client:
            response = self.client.get(f"/users/{user.id}")
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn("michael", data["data"]["username"])
            self.assertIn("michael@herman.org", data["data"]["email"])
            self.assertIn("success", data["status"])

    def test_single_user_no_id(self):
        """Ensure error is thrown if an id is not provided"""
        with self.client:
            response = self.client.get(f"/users/blah")
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("User does not exist.", data["message"])
            self.assertIn("fail", data["status"])

    def test_single_user_incorrect_id(self):
        """Ensure and error is thrown if an incorrect id is provided"""
        with self.client:
            response = self.client.get(f"/users/999")
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("User does not exist.", data["message"])
            self.assertIn("fail", data["status"])

    def test_all_users(self):
        """Ensure all user behavior functions correctly"""
        add_user(username="michael", email="michael@herman.org")
        add_user(username="ken", email="ken@bawecki.com")
        with self.client:
            response = self.client.get("/users")
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn("michael", data["data"]["users"][0]["username"])
            self.assertIn("michael@herman", data["data"]["users"][0]["email"])
            self.assertIn("ken", data["data"]["users"][1]["username"])
            self.assertIn("ken@bawecki.com", data["data"]["users"][1]["email"])
            self.assertIn("success", data["status"])

    def test_users(self):
        """ensure the /ping route behanves correctly"""
        response = self.client.get("/users/ping")
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn("pong", data["message"])
        self.assertIn("success", data["status"])


if __name__ == "__main__":
    unittest.main()
