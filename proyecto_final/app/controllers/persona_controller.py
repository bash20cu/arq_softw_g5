from app.database import db
from app.models.catalog import Canton, Distrito, Provincia, Role
from app.models.user import Cliente, Persona, User


class PersonaController:
    @staticmethod
    def list_personas() -> list[Persona]:
        return Persona.query.order_by(Persona.nombre.asc(), Persona.apellido.asc()).all()

    @staticmethod
    def get_persona_by_cedula(cedula: str) -> Persona | None:
        return Persona.query.filter_by(cedula=cedula).first()

    @staticmethod
    def create_persona(
        *,
        cedula: str,
        nombre: str,
        apellido: str,
        email: str,
        telefono: str | None = None,
        id_distrito: int | None = None,
    ) -> Persona:
        persona = Persona(
            cedula=PersonaController._require_text(cedula, "cedula"),
            nombre=PersonaController._require_text(nombre, "nombre"),
            apellido=PersonaController._require_text(apellido, "apellido"),
            email=PersonaController._require_text(email, "email"),
            telefono=(telefono or "").strip() or None,
            id_distrito=PersonaController._validate_distrito(id_distrito),
        )
        db.session.add(persona)
        db.session.commit()
        return persona

    @staticmethod
    def update_persona(persona: Persona, **fields) -> Persona:
        if "nombre" in fields:
            persona.nombre = PersonaController._require_text(fields["nombre"], "nombre")
        if "apellido" in fields:
            persona.apellido = PersonaController._require_text(fields["apellido"], "apellido")
        if "email" in fields:
            persona.email = PersonaController._require_text(fields["email"], "email")
        if "telefono" in fields:
            persona.telefono = (fields["telefono"] or "").strip() or None
        if "id_distrito" in fields:
            persona.id_distrito = PersonaController._validate_distrito(fields["id_distrito"])

        db.session.add(persona)
        db.session.commit()
        return persona

    @staticmethod
    def delete_persona(persona: Persona) -> None:
        if User.query.filter_by(cedula_persona=persona.cedula).first() is not None:
            raise ValueError("persona en uso por usuario")
        if Cliente.query.filter_by(cedula_persona=persona.cedula).first() is not None:
            raise ValueError("persona en uso por cliente")
        db.session.delete(persona)
        db.session.commit()

    @staticmethod
    def list_roles() -> list[Role]:
        return Role.query.order_by(Role.id_rol.asc()).all()

    @staticmethod
    def list_provincias() -> list[Provincia]:
        return Provincia.query.order_by(Provincia.id_provincia.asc()).all()

    @staticmethod
    def list_cantones(id_provincia: int | None = None) -> list[Canton]:
        query = Canton.query
        if id_provincia is not None:
            query = query.filter_by(id_provincia=id_provincia)
        return query.order_by(Canton.id_canton.asc()).all()

    @staticmethod
    def list_distritos(id_canton: int | None = None) -> list[Distrito]:
        query = Distrito.query
        if id_canton is not None:
            query = query.filter_by(id_canton=id_canton)
        return query.order_by(Distrito.id_distrito.asc()).all()

    @staticmethod
    def get_location_selection(id_distrito: int | None) -> dict:
        if not id_distrito:
            return {"id_provincia": None, "id_canton": None, "id_distrito": None}

        distrito = Distrito.query.filter_by(id_distrito=id_distrito).first()
        if distrito is None:
            return {"id_provincia": None, "id_canton": None, "id_distrito": None}

        canton = distrito.canton
        provincia = canton.provincia if canton else None
        return {
            "id_provincia": provincia.id_provincia if provincia else None,
            "id_canton": canton.id_canton if canton else None,
            "id_distrito": distrito.id_distrito,
        }

    @staticmethod
    def _require_text(value: str, field_name: str) -> str:
        parsed = (value or "").strip()
        if not parsed:
            raise ValueError(f"{field_name} es obligatorio")
        return parsed

    @staticmethod
    def _validate_distrito(value) -> int | None:
        if value in (None, "", 0, "0"):
            return None
        try:
            distrito_id = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("id_distrito debe ser numerico") from exc

        distrito = Distrito.query.filter_by(id_distrito=distrito_id).first()
        if distrito is None:
            raise ValueError("id_distrito no existe")
        return distrito_id
