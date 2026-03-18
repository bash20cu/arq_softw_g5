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
                    "id": "personas",
                    "nombre": "Personas",
                    "descripcion": "Directorio base de personas y datos de contacto.",
                    "ruta_front": "/personas/",
                },
                {
                    "id": "clientes",
                    "nombre": "Clientes",
                    "descripcion": "Base de clientes independientes o vinculados a persona.",
                    "ruta_front": "/clientes/",
                },
                {
                    "id": "usuarios",
                    "nombre": "CRUD Usuarios",
                    "descripcion": "Gestion completa de usuarios del sistema.",
                    "ruta_front": "/usuarios/",
                },
                {
                    "id": "productos",
                    "nombre": "Productos",
                    "descripcion": "Catálogo de productos, precios y stock.",
                    "ruta_front": "/productos/",
                },
                {
                    "id": "ordenes",
                    "nombre": "Ordenes de compra",
                    "descripcion": "Generación de órdenes y consulta del detalle.",
                    "ruta_front": "/ordenes/",
                },
                {
                    "id": "campanias",
                    "nombre": "Campanias",
                    "descripcion": "Promociones y comunicacion comercial.",
                    "ruta_front": "/campanias/",
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
