"""Rutas de catalogos auxiliares y endpoints livianos de soporte."""

from flask import request

from app.controllers.persona_controller import PersonaController


def register_catalog_routes(bp):
    """Catalog routes are read-only lookups shared by the frontend forms."""

    @bp.get("/health")
    def health():
        """Endpoint minimo para comprobar que el API esta respondiendo."""

        return {"status": "ok", "database": "mssql"}, 200

    @bp.get("/catalogos/roles")
    def list_roles():
        """Lista los roles disponibles del sistema."""

        return [role.to_dict() for role in PersonaController.list_roles()], 200

    @bp.get("/catalogos/provincias")
    def list_provincias():
        """Lista las provincias del catalogo geografico."""

        return [provincia.to_dict() for provincia in PersonaController.list_provincias()], 200

    @bp.get("/catalogos/cantones")
    def list_cantones():
        """Lista cantones y permite filtrar por provincia."""

        provincia_id = request.args.get("provincia_id", type=int)
        return [canton.to_dict() for canton in PersonaController.list_cantones(provincia_id)], 200

    @bp.get("/catalogos/distritos")
    def list_distritos():
        """Lista distritos y permite filtrar por canton."""

        canton_id = request.args.get("canton_id", type=int)
        return [distrito.to_dict() for distrito in PersonaController.list_distritos(canton_id)], 200
