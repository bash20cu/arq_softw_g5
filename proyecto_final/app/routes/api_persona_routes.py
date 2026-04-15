"""Rutas CRUD de personas."""

from flask import request
from sqlalchemy.exc import IntegrityError

from app.controllers.persona_controller import PersonaController
from app.database import db
from app.routes.api_authz import ROLE_ADMIN, ROLE_EMPLEADO, roles_required
from app.routes.api_helpers import filter_allowed_fields
from app.views.user_view import error_response


def register_persona_routes(bp):
    """Expose persona management endpoints as their own bounded context."""

    @bp.get("/personas")
    @roles_required(ROLE_ADMIN, ROLE_EMPLEADO)
    def list_personas():
        """Lista las personas registradas en el sistema."""

        personas = PersonaController.list_personas()
        return [persona.to_dict() for persona in personas], 200

    @bp.get("/personas/<string:cedula>")
    @roles_required(ROLE_ADMIN, ROLE_EMPLEADO)
    def get_persona(cedula: str):
        """Obtiene una persona por su cedula."""

        persona = PersonaController.get_persona_by_cedula(cedula)
        if persona is None:
            return error_response("persona no encontrada", 404)
        return persona.to_dict(), 200

    @bp.post("/personas")
    @roles_required(ROLE_ADMIN, ROLE_EMPLEADO)
    def create_persona():
        """Crea una nueva persona a partir del payload JSON recibido."""

        payload = request.get_json(silent=True) or {}
        try:
            persona = PersonaController.create_persona(
                cedula=payload.get("cedula"),
                nombre=payload.get("nombre"),
                apellido=payload.get("apellido"),
                email=payload.get("email"),
                telefono=payload.get("telefono"),
                id_distrito=payload.get("id_distrito"),
            )
        except ValueError as exc:
            db.session.rollback()
            return error_response(str(exc), 400)
        except IntegrityError:
            db.session.rollback()
            return error_response("cedula o email ya existe / FK invalida", 409)

        return persona.to_dict(), 201

    @bp.put("/personas/<string:cedula>")
    @roles_required(ROLE_ADMIN, ROLE_EMPLEADO)
    def update_persona(cedula: str):
        """Actualiza una persona existente."""

        persona = PersonaController.get_persona_by_cedula(cedula)
        if persona is None:
            return error_response("persona no encontrada", 404)

        payload = request.get_json(silent=True) or {}
        allowed_fields = {"nombre", "apellido", "email", "telefono", "id_distrito"}
        update_fields = filter_allowed_fields(payload, allowed_fields)
        if not update_fields:
            return error_response("no hay campos validos para actualizar", 400)

        try:
            updated_persona = PersonaController.update_persona(persona, **update_fields)
        except ValueError as exc:
            db.session.rollback()
            return error_response(str(exc), 400)
        except IntegrityError:
            db.session.rollback()
            return error_response("cedula o email ya existe / FK invalida", 409)

        return updated_persona.to_dict(), 200

    @bp.delete("/personas/<string:cedula>")
    @roles_required(ROLE_ADMIN)
    def delete_persona(cedula: str):
        """Elimina una persona si no esta siendo referenciada por otras tablas."""

        persona = PersonaController.get_persona_by_cedula(cedula)
        if persona is None:
            return error_response("persona no encontrada", 404)

        try:
            PersonaController.delete_persona(persona)
        except ValueError as exc:
            db.session.rollback()
            return error_response(str(exc), 409)
        except IntegrityError:
            db.session.rollback()
            return error_response("persona en uso por otras tablas", 409)

        return {"ok": True, "message": "persona eliminada"}, 200
