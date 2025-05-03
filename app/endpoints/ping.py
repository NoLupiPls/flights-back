from flask import Blueprint, jsonify


ping_bp = Blueprint('ping', __name__)


@ping_bp.route("/ping", methods=["GET"])
def ping():
    """
        Проверка того, что ваше приложение работает и готово принимать входящие запросы.
        Тело ответа может быть произвольным (на ваше усмотрение); главное - вернуть Status Code 200.
    """
    return jsonify({"status": "pong"})
