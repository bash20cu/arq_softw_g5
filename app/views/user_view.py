from flask import jsonify


def users_response(items: list[dict]):
    return jsonify(items), 200


def created_user_response(item: dict):
    return jsonify(item), 201


def error_response(message: str, status: int):
    return jsonify({"error": message}), status
