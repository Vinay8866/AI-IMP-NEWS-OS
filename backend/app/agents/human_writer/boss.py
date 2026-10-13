"""
AI IMP NEWS OS
Human Writer Boss
Version: 2.0

Stage 4 + Stage 5:
- Evidence files padho
- Hook + Story + Fact + Tone + CTA
- SEO + Image
- Content files save
- pipeline_stages update
"""

import json
from datetime import datetime
from pathlib import Path

from app.agents.human_writer.hook_agent import generate_hook
from app.agents.human_writer.story_agent import write_story
from app.agents.human_writer.fact_agent import fact_check
from app.agents.human_writer.tone_agent import improve_tone
from app.agents.human_writer.cta_agent import generate_cta
from app.agents.seo.seo_agent import SEOAgent
from app.agents.image_gen.image_agent import ImageAgent
from app.database.pipeline_repo import PipelineStagesRepository
from app.config.settings import (
    EVIDENCE_DIR, CONTENT_DIR,
    QUALITY_PUBLISH_THRESHOLD, QUALITY_REWRITE_THRESHOLD
)


class HumanWriterBoss:
    def __init__(self):
        self.stages_repo = PipelineStagesRepository()
        self.seo_agent = SEOAgent()
        self.image_agent = ImageAgent()

    def _load_verification(self, today, index):
        path = EVIDENCE_DIR / today / f"news_{index:03d}" / "verification.json"
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _quality_score(self, confidence, fact_result, hook, story):
        """0-100 quality"""
        score = 0
        score += min(40, int(confidence * 0.4))          # max 40 from confidence
        score += int(fact_result.get("score", 0) * 0.3)  # max 30 from facts
        score += 10 if hook and len(hook) > 20 else 0
        score += 10 if story and len(story) > 120 else 0
        score += 10 if story and len(story.split()) > 80 else 0
        return max(0, min(100, score))

    def run(self):
        today = datetime.now().strftime("%Y-%m-%d")

        print("\n" + "=" * 60)
        print("✍️  HUMAN WRITER BOSS - Stage 4+5")
        print("=" * 60)

        results = []

        for index in range(1, 7):
            print(f"\n--- Writing #{index:02d} ---")
            verification = self._load_verification(today, index)

            if not verification:
                print(f"  ⚠️  evidence missing for news_{index:03d}")
                print("     Pehle verify agent chalao.")
                results.append({
                    "title": f"News {index} (Missing Evidence)",
                    "hook": "",
                    "story": "",
                    "confidence": 0,
                    "quality": 0,
                    "decision": "REWRITE_QUEUE",
                    "file": "",
                    "source": "",
                    "category": ""
                })
                continue

            title = verification.get("title", f"News {index}")
            summary = verification.get("summary", "")
            source = verification.get("source", "")
            category = verification.get("category", "")
            confidence = verification.get("confidence", 0)

            # 1) Hook
            hook = generate_hook(title, summary)
            hook = improve_tone(hook)
            print(f"  🎣 Hook: {hook[:70]}...")

            # 2) Story
            story = write_story(title, verification)
            story = improve_tone(story)

            # 3) CTA
            cta = generate_cta(category)
            full_story = f"{story}\n\n{cta}"

            # 4) Fact check
            fact_result = fact_check(verification)
            print(f"  🧪 Fact score: {fact_result['score']} | passed={fact_result['passed']}")

            # 5) Quality + decision
            quality = self._quality_score(confidence, fact_result, hook, full_story)
            if quality >= QUALITY_PUBLISH_THRESHOLD:
                decision = "PUBLISH_QUEUE"
            elif quality >= QUALITY_REWRITE_THRESHOLD:
                decision = "REWRITE_QUEUE"
            else:
                decision = "REWRITE_QUEUE"

            print(f"  ⭐ Quality: {quality}/100 | Decision: {decision}")

            # 6) SEO
            seo_data = self.seo_agent.generate(title, hook, full_story)
            slug = seo_data["slug"]
            print(f"  🔍 Slug: {slug}")

            # 7) Image
            image_result = self.image_agent.generate(title, slug=slug, category=category)
            print(f"  🎨 Image: {image_result['status']}")

            # 8) Save content files
            content_folder = CONTENT_DIR / today / f"news_{index:03d}"
            content_folder.mkdir(parents=True, exist_ok=True)

            blog_file = content_folder / "blog.md"
            blog_text = (
                f"# {title}\n\n"
                f"**Hook:** {hook}\n\n"
                f"{full_story}\n\n"
                f"---\n"
                f"*Source: {source} | Confidence: {confidence}% | Quality: {quality}/100 | Decision: {decision}*\n"
            )
            with open(blog_file, "w", encoding="utf-8") as f:
                f.write(blog_text)

            # Save SEO json
            with open(content_folder / "seo.json", "w", encoding="utf-8") as f:
                json.dump(seo_data, f, indent=2, ensure_ascii=False)

            # Save image prompt
            with open(content_folder / "image_prompt.txt", "w", encoding="utf-8") as f:
                f.write(image_result["prompt"])

            # Save meta
            with open(content_folder / "meta.json", "w", encoding="utf-8") as f:
                json.dump({
                    "title": title,
                    "hook": hook,
                    "quality": quality,
                    "decision": decision,
                    "confidence": confidence,
                    "slug": slug,
                    "image_status": image_result["status"],
                    "image_path": image_result["path"],
                    "fact_check": fact_result
                }, f, indent=2, ensure_ascii=False)

            # 9) Update pipeline stages DB
            self.stages_repo.update_humanized(
                run_date=today,
                news_index=index,
                hook=hook,
                story=full_story[:2000],
                quality_score=quality,
                decision=decision,
                blog_file=str(blog_file)
            )

            self.stages_repo.update_image_seo(
                run_date=today,
                news_index=index,
                image_prompt=image_result["prompt"],
                image_status=image_result["status"],
                image_path=image_result["path"],
                slug=slug,
                meta_title=seo_data.get("meta_title", "")
            )

                        # Save to OutputRepository for Publish Queue
            from app.database.repository import OutputRepository
            out_repo = OutputRepository()
            out_repo.save(
                run_date=today,
                news_index=index,
                result={
                    "title": title,
                    "hook": hook,
                    "confidence": confidence,
                    "quality": quality,
                    "decision": decision,
                    "file": str(blog_file),
                    "source": source,
                    "category": category
                },
                seo_data=seo_data
            )

            result = {
                "title": title,
                "hook": hook,
                "story": full_story,
                "confidence": confidence,
                "quality": quality,
                "decision": decision,
                "file": str(blog_file),
                "source": source,
                "category": category,
                "slug": slug,
                "seo": seo_data,
                "image": image_result
            }
            results.append(result)
            print(f"  💾 Saved: {blog_file}")

        print("\n" + "=" * 60)
        print(f"✍️  HUMAN WRITER COMPLETE: {len(results)} articles")
        print("=" * 60)
        return results


if __name__ == "__main__":
    boss = HumanWriterBoss()
    output = boss.run()
    print("\nSummary:")
    for i, item in enumerate(output, 1):
        print(f"  {i}. Q={item['quality']} | {item['decision']} | {item['title'][:45]}")