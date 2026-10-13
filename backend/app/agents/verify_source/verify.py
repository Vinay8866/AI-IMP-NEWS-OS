"""
AI IMP NEWS OS
Verify Source Agent
Version: 2.0

Stage 2+3:
- IMP Selector से top 6 लेता है
- Verify करता है
- pipeline_stages DB में save करता है
- evidence files बनाता है
"""

import json
from datetime import datetime
from pathlib import Path

from app.agents.imp_news.selector import IMPNewsSelector
from app.agents.verify_source.claims import extract_claims
from app.agents.verify_source.evidence import find_evidence
from app.agents.verify_source.confidence import calculate_confidence
from app.database.pipeline_repo import PipelineStagesRepository
from app.config.settings import EVIDENCE_DIR


class VerifySourceAgent:
    """Verification Agent"""

    def __init__(self):
        self.selector = IMPNewsSelector()
        self.stages_repo = PipelineStagesRepository()

    def run(self):
        """
        Full verification pipeline:
        1. Select top 6
        2. Extract claims
        3. Gather evidence
        4. Calculate confidence
        5. Save to DB + files
        """
        today = datetime.now().strftime("%Y-%m-%d")

        print("\n" + "=" * 60)
        print("✅ VERIFY SOURCE AGENT - Stage 2+3")
        print("=" * 60)

        # Step 1: Get top news
        top_news = self.selector.top_news()

        if not top_news:
            print("⚠️  No news to verify. Run collector first.")
            return []

        # Clear previous run for today
        self.stages_repo.clear_run(today)

        results = []

        for index, news in enumerate(top_news, start=1):
            print(f"\n--- Verifying #{index}: {news['title'][:50]}... ---")

            # Stage 2: Save as selected
            self.stages_repo.create_selected(
                run_date=today,
                news_index=index,
                title=news.get("title", ""),
                source=news.get("source", ""),
                category=news.get("category", ""),
                link=news.get("link", ""),
                summary=news.get("summary", ""),
                image=news.get("image") or "",
                raw_score=news.get("score", 0),
                imp_score=news.get("score", 0)
            )

            # Extract claims
            claims_data = extract_claims(news)

            # Gather evidence
            evidence = find_evidence(news, claims_data)

            # Calculate confidence
            confidence = calculate_confidence(evidence)

            # Stage 3: Update verified
            claims_str = claims_data.get("claims_text", "")
            self.stages_repo.update_verified(
                run_date=today,
                news_index=index,
                confidence=confidence,
                claims_keywords=claims_str,
                verification_run_id=f"run_{today}_{index:03d}"
            )

            # Save evidence file
            evidence_folder = EVIDENCE_DIR / today / f"news_{index:03d}"
            evidence_folder.mkdir(parents=True, exist_ok=True)

            evidence_file = evidence_folder / "verification.json"
            verification_data = {
                "title": news.get("title", ""),
                "source": news.get("source", ""),
                "category": news.get("category", ""),
                "link": news.get("link", ""),
                "summary": news.get("summary", ""),
                "image": news.get("image"),
                "score": news.get("score", 0),
                "confidence": confidence,
                "claims": claims_data.get("claims", []),
                "keywords": claims_data.get("keywords", []),
                "evidence": evidence,
                "verified_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            with open(evidence_file, "w", encoding="utf-8") as f:
                json.dump(verification_data, f, indent=2, ensure_ascii=False)

            # Status label
            if confidence >= 70:
                status = "HIGH ✅"
            elif confidence >= 40:
                status = "MEDIUM ⚠️"
            else:
                status = "LOW ❌"

            print(f"  Confidence: {confidence}% ({status})")
            print(f"  Claims: {len(claims_data.get('claims', []))}")
            print(f"  Saved: {evidence_file}")

            # Add to results
            news["confidence"] = confidence
            news["claims"] = claims_data
            news["evidence"] = evidence
            news["news_index"] = index
            results.append(news)

        print("\n" + "=" * 60)
        print(f"✅ VERIFICATION COMPLETE: {len(results)} articles")
        print(f"📁 Evidence saved to: {EVIDENCE_DIR / today}")
        print("=" * 60)

        return results


if __name__ == "__main__":
    agent = VerifySourceAgent()
    results = agent.run()
    print(f"\n🎉 Done! {len(results)} articles verified")