from app.database import db


class User(db.Model):
    __tablename__ = "Usuario"

    id_usuario = db.Column(db.Integer, primary_key=True)
    cedula_persona = db.Column(db.String(20), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    id_rol = db.Column(db.Integer, nullable=False)
    activo = db.Column(db.Boolean, default=True)

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()

    def to_dict(self) -> dict:
        return {
            "id_usuario": self.id_usuario,
            "cedula_persona": self.cedula_persona,
            "username": self.username,
            "id_rol": self.id_rol,
            "activo": self.activo,
        }

# -------------------------------------------------------------------
# Base de datos temporal en memoria (simulación)
# -------------------------------------------------------------------
_MOCK_DB = [
    {
        "id_usuario": 1,
        "cedula_persona": "0101010101",
        "username": "admin",
        "password_hash": "hashed_password",
        "id_rol": 1,
        "activo": 1,
    },
    {
        "id_usuario": 2,
        "cedula_persona": "0202020202",
        "username": "jperez",
        "password_hash": "hashed_password",
        "id_rol": 2,
        "activo": 1,
    },
    {
        "id_usuario": 3,
        "cedula_persona": "0303030303",
        "username": "mgarcia",
        "password_hash": "hashed_password",
        "id_rol": 3,
        "activo": 0,
    },
    {
        "id_usuario": 4,
        "cedula_persona": "0404040404",
        "username": "lrodriguez",
        "password_hash": "hashed_password",
        "id_rol": 4,
        "activo": 1,
    },
]
_next_id = 5   # contador para nuevos IDs


class UserModel:
    """
    Modelo de Usuario con datos simulados en memoria.
    Misma interfaz que la versión real con API:
      get_all()        → (lista, error)
      get_by_id(id)    → (usuario, error)
      create(data)     → (usuario, error)
      update(id, data) → (usuario, error)
      delete(id)       → (True/False, error)
    """

    # ------------------------------------------------------------------
    # GET /api/v1/usuario
    # ------------------------------------------------------------------
    @classmethod
    def get_all(cls):
        return list(_MOCK_DB), None

    # ------------------------------------------------------------------
    # GET /api/v1/usuario/{id}
    # ------------------------------------------------------------------
    @classmethod
    def get_by_id(cls, usuario_id):
        usuario = next((u for u in _MOCK_DB if u["id_usuario"] == usuario_id), None)
        if not usuario:
            return None, "Usuario no encontrado."
        return usuario, None

    # ------------------------------------------------------------------
    # POST /api/v1/usuario
    # ------------------------------------------------------------------
    @classmethod
    def create(cls, data: dict):
        global _next_id
        nuevo = {
            "id_usuario":     _next_id,
            "cedula_persona": data.get("cedula_persona", ""),
            "username":       data.get("username", ""),
            "password_hash":  data.get("password_hash", "hashed"),
            "id_rol":         data.get("id_rol", 4),
            "activo":         data.get("activo", 1),
        }
        _MOCK_DB.append(nuevo)
        _next_id += 1
        return nuevo, None

    # ------------------------------------------------------------------
    # PUT /api/v1/usuario/{id}
    # ------------------------------------------------------------------
    @classmethod
    def update(cls, usuario_id, data: dict):
        for i, u in enumerate(_MOCK_DB):
            if u["id_usuario"] == usuario_id:
                _MOCK_DB[i] = {**u, **data, "id_usuario": usuario_id}
                return _MOCK_DB[i], None
        return None, "Usuario no encontrado."

    # ------------------------------------------------------------------
    # DELETE /api/v1/usuario/{id}
    # ------------------------------------------------------------------
    @classmethod
    def delete(cls, usuario_id):
        for i, u in enumerate(_MOCK_DB):
            if u["id_usuario"] == usuario_id:
                _MOCK_DB.pop(i)
                return True, None
        return False, "Usuario no encontrado."
