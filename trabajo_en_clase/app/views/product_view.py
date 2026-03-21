from flask import render_template


class ProductView:
    @staticmethod
    def render_lista(productos, error=None):
        return render_template("productos/lista.html", productos=productos, error=error)

    @staticmethod
    def render_form(producto, action, title, campanias, producto_id=None):
        return render_template(
            "productos/form.html",
            producto=producto,
            action=action,
            title=title,
            campanias=campanias,
            producto_id=producto_id,
        )

    @staticmethod
    def render_detalle(producto):
        return render_template("productos/detalle.html", producto=producto)
