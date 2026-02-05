import tempfile
import unittest
from pathlib import Path

from app import Database, StatsService


class StatsServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "test.db"
        self.db = Database(self.db_path)
        self.service = StatsService(self.db)
        self._seed()

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def _seed(self) -> None:
        with self.db.connect() as conn:
            conn.execute("INSERT INTO users(username, display_name) VALUES ('u1','User 1')")
            conn.execute("INSERT INTO drink_types(name, brand, default_abv) VALUES ('Beer','Asahi',0.05)")
            conn.execute("INSERT INTO drink_types(name, brand, default_abv) VALUES ('Whisky','Nikka',0.4)")
            conn.execute(
                """
                INSERT INTO drink_records(user_id, drink_type, abv, volume_ml, count, drank_at, source_image, recognized_payload)
                VALUES (1, 1, 0.05, 500, 2, datetime('now','-1 day'), 'beer.jpg', '{"score":0.9}')
                """
            )
            conn.execute(
                """
                INSERT INTO drink_records(user_id, drink_type, abv, volume_ml, count, drank_at, source_image, recognized_payload)
                VALUES (1, 2, 0.40, 45, 1, datetime('now'), 'whisky.jpg', '{"score":0.8}')
                """
            )
            conn.commit()

    def test_consumption_has_totals_and_trend(self) -> None:
        result = self.service.consumption(user_id=1, range_name="week")
        self.assertIn("totals", result)
        self.assertGreater(result["totals"]["volume_ml"], 0)
        self.assertGreater(len(result["trend"]), 0)

    def test_favorites_returns_ranked_types(self) -> None:
        result = self.service.favorites(user_id=1, top_n=2)
        self.assertEqual(result["top_n"], 2)
        self.assertEqual(result["favorites"][0]["drink_type"], "Beer")


if __name__ == "__main__":
    unittest.main()
