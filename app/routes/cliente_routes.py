from flask import Blueprint, jsonify
from app.models.user import Cliente
from app.database import db

cliente_bp = Blueprint("cliente", __name__)

@cliente_bp.route("/clientes", methods=["GET"])
def get_clientes():
    clientes = Cliente.query.all()
    return jsonify([
        {
            "id_cliente": c.id_cliente,
            "cedula_persona": c.cedula_persona
        } for c in clientes
    ])
