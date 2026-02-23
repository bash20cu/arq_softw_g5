from flask import Blueprint, jsonify, request

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return "Servidor Flask funcionando, SIIIIIIUUUUUUU"

@main.route('/api/v1/health')
def health():
    return jsonify({"status": "ok", "message": "API funcionando correctamente"})

@main.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    return jsonify({"message": "Login recibido", "data": data})

@main.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    return jsonify({"message": "Registro recibido", "data": data})