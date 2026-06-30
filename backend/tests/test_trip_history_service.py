import tempfile
import unittest
from pathlib import Path

from app.models.schemas import TripPlan, TripRequest
from app.services.trip_history_service import TripHistoryService


class TripHistoryServiceTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = (
            Path(self.temp_dir.name) / "nested" / "trip_history.db"
        )
        self.service = TripHistoryService(self.database_path)
        self.request = TripRequest(
            city="秦皇岛",
            start_date="2026-07-08",
            end_date="2026-07-10",
            travel_days=3,
            transportation="公共交通",
            accommodation="经济型酒店",
            preferences=["历史文化"],
            free_text_input="",
        )
        self.plan = TripPlan.model_validate(
            {
                "city": "秦皇岛",
                "start_date": "2026-07-08",
                "end_date": "2026-07-10",
                "days": [],
                "weather_info": [],
                "overall_suggestions": "注意防晒",
                "budget": None,
            }
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create_get_update_and_delete_history(self):
        self.assertTrue(self.database_path.exists())

        history_id = self.service.create(self.request, self.plan)

        detail = self.service.get(history_id)
        self.assertIsNotNone(detail)
        self.assertEqual(detail["id"], history_id)
        self.assertEqual(detail["city"], "秦皇岛")
        self.assertEqual(detail["transportation"], "公共交通")
        self.assertEqual(detail["accommodation"], "经济型酒店")
        self.assertEqual(detail["plan"]["overall_suggestions"], "注意防晒")
        self.assertNotIn("plan_json", detail)

        updated_plan = self.plan.model_copy(
            update={
                "city": "北京",
                "start_date": "2026-08-01",
                "end_date": "2026-08-02",
                "overall_suggestions": "携带雨具",
            }
        )
        self.assertTrue(self.service.update(history_id, updated_plan))

        updated_detail = self.service.get(history_id)
        self.assertEqual(updated_detail["city"], "北京")
        self.assertEqual(updated_detail["start_date"], "2026-08-01")
        self.assertEqual(updated_detail["end_date"], "2026-08-02")
        self.assertEqual(
            updated_detail["plan"]["overall_suggestions"],
            "携带雨具",
        )
        self.assertFalse(self.service.update("missing-id", updated_plan))

        self.assertTrue(self.service.delete(history_id))
        self.assertIsNone(self.service.get(history_id))
        self.assertFalse(self.service.delete(history_id))

    def test_list_orders_quick_creates_newest_first(self):
        first_id = self.service.create(self.request, self.plan)
        second_id = self.service.create(self.request, self.plan)

        records = self.service.list()

        self.assertEqual(
            [record["id"] for record in records],
            [second_id, first_id],
        )
        self.assertNotIn("plan_json", records[0])
        self.assertNotIn("plan", records[0])


if __name__ == "__main__":
    unittest.main()
