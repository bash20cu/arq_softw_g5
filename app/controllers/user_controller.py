from flask import request, redirect, url_for, flash
from app.models.user import User, UserModel
from app.views.user_view import UserView


# Clase que usan tus compañeros desde api_v1.py — no se toca
class UserController:
    @staticmethod
    def list_users() -> list:
        return User.query.order_by(User.id_usuario.asc()).all()

    @staticmethod
    def create_user(cedula_persona, username, password_hash, id_rol, activo=True):
        user = User(
            cedula_persona=cedula_persona,
            username=username,
            password_hash=password_hash,
            id_rol=id_rol,
            activo=activo,
        )
        user.save()
        return user


# ------------------------------------------------------------------
# Funciones del frontend (pantallas HTML) — usan UserModel con mock
# ------------------------------------------------------------------

def listar_usuarios():
    usuarios, error = UserModel.get_all()
    return UserView.render_lista(usuarios=usuarios, error=error)


def detalle_usuario(usuario_id):
    usuario, error = UserModel.get_by_id(usuario_id)
    if error:
        flash(error, 'error')
        return redirect(url_for('frontend.usuarios_listar'))
    return UserView.render_detalle(usuario=usuario)


def crear_usuario():
    if request.method == 'POST':
        data, form_errors = _parse_form(is_create=True)
        if form_errors:
            for msg in form_errors:
                flash(msg, 'error')
            return UserView.render_form(usuario=data, action='crear', title='Nuevo Usuario')

        result, error = UserModel.create(data)
        if error:
            flash(f'Error al crear usuario: {error}', 'error')
            return UserView.render_form(usuario=data, action='crear', title='Nuevo Usuario')

        flash('Usuario creado exitosamente.', 'success')
        return redirect(url_for('frontend.usuarios_listar'))

    return UserView.render_form(usuario={}, action='crear', title='Nuevo Usuario')


def editar_usuario(usuario_id):
    if request.method == 'POST':
        data, form_errors = _parse_form(is_create=False)
        if form_errors:
            for msg in form_errors:
                flash(msg, 'error')
            usuario, _ = UserModel.get_by_id(usuario_id)
            return UserView.render_form(
                usuario=usuario or data, action='editar',
                title='Editar Usuario', usuario_id=usuario_id
            )

        result, error = UserModel.update(usuario_id, data)
        if error:
            flash(f'Error al actualizar usuario: {error}', 'error')
            usuario, _ = UserModel.get_by_id(usuario_id)
            return UserView.render_form(
                usuario=usuario or data, action='editar',
                title='Editar Usuario', usuario_id=usuario_id
            )

        flash('Usuario actualizado exitosamente.', 'success')
        return redirect(url_for('frontend.usuarios_listar'))

    usuario, error = UserModel.get_by_id(usuario_id)
    if error:
        flash(error, 'error')
        return redirect(url_for('frontend.usuarios_listar'))

    return UserView.render_form(
        usuario=usuario, action='editar',
        title='Editar Usuario', usuario_id=usuario_id
    )


def eliminar_usuario(usuario_id):
    success, error = UserModel.delete(usuario_id)
    if error:
        flash(f'Error al eliminar usuario: {error}', 'error')
    else:
        flash('Usuario eliminado exitosamente.', 'success')
    return redirect(url_for('frontend.usuarios_listar'))


def _parse_form(is_create: bool):
    cedula   = request.form.get('cedula_persona', '').strip()
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    id_rol   = request.form.get('id_rol', '').strip()
    activo   = 1 if request.form.get('activo') == 'on' else 0

    errors = []
    if not cedula:
        errors.append('La cédula es requerida.')
    if not username:
        errors.append('El nombre de usuario es requerido.')
    if is_create and not password:
        errors.append('La contraseña es requerida.')
    if not id_rol:
        errors.append('Debe seleccionar un rol.')

    data = {
        'cedula_persona': cedula,
        'username':       username,
        'id_rol':         int(id_rol) if id_rol.isdigit() else None,
        'activo':         activo,
    }
    if password:
        data['password_hash'] = password

    return data, errors