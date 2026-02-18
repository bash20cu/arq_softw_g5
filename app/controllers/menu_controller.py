from app.database import db
from app.models.order import Order
from app.models.support_case import SupportCase


class MenuController:
    @staticmethod
    def get_main_menu_payload(user: dict) -> dict:
        ordenes_pendientes = (
            db.session.query(Order).filter(Order.estado == "Pendiente").count()
        )
        envios_en_ruta = db.session.query(Order).filter(Order.estado == "Enviado").count()
        casos_soporte_abiertos = (
            db.session.query(SupportCase)
            .filter(SupportCase.estado.in_(["Nuevo", "En Análisis", "Esperando Cliente"]))
            .count()
        )

        # MVP: la estructura del menu esta hardcodeada temporalmente para desacoplar backend/frontend.
        # Los KPIs si se calculan dinamicamente desde la base de datos.
        return {
            "empresa": "Envios G5",
            "bienvenida": f"Bienvenido, {user['username']}",
            "modulos": [
                {
                    "id": "ordenes",
                    "nombre": "Ordenes de envio",
                    "descripcion": "Crear y dar seguimiento a ordenes activas.",
                    "ruta_front": "/principal/ordenes",
                },
                {
                    "id": "clientes",
                    "nombre": "Clientes",
                    "descripcion": "Gestion de clientes y datos de contacto.",
                    "ruta_front": "/principal/clientes",
                },
                {
                    "id": "campanias",
                    "nombre": "Campanias",
                    "descripcion": "Promociones y comunicacion comercial.",
                    "ruta_front": "/principal/campanias",
                },
                {
                    "id": "soporte",
                    "nombre": "Soporte",
                    "descripcion": "Casos y seguimiento postventa.",
                    "ruta_front": "/principal/soporte",
                },
            ],
            "kpis": {
                "ordenes_pendientes": ordenes_pendientes,
                "envios_en_ruta": envios_en_ruta,
                "casos_soporte_abiertos": casos_soporte_abiertos,
            },
            "user": user,
        }
