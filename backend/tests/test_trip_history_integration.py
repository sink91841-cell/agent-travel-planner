import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.api.main import app
from app.api.routes import trip
from app.models.schemas import TripPlan
from app.services.trip_history_service import TripHistoryService


class TripHistoryIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.history_service = TripHistoryService(
            Path(self.temp_dir.name) / "trip_history.db"
        )
        self.plan = TripPlan(
            city="秦皇岛",
            start_date="2026-07-08",
            end_date="2026-07-10",
            days=[],
            weather_info=[],
            overall_suggestions="测试计划",
            budget=None,
        )
        self.agent = Mock()
        self.agent.plan_trip.return_value = self.plan
        app.dependency_overrides[trip.get_planner] = lambda: self.agent
        app.dependency_overrides[
            trip.get_history_service
        ] = lambda: self.history_service
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.pop(trip.get_planner, None)
        app.dependency_overrides.pop(trip.get_history_service, None)
        self.temp_dir.cleanup()

    def test_plan_response_contains_saved_history_id(self):
        with unittest.mock.patch("builtins.print"):
            response = self.client.post(
                "/api/trip/plan",
                json={
                    "city": "秦皇岛",
                    "start_date": "2026-07-08",
                    "end_date": "2026-07-10",
                    "travel_days": 3,
                    "transportation": "公共交通",
                    "accommodation": "经济型酒店",
                    "preferences": [],
                    "free_text_input": "",
                },
            )

        self.assertEqual(response.status_code, 200)
        history_id = response.json()["history_id"]
        saved = self.history_service.get(history_id)
        self.assertIsNotNone(saved)
        self.assertEqual(saved["plan"]["overall_suggestions"], "测试计划")
        self.agent.plan_trip.assert_called_once()


if __name__ == "__main__":
    unittest.main()
