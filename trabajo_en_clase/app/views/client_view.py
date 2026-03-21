from flask import render_template


class ClientView:
    @staticmethod
    def render_lista(clientes, error=None):
        return render_template("clientes/lista.html", clientes=clientes, error=error)

    @staticmethod
    def render_form(cliente, provincias, location, action, title, cliente_id=None):
        return render_template(
            "clientes/form.html",
            cliente=cliente,
            provincias=provincias,
            location=location,
            action=action,
            title=title,
            cliente_id=cliente_id,
        )

    @staticmethod
    def render_detalle(cliente):
        return render_template("clientes/detalle.html", cliente=cliente)
