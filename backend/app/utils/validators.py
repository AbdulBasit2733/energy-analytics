from datetime import date

from fastapi import HTTPException


def validate_date_range(start: date | None, end: date | None):
    """Validate that start date is before or equal to end date.

    Raises:
        HTTPException: 400 if start > end
    """
    if start and end and start > end:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid date range: 'from' ({start}) must be <= 'to' ({end})",
        )
