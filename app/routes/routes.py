from flask import Blueprint, jsonify, request
from app.models.user import User   # ✅ importar tu modelo
from app.database import db        # ✅ importar la conexión

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
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        return jsonify({"message": "Login exitoso", "user": user.to_dict()})
    else:
        return jsonify({"message": "Credenciales inválidas"}), 401

@main.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    cedula = data.get('cedula_persona')
    password = data.get('password')
    id_rol = data.get('id_rol', 1)  # rol por defecto

    new_user = User(
        username=username,
        cedula_persona=cedula,
        id_rol=id_rol
    )
    new_user.set_password(password)   # encriptar contraseña
    new_user.save()

    return jsonify({"message": "Usuario registrado con éxito", "user": new_user.to_dict()})