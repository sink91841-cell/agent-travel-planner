import unittest

from app.agents.trip_planner_agent import MultiAgentTripPlanner
from app.models.schemas import TripRequest


class AttractionQueryTests(unittest.TestCase):
    def setUp(self):
        self.planner = MultiAgentTripPlanner.__new__(MultiAgentTripPlanner)

    def make_request(self, preferences):
        return TripRequest(
            city="秦皇岛",
            start_date="2026-07-01",
            end_date="2026-07-01",
            travel_days=1,
            transportation="公共交通",
            accommodation="经济型酒店",
            preferences=preferences,
            free_text_input="",
        )

    def test_food_preference_does_not_become_attraction_keyword(self):
        query = self.planner._build_attraction_query(self.make_request(["美食"]))

        self.assertIn("热门旅游景点", query)
        self.assertNotIn("美食相关景点", query)
        self.assertIn("排除餐馆", query)

    def test_attraction_preference_is_selected_from_mixed_preferences(self):
        query = self.planner._build_attraction_query(
            self.make_request(["美食", "自然风光"])
        )

        self.assertIn("自然风光", query)
        self.assertNotIn("美食相关景点", query)

    def test_planner_prompt_keeps_dining_out_of_attractions(self):
        query = self.planner._build_planner_query(
            self.make_request(["美食"]),
            attractions="景点搜索结果",
            weather="天气结果",
            hotels="酒店结果",
        )

        self.assertIn("餐馆、小吃店和美食街不得放入 attractions", query)


if __name__ == "__main__":
    unittest.main()
