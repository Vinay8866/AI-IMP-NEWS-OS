"""
AI IMP NEWS OS
Final Boss / QA Inspection Agent
Version: 2.0

Bottom-To-Top Verification Pipeline:
Stage 6 (Published/Ready) → Stage 5 (Image/SEO) → Stage 4 (Humanizer) → Stage 3 (Verify) → Stage 2 (Selector)

हर पोस्ट को अंतिम मन्जूरी (Approval) या रिजेक्शन (Rejection) देता है।
"""

from datetime import datetime
from pathlib import Path

from app.database.pipeline_repo import PipelineStagesRepository


class FinalBossQAAgent:
    """Final Quality Assurance Inspector Agent"""

    def __init__(self):
        self.stages_repo = PipelineStagesRepository()

    def inspect_article(self, article):
        """
        Bottom-To-Top Multi-Point Inspection
        """
        checks = []
        is_approved = True

        # Check 1: File Exists
        blog_file = article.get("blog_file", "")
        if blog_file and Path(blog_file).exists():
            checks.append("✅ Content File Exists")
        else:
            checks.append("❌ Missing Content File")
            is_approved = False

        # Check 2: Quality Score
        quality = article.get("quality_score", 0)
        if quality >= 70:
            checks.append(f"✅ Quality Score OK ({quality}/100)")
        else:
            checks.append(f"❌ Quality Score Low ({quality}/100)")
            is_approved = False

        # Check 3: Confidence Score
        confidence = article.get("confidence", 0)
        if confidence >= 50:
            checks.append(f"✅ Verification Confidence OK ({confidence}%)")
        else:
            checks.append(f"❌ Confidence Too Low ({confidence}%)")
            is_approved = False

        # Check 4: SEO Metadata
        slug = article.get("slug", "")
        meta_title = article.get("meta_title", "")
        if slug and meta_title:
            checks.append("✅ SEO Slug & Meta Title Ready")
        else:
            checks.append("❌ Missing SEO Metadata")
            is_approved = False

        # Check 5: Image Prompt & Asset
        image_prompt = article.get("image_prompt", "")
        if image_prompt:
            checks.append("✅ Image Prompt Generated")
        else:
            checks.append("❌ Missing Image Prompt")
            is_approved = False

        notes = " | ".join(checks)
        return is_approved, notes

    def run(self):
        today = datetime.now().strftime("%Y-%m-%d")

        print("\n" + "=" * 60)
        print("👑 FINAL BOSS / QA INSPECTION AGENT")
        print("=" * 60)
        print("Performing Bottom-To-Top Quality Inspection...")
        print("-" * 60)

        journey = self.stages_repo.get_journey(today)

        if not journey:
            print("⚠️  No journey records found for today. Run full pipeline first.")
            print("=" * 60)
            return []

        approved_count = 0
        rejected_count = 0

        for item in journey:
            idx = item["news_index"]
            title = item.get("title", "Untitled")

            approved, notes = self.inspect_article(item)

            self.stages_repo.update_qa(
                run_date=today,
                news_index=idx,
                approved=approved,
                notes=notes
            )

            status_str = "🏆 APPROVED" if approved else "🛑 REJECTED"
            if approved:
                approved_count += 1
            else:
                rejected_count += 1

            print(f"\n--- Inspection #{idx:02d}: {title[:50]}... ---")
            print(f"  Decision: {status_str}")
            print(f"  Notes   : {notes}")

        print("\n" + "=" * 60)
        print(f"👑 FINAL BOSS QA SUMMARY: {approved_count} Approved | {rejected_count} Rejected")
        print("=" * 60)

        return journey


if __name__ == "__main__":
    qa = FinalBossQAAgent()
    qa.run()