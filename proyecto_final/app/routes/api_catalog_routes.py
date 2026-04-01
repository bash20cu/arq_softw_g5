from flask import request

from app.controllers.persona_controller import PersonaController


def register_catalog_routes(bp):
    """Catalog routes are read-only lookups shared by the frontend forms."""

    @bp.get("/health")
    def health():
        return {"status": "ok", "database": "mssql"}, 200

    @bp.get("/catalogos/roles")
    def list_roles():
        return [role.to_dict() for role in PersonaController.list_roles()], 200

    @bp.get("/catalogos/provincias")
    def list_provincias():
        return [provincia.to_dict() for provincia in PersonaController.list_provincias()], 200

    @bp.get("/catalogos/cantones")
    def list_cantones():
        provincia_id = request.args.get("provincia_id", type=int)
        return [canton.to_dict() for canton in PersonaController.list_cantones(provincia_id)], 200

    @bp.get("/catalogos/distritos")
    def list_distritos():
        canton_id = request.args.get("canton_id", type=int)
        return [distrito.to_dict() for distrito in PersonaController.list_distritos(canton_id)], 200
