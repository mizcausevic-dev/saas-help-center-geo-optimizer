from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any


def _clamp(value: float, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, round(value)))


@dataclass(slots=True)
class HelpCenterGeoService:
    source_path: Path

    def load(self) -> dict[str, Any]:
        return json.loads(self.source_path.read_text(encoding="utf-8"))

    def score_article(self, article: dict[str, Any]) -> dict[str, Any]:
        heading_count = len(article.get("headings", []))
        entities = len(article.get("entity_mentions", []))
        faq_blocks = article.get("faq_blocks", 0)
        schema_types = set(article.get("schema_types", []))
        freshness_days = article.get("last_updated_days_ago", 0)
        sentence_count = len(article.get("body", []))

        entity_clarity = _clamp(40 + entities * 10)
        structure_readiness = _clamp(35 + heading_count * 12)
        faq_readiness = _clamp(30 + faq_blocks * 22)
        schema_readiness = _clamp(45 + len(schema_types) * 18 + (10 if "FAQPage" in schema_types else 0))
        citation_bait = _clamp(30 + sentence_count * 14 + (8 if "board" in " ".join(article.get("body", [])).lower() else 0))
        freshness = _clamp(100 - freshness_days * 0.32)

        geo_score = _clamp(
            entity_clarity * 0.2
            + structure_readiness * 0.2
            + faq_readiness * 0.16
            + schema_readiness * 0.16
            + citation_bait * 0.14
            + freshness * 0.14
        )

        fixes: list[str] = []
        if freshness_days > 90:
            fixes.append("Refresh article examples and timestamp to improve answer trust.")
        if faq_blocks < 2:
            fixes.append("Add explicit FAQ blocks to increase answer extraction quality.")
        if "FAQPage" not in schema_types:
            fixes.append("Publish FAQPage schema alongside the article payload.")
        if heading_count < 3:
            fixes.append("Expand heading structure so answer engines can isolate tasks and outcomes.")
        if entities < 4:
            fixes.append("Increase entity clarity with product, role, and integration names.")

        priority = "high" if geo_score < 65 else "medium" if geo_score < 80 else "watch"

        return {
            "slug": article["slug"],
            "title": article["title"],
            "category": article["category"],
            "url": article["url"],
            "geoScore": geo_score,
            "priority": priority,
            "entityClarity": entity_clarity,
            "structureReadiness": structure_readiness,
            "faqReadiness": faq_readiness,
            "schemaReadiness": schema_readiness,
            "citationBait": citation_bait,
            "freshness": freshness,
            "fixQueue": fixes,
        }

    def scored_articles(self) -> list[dict[str, Any]]:
        data = self.load()
        return sorted(
            [self.score_article(article) for article in data["articles"]],
            key=lambda item: (item["geoScore"], item["title"]),
        )

    def summary(self) -> dict[str, Any]:
        data = self.load()
        scored = self.scored_articles()
        avg_score = mean(article["geoScore"] for article in scored)
        high_priority = [article for article in scored if article["priority"] == "high"]
        faq_gaps = [article for article in scored if article["faqReadiness"] < 70]
        schema_gaps = [article for article in scored if article["schemaReadiness"] < 80]
        return {
            "brand": data["brand"],
            "platform": data["platform"],
            "articleCount": len(scored),
            "averageGeoScore": round(avg_score, 1),
            "highPriorityCount": len(high_priority),
            "faqGapCount": len(faq_gaps),
            "schemaGapCount": len(schema_gaps),
            "leadRecommendation": (
                "Prioritize stale authentication and analytics content first, then "
                "expand FAQ and schema coverage so AI answer systems can cite the help center directly."
            ),
        }

    def queue(self) -> list[dict[str, Any]]:
        return self.scored_articles()

    def article(self, slug: str) -> dict[str, Any] | None:
        for article in self.scored_articles():
            if article["slug"] == slug:
                return article
        return None

    def sample_payload(self) -> dict[str, Any]:
        queue = self.queue()
        return {
            "dashboard": self.summary(),
            "topFixes": [
                {
                    "slug": article["slug"],
                    "title": article["title"],
                    "geoScore": article["geoScore"],
                    "priority": article["priority"],
                    "nextAction": article["fixQueue"][0] if article["fixQueue"] else "Keep monitoring.",
                }
                for article in queue[:3]
            ],
        }


def build_service(root: Path | None = None) -> HelpCenterGeoService:
    base = root or Path(__file__).resolve().parents[2]
    return HelpCenterGeoService(base / "app" / "data" / "sample_help_center.json")
