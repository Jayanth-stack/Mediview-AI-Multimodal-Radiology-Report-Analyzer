from __future__ import annotations

import unittest
from datetime import timedelta

from jose import jwt

from app.core import security
from app.core.config import settings


class SecurityTests(unittest.TestCase):
    def test_create_access_token_contains_subject(self):
        token = security.create_access_token("123", expires_delta=timedelta(minutes=5))
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        self.assertEqual(payload["sub"], "123")
        self.assertIn("exp", payload)

    def test_verify_password_roundtrip(self):
        hashed = security.get_password_hash("strong-password")
        self.assertTrue(security.verify_password("strong-password", hashed))

    def test_verify_password_rejects_incorrect_password(self):
        hashed = security.get_password_hash("strong-password")
        self.assertFalse(security.verify_password("wrong-password", hashed))


if __name__ == "__main__":
    unittest.main()

