"""
AI IMP NEWS OS - FastAPI Routes
Version: 3.0 Buffer Edition - All Routes + Social Buffer Routes
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.database.db import get_connection
from app.database.repository import OutputRepository, NewsRepository
from app.database.pipeline_repo import PipelineStagesRepository
from app.database.social_repo import SocialScheduleRepository
from app.services.social.publisher import SocialPublisher

router = APIRouter()


# ==========================
# EXISTING ROUTES
# ==========================
@router.get("/stats")
def get_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM news_articles")
    raw_news_count = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as total FROM pipeline_stages")
    pipeline_total = cursor.fetchone()["total"]

    cursor.execute("""
    SELECT run_date,
           COUNT(*) as total,
           SUM(CASE WHEN decision='PUBLISH_QUEUE' THEN 1 ELSE 0 END) as publish_count,
           SUM(CASE WHEN decision='REWRITE_QUEUE' THEN 1 ELSE 0 END) as rewrite_count,
           AVG(quality_score) as avg_quality,
           AVG(confidence) as avg_confidence
    FROM articles_output
    WHERE run_date = (SELECT MAX(run_date) FROM articles_output)
    GROUP BY run_date
    """)
    latest_run = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) as total FROM articles_output WHERE publish_status='published'")
    published_count = cursor.fetchone()["total"]

    # Social stats
    try:
        cursor.execute("SELECT status, COUNT(*) as cnt FROM social_schedule GROUP BY status")
        social_rows = cursor.fetchall()
        social_stats = {r["status"]: r["cnt"] for r in social_rows}
    except:
        social_stats = {}

    conn.close()

    if latest_run:
        summary = dict(latest_run)
    else:
        summary = {
            "run_date": None,
            "total": 0,
            "publish_count": 0,
            "rewrite_count": 0,
            "avg_quality": 0,
            "avg_confidence": 0
        }

    return {
        "raw_news": raw_news_count,
        "pipeline_total": pipeline_total,
        "published_total": published_count,
        "latest_run": summary,
        "social": {
            "queued": social_stats.get("queued", 0),
            "scheduled": social_stats.get("scheduled", 0),
            "posted": social_stats.get("posted", 0),
            "failed": social_stats.get("failed", 0),
            "total": sum(social_stats.values())
        }
    }


@router.get("/queue")
def get_queue():
    repo = OutputRepository()
    publish_queue = repo.get_publish_queue()
    rewrite_queue = repo.get_rewrite_queue()
    return {
        "publish_queue": publish_queue,
        "rewrite_queue": rewrite_queue, # keeping compat
        "publish_count": len(publish_queue),
        "rewrite_count": len(rewrite_queue),
        "publish": publish_queue,
        "rewrite": rewrite_queue
    }


@router.get("/pipeline")
def get_pipeline_status():
    repo = PipelineStagesRepository()
    latest_date = repo.get_latest_run_date()
    if not latest_date:
        return {"run_date": None, "journey": [], "counts": {}}

    journey = repo.get_journey(latest_date)
    counts = repo.count_by_stage(latest_date)

    return {
        "run_date": latest_date,
        "journey": journey,
        "counts": counts
    }


# ===== JOURNEY ROUTES =====
@router.get("/journey/dates")
def get_journey_dates(limit: int = 30):
    repo = PipelineStagesRepository()
    dates = repo.get_all_dates(limit=limit)
    return {"dates": dates}


@router.get("/journey/latest/full")
def get_latest_journey_full():
    repo = PipelineStagesRepository()
    latest_date = repo.get_latest_run_date()
    if not latest_date:
        return {"run_date": None, "journey": []}

    journey = repo.get_journey(latest_date)
    return {"run_date": latest_date, "journey": journey}


@router.get("/journey/{run_date}")
def get_journey_by_date(run_date: str):
    if run_date == "latest":
        return get_latest_journey_full()

    repo = PipelineStagesRepository()
    journey = repo.get_journey(run_date)
    if not journey:
        raise HTTPException(status_code=404, detail=f"No journey found for {run_date}")

    counts = repo.count_by_stage(run_date)
    return {"run_date": run_date, "journey": journey, "counts": counts}


# @router.get("/journey/raw-news")
# def get_raw_news(limit: int = 50):
#     repo = NewsRepository()
#     latest = repo.latest(limit=limit)
#     return {"news": latest, "count": len(latest)}

@router.get("/raw-news")
def get_raw_news(limit: int = 50):
    repo = NewsRepository()
    articles = repo.latest(limit=limit)

    return {
        "raw_news": articles,
        "news": articles,
        "count": len(articles),
        "total": repo.count()
    }


@router.get("/analytics/summary")
def get_analytics_summary(days: int = 7):
    repo = OutputRepository()
    runs = repo.get_all_runs(days=days)
    return {"days": days, "runs": runs}


@router.post("/run-pipeline")
def trigger_pipeline():
    from app.main import run_pipeline
    try:
        result = run_pipeline()
        return {"status": "success", "message": "Pipeline completed", "result": str(result)[:500]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================
# BUFFER CLONE - SOCIAL ROUTES (NEW)
# ==========================

class ScheduleRequest(BaseModel):
    article_id: int
    caption: Optional[str] = None
    platforms: Optional[List[str]] = None
    scheduled_at: Optional[str] = None  # "2025-01-20 13:00:00"


class UpdateCaptionRequest(BaseModel):
    caption: str
    platforms: Optional[List[str]] = None


class RescheduleRequest(BaseModel):
    scheduled_at: str  # "2025-01-20 19:00:00"


@router.get("/social/queue")
def get_social_queue(status: Optional[str] = None, limit: int = 50):
    """Buffer Queue - All posts"""
    repo = SocialScheduleRepository()
    queue = repo.get_queue(status=status, limit=limit)
    counts = repo.count_by_status()
    # Parse platforms JSON for frontend
    for item in queue:
        try:
            import json
            item["platforms_list"] = json.loads(item["platforms"]) if isinstance(item["platforms"], str) else item["platforms"]
        except:
            item["platforms_list"] = ["facebook"]
    return {"queue": queue, "counts": counts, "count": len(queue)}


@router.get("/social/calendar")
def get_social_calendar(days: int = 7):
    """Buffer Calendar View - Next N days"""
    repo = SocialScheduleRepository()
    calendar = repo.get_calendar(days=days)
    return {"calendar": calendar, "days": days}


@router.get("/social/stats")
def get_social_stats():
    repo = SocialScheduleRepository()
    counts = repo.count_by_status()
    return counts


@router.post("/social/schedule")
def schedule_social_post(req: ScheduleRequest):
    """Manually schedule an article from Publish Queue to Social Queue"""
    # Get article
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM articles_output WHERE id = ?", (req.article_id,))
    article = cursor.fetchone()
    conn.close()

    if not article:
        raise HTTPException(status_code=404, detail=f"Article ID {req.article_id} not found")

    article_dict = dict(article)
    repo = SocialScheduleRepository()

    # Check duplicate
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as cnt FROM social_schedule WHERE article_id = ?", (req.article_id,))
    exists = cursor.fetchone()["cnt"] > 0
    conn.close()

    if exists:
        # Allow re-schedule? For now block
        raise HTTPException(status_code=400, detail="Already scheduled in social queue")

    post_id = repo.save_from_article(
        article_output_row=article_dict,
        caption=req.caption,
        platforms=req.platforms,
        scheduled_at=req.scheduled_at
    )

    if not post_id:
        raise HTTPException(status_code=500, detail="Failed to schedule")

    return {"status": "success", "post_id": post_id, "message": f"Scheduled as ID {post_id}"}


@router.put("/social/{post_id}/caption")
def update_social_caption(post_id: int, req: UpdateCaptionRequest):
    repo = SocialScheduleRepository()
    try:
        repo.update_caption(post_id, req.caption, platforms=req.platforms)
        return {"status": "success", "message": "Caption updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/social/{post_id}/reschedule")
def reschedule_social_post(post_id: int, req: RescheduleRequest):
    repo = SocialScheduleRepository()
    try:
        repo.reschedule(post_id, req.scheduled_at)
        return {"status": "success", "message": f"Rescheduled to {req.scheduled_at}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/social/{post_id}/post-now")
def post_social_now(post_id: int):
    """Buffer 'Post Now' - Instant publish"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM social_schedule WHERE id = ?", (post_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Social post not found")

    social_row = dict(row)
    publisher = SocialPublisher()

    try:
        result = publisher.publish(social_row)
        if result.get("success"):
            repo = SocialScheduleRepository()
            fb_id = result.get("results", {}).get("facebook")
            ig_id = result.get("results", {}).get("instagram")
            status = "simulated" if result.get("mode") == "mock" else "posted"
            repo.update_status(
                post_id,
                status,
                fb_post_id=str(fb_id) if fb_id else None,
                ig_post_id=str(ig_id) if ig_id else None
            )
            return {"status": "success", "result": result}
        else:
            repo = SocialScheduleRepository()
            repo.update_status(post_id, "failed", error=result.get("error"))
            raise HTTPException(status_code=500, detail=result.get("error"))
    except Exception as e:
        repo = SocialScheduleRepository()
        repo.update_status(post_id, "failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/social/{post_id}")
def delete_social_post(post_id: int):
    repo = SocialScheduleRepository()
    repo.delete(post_id)
    return {"status": "success", "message": f"Deleted post {post_id}"}


@router.post("/social/auto-schedule-all")
def auto_schedule_all_from_publish_queue():
    """One-click: Take all publish_queue and push to social queue"""
    from app.database.repository import OutputRepository

    output_repo = OutputRepository()
    publish_queue = output_repo.get_social_candidates()

    if not publish_queue:
        return {"status": "success", "scheduled": 0, "message": "No eligible published articles to schedule"}

    social_repo = SocialScheduleRepository()
    scheduled = 0
    skipped = 0

    for article in publish_queue:
        # Check exists
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM social_schedule WHERE article_id = ?", (article["id"],))
        exists = cursor.fetchone()["cnt"] > 0
        conn.close()

        if exists:
            skipped += 1
            continue

        post_id = social_repo.save_from_article(article)
        if post_id:
            scheduled += 1

    return {
        "status": "success",
        "scheduled": scheduled,
        "skipped": skipped,
        "message": f"Scheduled {scheduled} new posts, skipped {skipped} already scheduled"
    }
