from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from app.main import app
from app.services.geo_service import build_service


class GeoOptimizerTests(unittest.TestCase):
    def test_summary_shape(self) -> None:
        summary = build_service().summary()
        self.assertGreaterEqual(summary["articleCount"], 4)
        self.assertGreater(summary["averageGeoScore"], 0)

    def test_queue_prioritizes_weaker_content(self) -> None:
        queue = build_service().queue()
        self.assertLessEqual(queue[0]["geoScore"], queue[-1]["geoScore"])

    def test_api_article_lookup(self) -> None:
        client = TestClient(app)
        response = client.get("/api/articles/set-up-sso-for-your-workspace")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["category"], "Authentication")


if __name__ == "__main__":
    unittest.main()
