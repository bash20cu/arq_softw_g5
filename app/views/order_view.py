from flask import render_template


class OrderView:
    @staticmethod
    def render_lista(ordenes, error=None):
        return render_template("ordenes/lista.html", ordenes=ordenes, error=error)

    @staticmethod
    def render_form(clientes, productos, order_data=None, order=None, is_edit=False):
        return render_template(
            "ordenes/form.html",
            clientes=clientes,
            productos=productos,
            order_data=order_data or {},
            order=order,
            is_edit=is_edit,
        )

    @staticmethod
    def render_detalle(orden, total, available_transitions):
        return render_template(
            "ordenes/detalle.html",
            orden=orden,
            total=total,
            available_transitions=available_transitions,
        )
