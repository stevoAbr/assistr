from typing import Callable  # we use callbacks for our handlers
from fastapi import FastAPI
from app.db.tasks import connect_to_db, close_db_connection


def create_start_app_handler(app: FastAPI) -> Callable:
    """
    Returns a callback
    """

    async def start_app() -> None:
        await connect_to_db(app)

    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    """
    describe
    """

    async def stop_app() -> None:
        await close_db_connection(app)

    return stop_app