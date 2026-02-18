from flask import Blueprint
from app.controllers.user_controller import (
    listar_usuarios,
    detalle_usuario,
    crear_usuario,
    editar_usuario,
    eliminar_usuario,
)

frontend_bp = Blueprint('frontend', __name__, url_prefix='/usuarios')

frontend_bp.add_url_rule('/',                         'usuarios_listar',  listar_usuarios,  methods=['GET'])
frontend_bp.add_url_rule('/nuevo',                    'usuarios_crear',   crear_usuario,    methods=['GET', 'POST'])
frontend_bp.add_url_rule('/<int:usuario_id>',         'usuarios_detalle', detalle_usuario,  methods=['GET'])
frontend_bp.add_url_rule('/<int:usuario_id>/editar',  'usuarios_editar',  editar_usuario,   methods=['GET', 'POST'])
frontend_bp.add_url_rule('/<int:usuario_id>/eliminar','usuarios_eliminar',eliminar_usuario, methods=['POST'])