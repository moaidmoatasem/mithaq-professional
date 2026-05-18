import logging

from cherenkov.api.middleware.auth import Role, hash_password
from cherenkov.core.storage.database import init_db, save_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_auth():
    init_db()

    # Default admin user
    username = "admin"
    password = "admin"
    hashed = hash_password(password)

    save_user(username, hashed, Role.ADMIN)
    logger.info(f"Initialized default user: {username} (Role: ADMIN)")


if __name__ == "__main__":
    init_auth()
