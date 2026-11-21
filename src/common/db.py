"""PostgreSQL connection factory."""

import os
import pg8000


def connect_db():
    """Open a connection using the environment configured in template.yaml."""
    return pg8000.connect(
        host=os.environ.get("DB_HOST", "db"),
        port=int(os.environ.get("DB_PORT", "5432")),
        database=os.environ.get("DB_NAME", "appointments_db"),
        user=os.environ.get("DB_USER", "app_user"),
        password=os.environ.get("DB_PASSWORD", "local_dev_password"),
        timeout=5,
    )
