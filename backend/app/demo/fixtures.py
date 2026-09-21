"""In-memory fixtures for demo mode."""
import math
from datetime import datetime, timezone, timedelta

from app.db.seed import CATEGORIES, CHANNELS, FREE_CHANNELS, PERIOD_KEY_MAP
from app.core.periods import get_period_bounds, now_tashkent, seconds_until_period_end
from app.core.money import units_to_b_display

def _format_listing(ch: dict, clickthroughs: int = 0) -> dict:
    return {
        "slug": ch["slug"],
        "handle": ch["handle"],
        "name": ch["name"],
        "description": ch.get("desc"),
        "category_slug": ch["category"],
        "category_color": next((c["color"] for c in CATEGORIES if c["slug"] == ch["category"]), None),
        "subscribers": ch["subscribers"],
        "verified": ch["verified"],
        "claimed": ch["claimed"],
        "free_label": ch.get("free_label"),
        "gradient_start": ch["g"][0],
        "gradient_end": ch["g"][1],
        "clickthroughs": clickthroughs,
        "created_at": (now_tashkent() - timedelta(days=ch["age_days"])).isoformat()
    }

def get_demo_categories() -> list[dict]:
    res = []
    for c in CATEGORIES:
        count = sum(1 for ch in CHANNELS + FREE_CHANNELS if ch["category"] == c["slug"])
        res.append({
            "slug": c["slug"],
            "name_uz": c["name_uz"],
            "color": c["color"],
            "icon": c["icon"],
            "listing_count": count
        })
    return res

def get_demo_stats() -> dict:
    return {
        "total_listings": len(CHANNELS) + len(FREE_CHANNELS),
        "total_entries": len(CHANNELS) * 4,  # roughly
        "online_now": None,
        "visits_today": None,
        "total_paid_units": 150000
    }

def get_demo_tabs() -> list[dict]:
    tabs = []
    ref = now_tashkent()
    for period_short, period_type in PERIOD_KEY_MAP.items():
        _, ends_at, _ = get_period_bounds(period_type, ref)
        count = sum(1 for ch in CHANNELS if period_short in ch["paid"])
        if count > 0:
            tabs.append({
                "period_type": period_type,
                "active_count": count,
                "ends_at": ends_at.isoformat() if ends_at else None,
                "seconds_remaining": seconds_until_period_end(period_type, ref)
            })
    return tabs

def get_demo_board_current(period_type: str, page: int = 1, category: str = None, q: str = None) -> dict:
    ref = now_tashkent()
    _, _, period_key = get_period_bounds(period_type, ref)
    period_short = next((k for k, v in PERIOD_KEY_MAP.items() if v == period_type), None)
    
    entries = []
    for ch in CHANNELS:
        if period_short in ch["paid"]:
            if category and ch["category"] != category:
                continue
            if q and q.lower() not in ch["name"].lower() and q.lower() not in ch["handle"].lower():
                continue
            paid_units = ch["paid"][period_short] * 1000
            entries.append({
                "listing": ch,
                "paid_units": paid_units
            })
    
    # Sort by paid DESC
    entries.sort(key=lambda e: e["paid_units"], reverse=True)
    
    total = len(entries)
    page_size = 12
    offset = (page - 1) * page_size
    entries_page = entries[offset:offset + page_size]
    
    entry_outs = []
    for idx, e in enumerate(entries_page):
        rank = offset + idx + 1
        entry_outs.append({
            "rank": rank,
            "listing": _format_listing(e["listing"], e["listing"]["clicks"]),
            "paid_b": units_to_b_display(e["paid_units"]),
            "paid_units": e["paid_units"],
            "entered_at": (ref - timedelta(hours=24 - rank)).isoformat()
        })
        
    return {
        "period_type": period_type,
        "period_key": period_key,
        "board_id": 999,
        "entries": entry_outs,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, math.ceil(total / page_size))
    }

def get_demo_daily_history() -> list[dict]:
    ref_now = now_tashkent()
    history = []
    for days_ago in [1, 2]:
        ref = ref_now - timedelta(days=days_ago)
        _, ends_at, period_key = get_period_bounds("daily", ref)
        
        top3 = []
        for i, ch in enumerate(CHANNELS[:3]):
            b_amount = ch["paid"].get("d", 3 - i)
            top3.append({
                "rank": i + 1,
                "listing": _format_listing(ch, ch["clicks"]),
                "paid_b": units_to_b_display(b_amount * 1000),
                "paid_units": b_amount * 1000,
                "entered_at": (ref - timedelta(hours=12 - i)).isoformat()
            })
        
        history.append({
            "period_key": period_key,
            "ends_at": ends_at.isoformat() if ends_at else None,
            "top3": top3
        })
    return history
