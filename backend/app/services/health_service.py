import logging
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def check_db_health(db: Session) -> bool:
    """
    Executes a simple lightweight query to verify active database reachability.
    """
    try:
        db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        return False
