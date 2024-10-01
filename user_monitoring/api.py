from flask import Blueprint, current_app, request
from user_monitoring.user_data_handler import handle_user_data

api = Blueprint("api", __name__)


@api.post("/event")
def handle_user_event() -> dict:
    current_app.logger.info("Handling user event")
    data = request.get_json()

    return handle_user_data(data)
