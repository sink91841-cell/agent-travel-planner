import asyncio
import inspect
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from app.api.main import app, startup_event
from app.api.routes.history import (
    delete_history,
    get_history,
    get_history_service,
    list_history,
    update_history,
)
from app.models.schemas import (
    TripHistoryDetailResponse,
    TripHistoryListResponse,
    TripPlan,
    TripRequest,
)
from app.services.trip_history_service import TripHistoryService


class HistoryApiTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        database_path = Path(self.temp_dir.name) / "trip_history.db"
        self.service = TripHistoryService(database_path)
        app.dependency_overrides[get_history_service] = lambda: self.service
        self.client = TestClient(app)

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
        self.plan = TripPlan(
            city="秦皇岛",
            start_date="2026-07-08",
            end_date="2026-07-10",
            days=[],
            weather_info=[],
            overall_suggestions="注意防晒",
            budget=None,
        )

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.pop(get_history_service, None)
        self.temp_dir.cleanup()

    def test_list_empty_history_returns_200(self):
        response = self.client.get("/api/history")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "success": True,
                "message": "获取历史记录成功",
                "data": [],
            },
        )

    def test_get_unknown_history_returns_404(self):
        response = self.client.get("/api/history/missing-id")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "历史记录不存在")

    def test_get_update_and_delete_history(self):
        history_id = self.service.create(self.request, self.plan)

        get_response = self.client.get(f"/api/history/{history_id}")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json()["data"]["id"], history_id)
        self.assertEqual(
            get_response.json()["data"]["plan"]["overall_suggestions"],
            "注意防晒",
        )

        updated_plan = self.plan.model_copy(
            update={
                "city": "北京",
                "start_date": "2026-08-01",
                "end_date": "2026-08-02",
                "overall_suggestions": "携带雨具",
            }
        )
        update_response = self.client.put(
            f"/api/history/{history_id}",
            json={"plan": updated_plan.model_dump()},
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json()["data"]["city"], "北京")
        self.assertEqual(
            update_response.json()["data"]["plan"]["overall_suggestions"],
            "携带雨具",
        )

        delete_response = self.client.delete(f"/api/history/{history_id}")
        self.assertEqual(delete_response.status_code, 204)
        self.assertEqual(delete_response.content, b"")
        self.assertIsNone(self.service.get(history_id))

    def test_update_and_delete_unknown_history_return_404(self):
        update_response = self.client.put(
            "/api/history/missing-id",
            json={"plan": self.plan.model_dump()},
        )
        delete_response = self.client.delete("/api/history/missing-id")

        self.assertEqual(update_response.status_code, 404)
        self.assertEqual(
            update_response.json()["detail"],
            "历史记录不存在",
        )
        self.assertEqual(delete_response.status_code, 404)
        self.assertEqual(
            delete_response.json()["detail"],
            "历史记录不存在",
        )

    def test_database_errors_return_safe_chinese_message(self):
        failing_service = Mock(spec=TripHistoryService)
        failing_service.list.side_effect = sqlite3.OperationalError(
            "sensitive database path"
        )
        failing_service.delete.side_effect = sqlite3.OperationalError(
            "sensitive database path"
        )
        app.dependency_overrides[get_history_service] = lambda: failing_service

        list_response = self.client.get("/api/history")
        delete_response = self.client.delete("/api/history/history-id")

        self.assertEqual(list_response.status_code, 500)
        self.assertEqual(
            list_response.json()["detail"],
            "历史记录服务暂时不可用",
        )
        self.assertNotIn("sensitive", list_response.text)
        self.assertEqual(delete_response.status_code, 500)
        self.assertEqual(
            delete_response.json()["detail"],
            "历史记录服务暂时不可用",
        )

    def test_history_handlers_are_synchronous_for_sqlite_calls(self):
        handlers = [list_history, get_history, update_history, delete_history]

        self.assertTrue(
            all(not inspect.iscoroutinefunction(handler) for handler in handlers)
        )


class HistoryResponseModelTest(unittest.TestCase):
    def test_list_response_defaults_success_to_true(self):
        response = TripHistoryListResponse()

        self.assertTrue(response.success)

    def test_detail_response_defaults_success_to_true(self):
        response = TripHistoryDetailResponse(
            data={
                "id": "history-id",
                "city": "秦皇岛",
                "start_date": "2026-07-08",
                "end_date": "2026-07-10",
                "transportation": "公共交通",
                "accommodation": "经济型酒店",
                "created_at": "2026-06-29T00:00:00+00:00",
                "updated_at": "2026-06-29T00:00:00+00:00",
                "plan": {
                    "city": "秦皇岛",
                    "start_date": "2026-07-08",
                    "end_date": "2026-07-10",
                    "days": [],
                    "weather_info": [],
                    "overall_suggestions": "注意防晒",
                    "budget": None,
                },
            }
        )

        self.assertTrue(response.success)


class HistoryStartupTest(unittest.TestCase):
    def test_history_initialization_failure_stops_startup_immediately(self):
        history_service = Mock()
        history_service.initialize.side_effect = RuntimeError("数据库不可用")

        with (
            patch(
                "app.api.main.get_trip_history_service",
                return_value=history_service,
            ),
            patch("app.api.main.print_config") as print_config,
            patch("app.api.main.validate_config") as validate_config,
        ):
            with self.assertRaisesRegex(RuntimeError, "数据库不可用"):
                asyncio.run(startup_event())

        history_service.initialize.assert_called_once_with()
        print_config.assert_not_called()
        validate_config.assert_not_called()

    def test_test_client_context_runs_startup_initialization(self):
        history_service = Mock()

        with (
            patch(
                "app.api.main.get_trip_history_service",
                return_value=history_service,
            ),
            patch("app.api.main.print_config"),
            patch("app.api.main.validate_config"),
            patch("builtins.print"),
            TestClient(app),
        ):
            pass

        history_service.initialize.assert_called_once_with()

    def test_backend_start_script_forces_utf8_python_output(self):
        script_path = Path(__file__).resolve().parents[2] / "start-backend.ps1"
        script = script_path.read_text(encoding="utf-8")

        self.assertIn("$env:PYTHONIOENCODING", script)
        self.assertIn('"utf-8"', script)


if __name__ == "__main__":
    unittest.main()
