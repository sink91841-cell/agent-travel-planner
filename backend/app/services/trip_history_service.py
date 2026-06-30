import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

from ..models.schemas import TripPlan, TripRequest


class TripHistoryService:
    def __init__(self, database_path: Path):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with closing(self._connect()) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS trip_history (
                    id TEXT PRIMARY KEY,
                    city TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    transportation TEXT NOT NULL,
                    accommodation TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    plan_json TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def create(self, request: TripRequest, plan: TripPlan) -> str:
        history_id = str(uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        with closing(self._connect()) as connection:
            connection.execute(
                """
                INSERT INTO trip_history (
                    id, city, start_date, end_date, transportation,
                    accommodation, created_at, updated_at, plan_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    history_id,
                    request.city,
                    request.start_date,
                    request.end_date,
                    request.transportation,
                    request.accommodation,
                    timestamp,
                    timestamp,
                    plan.model_dump_json(),
                ),
            )
            connection.commit()
        return history_id

    def list(self) -> list[dict[str, Any]]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                """
                SELECT id, city, start_date, end_date, transportation,
                       accommodation, created_at, updated_at
                FROM trip_history
                ORDER BY created_at DESC, rowid DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def get(self, history_id: str) -> Optional[dict[str, Any]]:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT * FROM trip_history WHERE id = ?",
                (history_id,),
            ).fetchone()
        if row is None:
            return None

        result = dict(row)
        result["plan"] = json.loads(result.pop("plan_json"))
        return result

    def update(self, history_id: str, plan: TripPlan) -> bool:
        timestamp = datetime.now(timezone.utc).isoformat()
        with closing(self._connect()) as connection:
            cursor = connection.execute(
                """
                UPDATE trip_history
                SET city = ?, start_date = ?, end_date = ?,
                    updated_at = ?, plan_json = ?
                WHERE id = ?
                """,
                (
                    plan.city,
                    plan.start_date,
                    plan.end_date,
                    timestamp,
                    plan.model_dump_json(),
                    history_id,
                ),
            )
            connection.commit()
            updated = cursor.rowcount > 0
        return updated

    def delete(self, history_id: str) -> bool:
        with closing(self._connect()) as connection:
            cursor = connection.execute(
                "DELETE FROM trip_history WHERE id = ?",
                (history_id,),
            )
            connection.commit()
            deleted = cursor.rowcount > 0
        return deleted


_history_service: Optional[TripHistoryService] = None


def get_trip_history_service() -> TripHistoryService:
    global _history_service
    if _history_service is None:
        database_path = (
            Path(__file__).resolve().parents[2] / "data" / "trip_history.db"
        )
        _history_service = TripHistoryService(database_path)
    return _history_service
