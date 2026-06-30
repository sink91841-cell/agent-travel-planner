import unittest

from app.api.main import app
from app.config import get_settings


class BrandingTest(unittest.TestCase):
    def test_backend_uses_smart_travel_assistant_brand(self):
        settings = get_settings()

        self.assertEqual(settings.app_name, "智能旅行助手")
        self.assertEqual(app.title, "智能旅行助手")
        self.assertNotIn("HelloAgents", app.description)


if __name__ == "__main__":
    unittest.main()
