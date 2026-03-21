from app.controllers.persona_controller import PersonaController
from app.database import db
from app.models.user import Cliente, Persona


class ClientController:
    ALLOWED_STATES = {"Activo", "Inactivo", "VIP", "Moroso"}
    ALLOWED_TYPES = {"Persona", "Empresa"}

    @staticmethod
    def list_clients() -> list[Cliente]:
        return Cliente.query.order_by(Cliente.nombre.asc(), Cliente.apellido.asc()).all()

    @staticmethod
    def get_client_by_id(client_id: int) -> Cliente | None:
        return Cliente.query.filter_by(id_cliente=client_id).first()

    @staticmethod
    def get_client_by_cedula(cedula_persona: str) -> Cliente | None:
        return Cliente.query.filter_by(cedula_persona=cedula_persona).first()

    @staticmethod
    def create_client(
        *,
        tipo_cliente: str = "Persona",
        nombre: str,
        apellido: str | None,
        email: str,
        telefono: str | None = None,
        direccion: str | None = None,
        id_distrito: int | None = None,
        cedula_persona: str | None = None,
        puntos_lealtad=0,
        estado_cliente: str = "Activo",
    ) -> Cliente:
        persona = ClientController._validate_persona_link(cedula_persona)
        normalized = ClientController._normalize_base_fields(
            tipo_cliente=tipo_cliente,
            nombre=nombre,
            apellido=apellido,
            email=email,
            telefono=telefono,
            direccion=direccion,
            id_distrito=id_distrito,
            puntos_lealtad=puntos_lealtad,
            estado_cliente=estado_cliente,
        )
        ClientController._validate_unique_link(cedula_persona)

        if persona is not None:
            normalized = ClientController._merge_with_persona(normalized, persona)

        client = Cliente(cedula_persona=cedula_persona, **normalized)
        db.session.add(client)
        db.session.commit()
        return client

    @staticmethod
    def create_client_from_persona(
        *,
        cedula_persona: str,
        puntos_lealtad=0,
        estado_cliente: str = "Activo",
    ) -> Cliente:
        persona = ClientController._validate_persona_link(cedula_persona)
        if persona is None:
            raise ValueError("cedula_persona no existe en Persona")
        ClientController._validate_unique_link(cedula_persona)

        client = Cliente(
            cedula_persona=cedula_persona,
            tipo_cliente="Persona",
            nombre=persona.nombre,
            apellido=persona.apellido,
            email=persona.email,
            telefono=persona.telefono,
            direccion=None,
            id_distrito=persona.id_distrito,
            puntos_lealtad=ClientController._validate_points(puntos_lealtad),
            estado_cliente=ClientController._validate_state(estado_cliente),
        )
        db.session.add(client)
        db.session.commit()
        return client

    @staticmethod
    def update_client(client: Cliente, **fields) -> Cliente:
        if "cedula_persona" in fields:
            persona = ClientController._validate_persona_link(fields["cedula_persona"])
            ClientController._validate_unique_link(
                fields["cedula_persona"], current_client_id=client.id_cliente
            )
            client.cedula_persona = fields["cedula_persona"] or None
            if persona is not None:
                client.tipo_cliente = "Persona"
                client.nombre = persona.nombre
                client.apellido = persona.apellido
                client.email = persona.email
                client.telefono = persona.telefono
                client.direccion = None
                client.id_distrito = persona.id_distrito

        if "tipo_cliente" in fields:
            client.tipo_cliente = ClientController._validate_type(fields["tipo_cliente"])
        if "nombre" in fields:
            client.nombre = ClientController._require_text(fields["nombre"], "nombre")
        if "apellido" in fields:
            client.apellido = ClientController._normalize_last_name(
                fields["apellido"], client.tipo_cliente
            )
        if "email" in fields:
            client.email = ClientController._require_text(fields["email"], "email")
        if "telefono" in fields:
            client.telefono = (fields["telefono"] or "").strip() or None
        if "direccion" in fields:
            client.direccion = (fields["direccion"] or "").strip() or None
        if "id_distrito" in fields:
            client.id_distrito = PersonaController._validate_distrito(fields["id_distrito"])
        if "puntos_lealtad" in fields:
            client.puntos_lealtad = ClientController._validate_points(fields["puntos_lealtad"])
        if "estado_cliente" in fields:
            client.estado_cliente = ClientController._validate_state(fields["estado_cliente"])

        db.session.add(client)
        db.session.commit()
        return client

    @staticmethod
    def delete_client(client: Cliente) -> None:
        db.session.delete(client)
        db.session.commit()

    @staticmethod
    def _normalize_base_fields(
        *,
        tipo_cliente: str,
        nombre: str,
        apellido: str | None,
        email: str,
        telefono: str | None,
        direccion: str | None,
        id_distrito,
        puntos_lealtad,
        estado_cliente: str,
    ) -> dict:
        parsed_type = ClientController._validate_type(tipo_cliente)
        return {
            "tipo_cliente": parsed_type,
            "nombre": ClientController._require_text(nombre, "nombre"),
            "apellido": ClientController._normalize_last_name(apellido, parsed_type),
            "email": ClientController._require_text(email, "email"),
            "telefono": (telefono or "").strip() or None,
            "direccion": (direccion or "").strip() or None,
            "id_distrito": PersonaController._validate_distrito(id_distrito),
            "puntos_lealtad": ClientController._validate_points(puntos_lealtad),
            "estado_cliente": ClientController._validate_state(estado_cliente),
        }

    @staticmethod
    def _merge_with_persona(fields: dict, persona: Persona) -> dict:
        merged = dict(fields)
        merged["tipo_cliente"] = "Persona"
        merged["nombre"] = persona.nombre
        merged["apellido"] = persona.apellido
        merged["email"] = persona.email
        merged["telefono"] = persona.telefono
        merged["id_distrito"] = persona.id_distrito
        return merged

    @staticmethod
    def _validate_persona_link(cedula_persona: str | None) -> Persona | None:
        parsed = (cedula_persona or "").strip()
        if not parsed:
            return None
        persona = Persona.query.filter_by(cedula=parsed).first()
        if persona is None:
            raise ValueError("cedula_persona no existe en Persona")
        return persona

    @staticmethod
    def _validate_unique_link(
        cedula_persona: str | None,
        *,
        current_client_id: int | None = None,
    ) -> None:
        parsed = (cedula_persona or "").strip()
        if not parsed:
            return
        query = Cliente.query.filter_by(cedula_persona=parsed)
        if current_client_id is not None:
            query = query.filter(Cliente.id_cliente != current_client_id)
        if query.first() is not None:
            raise ValueError("ya existe un cliente vinculado a esa persona")

    @staticmethod
    def _require_text(value: str, field_name: str) -> str:
        parsed = (value or "").strip()
        if not parsed:
            raise ValueError(f"{field_name} es obligatorio")
        return parsed

    @staticmethod
    def _validate_type(value: str) -> str:
        parsed = (value or "Persona").strip()
        if parsed not in ClientController.ALLOWED_TYPES:
            raise ValueError("tipo_cliente no permitido")
        return parsed

    @staticmethod
    def _normalize_last_name(value: str | None, tipo_cliente: str) -> str | None:
        parsed = (value or "").strip()
        if tipo_cliente == "Empresa":
            return parsed or None
        if not parsed:
            raise ValueError("apellido es obligatorio")
        return parsed

    @staticmethod
    def _validate_points(value) -> int:
        try:
            points = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("puntos_lealtad debe ser numerico") from exc
        if points < 0:
            raise ValueError("puntos_lealtad no puede ser negativo")
        return points

    @staticmethod
    def _validate_state(value: str) -> str:
        state = (value or "Activo").strip()
        if state not in ClientController.ALLOWED_STATES:
            raise ValueError("estado_cliente no permitido")
        return state
