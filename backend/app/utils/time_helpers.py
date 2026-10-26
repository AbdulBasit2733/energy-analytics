from datetime import date, datetime, timedelta, timezone


def floor_to_hour(dt: datetime) -> datetime:
    return dt.replace(minute=0, second=0, microsecond=0)


def make_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def date_to_utc_datetime(d: date, hour: int = 0) -> datetime:
    return datetime(d.year, d.month, d.day, hour, 0, 0, tzinfo=timezone.utc)


def iter_dates(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)
