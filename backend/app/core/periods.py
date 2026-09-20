"""Period boundary calculations in Asia/Tashkent timezone.

All six period types:
    all_time  — never rolls over
    daily     — midnight to midnight
    weekly    — Monday 00:00 to Sunday 23:59:59
    monthly   — 1st to last day of month
    seasonal  — meteorological: Dec–Feb, Mar–May, Jun–Aug, Sep–Nov
    yearly    — Jan 1 to Dec 31
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Tashkent")

PERIOD_TYPES = ("all_time", "daily", "weekly", "monthly", "seasonal", "yearly")

# Meteorological seasons (month -> (season_label, start_month, end_month))
_SEASON_MAP = {
    12: ("winter", 12, 2),
    1: ("winter", 12, 2),
    2: ("winter", 12, 2),
    3: ("spring", 3, 5),
    4: ("spring", 3, 5),
    5: ("spring", 3, 5),
    6: ("summer", 6, 8),
    7: ("summer", 6, 8),
    8: ("summer", 6, 8),
    9: ("autumn", 9, 11),
    10: ("autumn", 9, 11),
    11: ("autumn", 9, 11),
}


def now_tashkent() -> datetime:
    """Current UTC time converted to Asia/Tashkent."""
    return datetime.now(tz=TZ)


def _start_of_day(dt: datetime) -> datetime:
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def _end_of_day(dt: datetime) -> datetime:
    return dt.replace(hour=23, minute=59, second=59, microsecond=999999)


def get_period_bounds(period_type: str, ref: datetime | None = None) -> tuple[datetime, datetime | None, str]:
    """Return (starts_at, ends_at, period_key) in UTC for the period containing `ref`.

    `starts_at` and `ends_at` are timezone-aware UTC datetimes.
    `ends_at` is None only for all_time.
    """
    if ref is None:
        ref = now_tashkent()
    elif ref.tzinfo is None:
        ref = ref.replace(tzinfo=TZ)
    else:
        ref = ref.astimezone(TZ)

    if period_type == "all_time":
        epoch = datetime(2020, 1, 1, 0, 0, 0, tzinfo=TZ)
        return epoch.astimezone(timezone.utc), None, "all_time"

    if period_type == "daily":
        start = _start_of_day(ref)
        end = _end_of_day(ref)
        key = start.strftime("%Y-%m-%d")
        return start.astimezone(timezone.utc), end.astimezone(timezone.utc), key

    if period_type == "weekly":
        # Monday = 0
        monday = ref - timedelta(days=ref.weekday())
        start = _start_of_day(monday)
        end = _end_of_day(monday + timedelta(days=6))
        key = start.strftime("%Y-W%W")
        return start.astimezone(timezone.utc), end.astimezone(timezone.utc), key

    if period_type == "monthly":
        start = _start_of_day(ref.replace(day=1))
        # Last day: first day of next month minus 1 day
        if ref.month == 12:
            next_month = ref.replace(year=ref.year + 1, month=1, day=1)
        else:
            next_month = ref.replace(month=ref.month + 1, day=1)
        end = _end_of_day(next_month - timedelta(days=1))
        key = start.strftime("%Y-%m")
        return start.astimezone(timezone.utc), end.astimezone(timezone.utc), key

    if period_type == "seasonal":
        _, start_m, end_m = _SEASON_MAP[ref.month]
        if start_m > end_m:
            # Winter: Dec of this or prev year → Feb of next year
            if ref.month == 12:
                s_year = ref.year
                e_year = ref.year + 1
            else:
                s_year = ref.year - 1
                e_year = ref.year
            start = _start_of_day(datetime(s_year, 12, 1, tzinfo=TZ))
            import calendar
            last_day = calendar.monthrange(e_year, 2)[1]
            end = _end_of_day(datetime(e_year, 2, last_day, tzinfo=TZ))
        else:
            import calendar
            start = _start_of_day(datetime(ref.year, start_m, 1, tzinfo=TZ))
            last_day = calendar.monthrange(ref.year, end_m)[1]
            end = _end_of_day(datetime(ref.year, end_m, last_day, tzinfo=TZ))
        key = start.strftime("%Y-S%m")
        return start.astimezone(timezone.utc), end.astimezone(timezone.utc), key

    if period_type == "yearly":
        start = _start_of_day(datetime(ref.year, 1, 1, tzinfo=TZ))
        end = _end_of_day(datetime(ref.year, 12, 31, tzinfo=TZ))
        key = str(ref.year)
        return start.astimezone(timezone.utc), end.astimezone(timezone.utc), key

    raise ValueError(f"Unknown period_type: {period_type!r}")


def seconds_until_period_end(period_type: str, ref: datetime | None = None) -> int | None:
    """Seconds remaining in current period. None for all_time."""
    _, ends_at, _ = get_period_bounds(period_type, ref)
    if ends_at is None:
        return None
    now = (ref or now_tashkent()).astimezone(timezone.utc)
    delta = ends_at - now
    return max(0, int(delta.total_seconds()))
