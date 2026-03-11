from flask import render_template


class PersonaView:
    @staticmethod
    def render_lista(personas, error=None):
        return render_template("personas/lista.html", personas=personas, error=error)

    @staticmethod
    def render_form(persona, distritos, action, title, cedula=None):
        return render_template(
            "personas/form.html",
            persona=persona,
            distritos=distritos,
            action=action,
            title=title,
            cedula=cedula,
        )

    @staticmethod
    def render_detalle(persona):
        return render_template("personas/detalle.html", persona=persona)
