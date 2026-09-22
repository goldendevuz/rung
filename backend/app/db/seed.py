"""Demo seed data — reproduces the prototype's demo data exactly.

Run when SEED_DEMO=true (idempotent: safe to call multiple times).

Prototype channels (slug, name, handle, category_slug, subscribers,
clickthroughs, verified, claimed, grad_start, grad_end,
per-period paid B: a=all_time d=daily w=weekly m=monthly y=yearly;
missing key = no entry in that period):

 1. kodlash_uz      Kodlash.uz         @kodlash_uz      dasturlash  84200  1289  True  True   #2563EB #1E3A8A  a=25 d=5 w=12 m=20 y=22
 2. aibiz           AI Biz             @aibiz_uz        ai          31400   847  True  True   #7C3AED #4C1D95  a=18 d=4 w=9  m=14 y=16
 3. startupuz       Startup Uzbekistan @startupuz       biznes      22100   612  True  True   #059669 #064E3B  a=15 d=3 w=7  m=11 y=13
 4. techuz          Tech Uzbekistan    @techuz          texnologiya 18600   534  True  True   #D97706 #92400E  a=12 d=2 w=5  m=9  y=11
 5. designuz        Design UZ          @designuz_uz     dizayn      14200   423  True  True   #DB2777 #831843  a=9  d=2 w=4  m=7  y=9
 6. kriptauz        Kripta UZ          @kripta_uz       moliya      12800   398  True  True   #0891B2 #164E63  a=8  d=1 w=3  m=6  y=8
 7. gaminguz        Gaming UZ          @gaminguz        oyinlar     11500   367  False True   #4F46E5 #1E1B4B  a=7  d=1 w=3  m=5  y=7
 8. mobiluz         Mobil UZ           @mobiluz         mobil       10200   312  False True   #16A34A #14532D  a=6  d=1 w=2  m=4  y=6
 9. ecomuz          E-commerce UZ      @ecomuz          ecommerce   9100    287  False True   #EA580C #7C2D12  a=5  w=2  m=3  y=5
10. saasuz          SaaS UZ            @saasuz          saas        8400    241  False True   #7C6CFF #3730A3  a=4  w=2  m=3  y=4
11. markaztv        Markaz TV          @markaztv        marketing   7200    198  False True   #0EA5E9 #075985  a=3  w=1  m=2  y=3
12. devtoolsuz      Dev Tools UZ       @devtoolsuz      devtools    6100    167  False True   #8B5CF6 #4C1D95  a=2  w=1  m=2  y=2
13. eduuz           Edu UZ             @eduuz           talim       5200    143  False True   #10B981 #064E3B  a=2  w=1  m=1  y=2
14. produz          Prod UZ            @produz          mahsuldorlik 4100   118  False True   #F59E0B #78350F  a=1  m=1  y=1
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.periods import TZ, get_period_bounds, now_tashkent
from app.db.session import async_session_factory
from app.models.board import Board, BoardEntry
from app.models.category import Category
from app.models.listing import Listing
from app.models.setting import Setting
from app.models.stats import ListingStatsDaily

logger = logging.getLogger(__name__)

# ── Categories (13 from prototype) ────────────────────────────────────────────
CATEGORIES = [
    {"slug": "ai",           "name_uz": "AI va agentlar",      "color": "#7C3AED", "icon": "🤖", "sort_order": 1},
    {"slug": "saas",         "name_uz": "SaaS",                "color": "#7C6CFF", "icon": "☁️", "sort_order": 2},
    {"slug": "marketing",    "name_uz": "Marketing",           "color": "#0EA5E9", "icon": "📢", "sort_order": 3},
    {"slug": "devtools",     "name_uz": "Dev Tools",           "color": "#8B5CF6", "icon": "🔧", "sort_order": 4},
    {"slug": "talim",        "name_uz": "Ta'lim",              "color": "#10B981", "icon": "📚", "sort_order": 5},
    {"slug": "moliya",       "name_uz": "Moliya",              "color": "#0891B2", "icon": "💰", "sort_order": 6},
    {"slug": "ecommerce",    "name_uz": "E-tijorat",           "color": "#EA580C", "icon": "🛍️", "sort_order": 7},
    {"slug": "oyinlar",      "name_uz": "O'yinlar",            "color": "#4F46E5", "icon": "🎮", "sort_order": 8},
    {"slug": "mobil",        "name_uz": "Mobil",               "color": "#16A34A", "icon": "📱", "sort_order": 9},
    {"slug": "mahsuldorlik", "name_uz": "Mahsuldorlik",        "color": "#F59E0B", "icon": "⚡", "sort_order": 10},
    {"slug": "dizayn",       "name_uz": "Dizayn",              "color": "#DB2777", "icon": "🎨", "sort_order": 11},
    {"slug": "dasturlash",   "name_uz": "Dasturlash",          "color": "#2563EB", "icon": "💻", "sort_order": 12},
    {"slug": "texnologiya",  "name_uz": "Texnologiya",         "color": "#D97706", "icon": "⚙️", "sort_order": 13},
]

# ── Channels ──────────────────────────────────────────────────────────────────
# per-period paid B: keys a/d/w/m/y
CHANNELS = [
    {
        "id": "7fe75ed1-6fe9-5414-b2a0-385d71a5e190", "handle": "@kodlash_uz", "name": "Kodlash.uz",
        "category": "dasturlash", "subscribers": 84200, "clicks": 1289,
        "verified": True, "claimed": True,
        "g": ["#2563EB", "#1E3A8A"],
        "paid": {"a": 25, "d": 5, "w": 12, "m": 20, "y": 22},
        "desc": "O'zbekistondagi eng yirik dasturlash kanali. Har kuni dasturlash, veb-ishlanma, mobil ilovalar va sun'iy intellekt sohalari boyicha qiziqarli maqolalar va darslar chop etiladi. Python, JavaScript, TypeScript, Go va boshqa zamonaviy texnologiyalar boyicha bilimlaringizni oshiring. 84 000 dan ortiq obunachilar hamjamiyatida tajribali mutaxassislar va yangi boshlovchilar birga suhbatlashadi va bilim ulashadi. Rung platformasida birinchi orinni egallagan, O'zbekiston IT ekotizimining yetakchi kanali.",
        "age_days": 120,
    },
    {
        "id": "728951dd-2168-5bc1-bbca-e3ec280f7336", "handle": "@aibiz_uz", "name": "AI Biz",
        "category": "ai", "subscribers": 31400, "clicks": 847,
        "verified": True, "claimed": True,
        "g": ["#7C3AED", "#4C1D95"],
        "paid": {"a": 18, "d": 4, "w": 9, "m": 14, "y": 16},
        "desc": "Sun'iy intellekt va biznes haqida.",
        "age_days": 95,
    },
    {
        "id": "a9a9caca-3a6a-5cf3-b466-cae37e8a126c", "handle": "@startupuz", "name": "Startup Uzbekistan",
        "category": "saas", "subscribers": 22100, "clicks": 612,
        "verified": True, "claimed": True,
        "g": ["#059669", "#064E3B"],
        "paid": {"a": 15, "d": 3, "w": 7, "m": 11, "y": 13},
        "desc": "O'zbekiston startap ekotizimlari haqida.",
        "age_days": 80,
    },
    {
        "id": "b6a39eda-50d4-50c9-a007-4d7d21f35998", "handle": "@techuz", "name": "Tech Uzbekistan",
        "category": "texnologiya", "subscribers": 18600, "clicks": 534,
        "verified": True, "claimed": True,
        "g": ["#D97706", "#92400E"],
        "paid": {"a": 12, "d": 2, "w": 5, "m": 9, "y": 11},
        "desc": "O'zbekistondagi texnologiyalar yangiliklari.",
        "age_days": 75,
    },
    {
        "id": "0eab0f21-c108-5dcd-b274-14678908bb57", "handle": "@designuz_uz", "name": "Design UZ",
        "category": "dizayn", "subscribers": 14200, "clicks": 423,
        "verified": True, "claimed": True,
        "g": ["#DB2777", "#831843"],
        "paid": {"a": 9, "d": 2, "w": 4, "m": 7, "y": 9},
        "desc": "Dizayn va kreativlik haqida kanal.",
        "age_days": 65,
    },
    {
        "id": "38636031-9940-50d5-85ab-2589713cda98", "handle": "@kripta_uz", "name": "Kripta UZ",
        "category": "moliya", "subscribers": 12800, "clicks": 398,
        "verified": True, "claimed": True,
        "g": ["#0891B2", "#164E63"],
        "paid": {"a": 8, "d": 1, "w": 3, "m": 6, "y": 8},
        "desc": "Kripto valyutalar va moliyaviy texnologiyalar.",
        "age_days": 60,
    },
    {
        "id": "edca1ca7-86e0-595d-8adc-a5ea39eb5285", "handle": "@gaminguz", "name": "Gaming UZ",
        "category": "oyinlar", "subscribers": 11500, "clicks": 367,
        "verified": False, "claimed": True,
        "g": ["#4F46E5", "#1E1B4B"],
        "paid": {"a": 7, "d": 1, "w": 3, "m": 5, "y": 7},
        "desc": "O'yin yangiliklari va tahlillari.",
        "age_days": 55,
    },
    {
        "id": "4697f261-7e50-58b6-a1ea-f76c96492286", "handle": "@mobiluz", "name": "Mobil UZ",
        "category": "mobil", "subscribers": 10200, "clicks": 312,
        "verified": False, "claimed": True,
        "g": ["#16A34A", "#14532D"],
        "paid": {"a": 6, "d": 1, "w": 2, "m": 4, "y": 6},
        "desc": "Mobil ilovalar va gadjetlar haqida.",
        "age_days": 50,
    },
    {
        "id": "b4aa2863-bde9-54eb-bc37-b600fe99fc30", "handle": "@ecomuz", "name": "E-commerce UZ",
        "category": "ecommerce", "subscribers": 9100, "clicks": 287,
        "verified": False, "claimed": True,
        "g": ["#EA580C", "#7C2D12"],
        "paid": {"a": 5, "w": 2, "m": 3, "y": 5},
        "desc": "O'zbekistonda onlayn savdo.",
        "age_days": 45,
    },
    {
        "id": "15188b58-2859-5b2e-88ab-e3f5343e269c", "handle": "@saasuz", "name": "SaaS UZ",
        "category": "saas", "subscribers": 8400, "clicks": 241,
        "verified": False, "claimed": True,
        "g": ["#7C6CFF", "#3730A3"],
        "paid": {"a": 4, "w": 2, "m": 3, "y": 4},
        "desc": "B2B va SaaS mahsulotlari haqida.",
        "age_days": 40,
    },
    {
        "id": "229be3ef-d6d0-5d94-8d12-6be2c70975cc", "handle": "@markaztv", "name": "Markaz TV",
        "category": "marketing", "subscribers": 7200, "clicks": 198,
        "verified": False, "claimed": True,
        "g": ["#0EA5E9", "#075985"],
        "paid": {"a": 3, "w": 1, "m": 2, "y": 3},
        "desc": "Marketing va reklama sohasida.",
        "age_days": 35,
    },
    {
        "id": "8625895a-77b3-5a7e-bcad-0c2f47b3f905", "handle": "@devtoolsuz", "name": "Dev Tools UZ",
        "category": "devtools", "subscribers": 6100, "clicks": 167,
        "verified": False, "claimed": True,
        "g": ["#8B5CF6", "#4C1D95"],
        "paid": {"a": 2, "w": 1, "m": 2, "y": 2},
        "desc": "Ishlab chiquvchilar uchun qurollar.",
        "age_days": 30,
    },
    {
        "id": "563ffc96-f636-5aaf-b2d9-5df80e8eb2ee", "handle": "@eduuz", "name": "Edu UZ",
        "category": "talim", "subscribers": 5200, "clicks": 143,
        "verified": False, "claimed": True,
        "g": ["#10B981", "#064E3B"],
        "paid": {"a": 2, "w": 1, "m": 1, "y": 2},
        "desc": "Ta'lim va onlayn kurslar.",
        "age_days": 25,
    },
    {
        "id": "c1894ca0-eeee-5ce9-b132-42bd359d5e34", "handle": "@produz", "name": "Prod UZ",
        "category": "mahsuldorlik", "subscribers": 4100, "clicks": 118,
        "verified": False, "claimed": True,
        "g": ["#F59E0B", "#78350F"],
        "paid": {"a": 1, "m": 1, "y": 1},
        "desc": "Mahsuldorlik va shaxsiy rivojlanish.",
        "age_days": 20,
    },
]

# Free catalog (not in any paid board)
FREE_CHANNELS = [
    {
        "id": "aa7f21fe-cbb6-59ce-bd64-19ff07d65eec", "handle": "@rung_uz", "name": "Rung jamoasi",
        "category": "texnologiya", "subscribers": 0, "clicks": 0,
        "verified": True, "claimed": True,
        "g": ["#B8F03C", "#4D6B08"],
        "free_label": "Rung jamoasi",
        "desc": "Rung platformasining rasmiy kanali.",
        "age_days": 200,
    },
    {
        "id": "9122c5d2-bd6d-5082-b128-39c3d5e8a397", "handle": "@anon_kanal", "name": "Noma'lum kanal",
        "category": "texnologiya", "subscribers": 1200, "clicks": 45,
        "verified": False, "claimed": False,
        "g": ["#6D7679", "#3A4147"],
        "free_label": "Egasi tasdiqlanmagan",
        "desc": "Egasi tasdiqlanmagan kanal namunasi.",
        "age_days": 10,
    },
]

# period key short → period_type
PERIOD_KEY_MAP = {"a": "all_time", "d": "daily", "w": "weekly", "m": "monthly", "y": "yearly"}


async def _get_or_create_board(
    session: AsyncSession,
    period_type: str,
    ref: datetime | None = None,
) -> Board:
    starts_at, ends_at, period_key = get_period_bounds(period_type, ref)
    result = await session.execute(
        select(Board).where(Board.period_type == period_type, Board.period_key == period_key)
    )
    board = result.scalar_one_or_none()
    if board is None:
        board = Board(
            period_type=period_type,
            period_key=period_key,
            starts_at=starts_at,
            ends_at=ends_at,
            status="active",
        )
        session.add(board)
        await session.flush()
    return board


async def seed_reference() -> None:
    """Seed reference data (13 categories + settings). Always runs on deploy, idempotent."""
    async with async_session_factory() as session:
        async with session.begin():
            await _seed_categories(session)
            await _seed_settings(session)
    logger.info("Reference seed complete.")


async def seed_demo() -> None:
    """Seed demo listings and boards. Only when SEED_DEMO=true, idempotent."""
    async with async_session_factory() as session:
        async with session.begin():
            await _seed_listings(session)

        async with session.begin():
            await _seed_boards_and_entries(session)

        async with session.begin():
            await _seed_closed_daily_boards(session)

    logger.info("Demo seed complete.")


async def run_seed() -> None:
    """Idempotent seed — kept for backward-compat (make seed). Runs both phases."""
    await seed_reference()
    await seed_demo()
    logger.info("Full seed complete.")


async def _seed_categories(session: AsyncSession) -> None:
    for cat in CATEGORIES:
        exists = (
            await session.execute(select(Category).where(Category.slug == cat["slug"]))
        ).scalar_one_or_none()
        if exists is None:
            session.add(Category(**cat))
    await session.flush()


async def _seed_settings(session: AsyncSession) -> None:
    defaults = [
        ("floor_b", "1", "Minimum price to enter any board (whole B)"),
        ("min_step_b", "1", "Minimum overbid step (whole B)"),
        ("b_unit_uzs", "1000", "1 B in UZS (informational)"),
    ]
    for key, value, desc in defaults:
        exists = (
            await session.execute(select(Setting).where(Setting.key == key))
        ).scalar_one_or_none()
        if exists is None:
            session.add(Setting(key=key, value=value, description=desc))
    await session.flush()


async def _get_category_id(session: AsyncSession, slug: str) -> str | None:
    result = await session.execute(select(Category).where(Category.slug == slug))
    cat = result.scalar_one_or_none()
    return cat.id if cat else None


async def _seed_listings(session: AsyncSession) -> None:
    ref_now = now_tashkent()

    for ch in CHANNELS + FREE_CHANNELS:
        exists = (
            await session.execute(select(Listing).where(Listing.id == ch["id"]))
        ).scalar_one_or_none()
        if exists is not None:
            continue

        cat_id = await _get_category_id(session, ch["category"])
        age = timedelta(days=ch["age_days"])
        created = (ref_now - age).astimezone(timezone.utc)

        listing = Listing(
            id=ch["id"],
            kind="channel",
            handle=ch["handle"],
            name=ch["name"],
            description=ch.get("desc"),
            category_id=cat_id,
            subscribers=ch["subscribers"],
            verified=ch["verified"],
            claimed=ch["claimed"],
            status="active",
            free_label=ch.get("free_label"),
            gradient_start=ch["g"][0],
            gradient_end=ch["g"][1],
            created_at=created,
        )
        session.add(listing)
        await session.flush()

        # Seed click-through stats for today
        if ch["clicks"] > 0:
            today = ref_now.date()
            stat_exists = (
                await session.execute(
                    select(ListingStatsDaily).where(
                        ListingStatsDaily.listing_id == listing.id,
                        ListingStatsDaily.stat_date == today,
                    )
                )
            ).scalar_one_or_none()
            if stat_exists is None:
                session.add(
                    ListingStatsDaily(
                        listing_id=listing.id,
                        stat_date=today,
                        clickthroughs=ch["clicks"],
                    )
                )


async def _seed_boards_and_entries(session: AsyncSession) -> None:
    """Create current period boards and add entries for paid channels."""
    ref_now = now_tashkent()

    for ch in CHANNELS:
        listing_result = await session.execute(
            select(Listing).where(Listing.id == ch["id"])
        )
        listing = listing_result.scalar_one_or_none()
        if listing is None:
            continue

        for period_short, b_amount in ch["paid"].items():
            period_type = PERIOD_KEY_MAP.get(period_short)
            if period_type is None:
                continue

            board = await _get_or_create_board(session, period_type, ref_now)
            paid_units = b_amount * 1000  # 1 B = 1000 units

            # Check if entry already exists
            entry_exists = (
                await session.execute(
                    select(BoardEntry).where(
                        BoardEntry.board_id == board.id,
                        BoardEntry.listing_id == listing.id,
                        BoardEntry.status == "active",
                    )
                )
            ).scalar_one_or_none()

            if entry_exists is None:
                # Stagger entered_at by rank position for tie-break predictability
                rank_idx = CHANNELS.index(ch)
                entered_at = (ref_now - timedelta(hours=24 - rank_idx)).astimezone(timezone.utc)
                session.add(
                    BoardEntry(
                        board_id=board.id,
                        listing_id=listing.id,
                        paid_units=paid_units,
                        entered_at=entered_at,
                        status="active",
                    )
                )

    await session.flush()


async def _seed_closed_daily_boards(session: AsyncSession) -> None:
    """Seed two previous daily boards (closed) with top-3 entries for the history page."""
    ref_now = now_tashkent()

    for days_ago in [1, 2]:
        ref = ref_now - timedelta(days=days_ago)
        _, _, period_key = get_period_bounds("daily", ref)
        starts_at, ends_at, _ = get_period_bounds("daily", ref)

        exists = (
            await session.execute(
                select(Board).where(Board.period_type == "daily", Board.period_key == period_key)
            )
        ).scalar_one_or_none()
        if exists is not None:
            continue

        closed_board = Board(
            period_type="daily",
            period_key=period_key,
            starts_at=starts_at,
            ends_at=ends_at,
            status="closed",
        )
        session.add(closed_board)
        await session.flush()

        # Add top 3 channels for this closed board
        for i, ch in enumerate(CHANNELS[:3]):
            listing_result = await session.execute(
                select(Listing).where(Listing.id == ch["id"])
            )
            listing = listing_result.scalar_one_or_none()
            if listing is None:
                continue

            b_amount = ch["paid"].get("d", 3 - i)
            entered_at = (ref - timedelta(hours=12 - i)).astimezone(timezone.utc)
            session.add(
                BoardEntry(
                    board_id=closed_board.id,
                    listing_id=listing.id,
                    paid_units=b_amount * 1000,
                    entered_at=entered_at,
                    status="active",
                )
            )

    await session.flush()


if __name__ == "__main__":
    asyncio.run(run_seed())
