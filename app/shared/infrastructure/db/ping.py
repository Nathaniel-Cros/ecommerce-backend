"""Database health checks."""

from sqlalchemy import text
from sqlalchemy.orm import Session


def ping_db(session: Session) -> bool:
    """Run a minimal query to verify DB connectivity."""

    result = session.execute(text("SELECT 1"))
    return result.scalar_one() == 1
