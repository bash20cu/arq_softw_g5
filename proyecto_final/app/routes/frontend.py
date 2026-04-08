from flask import Blueprint, redirect, render_template, session, url_for


frontend_bp = Blueprint("frontend", __name__)


@frontend_bp.get("/")
def home():
    return render_template("index.html")


@frontend_bp.get("/login")
def login_page():
    return render_template("login.html")


@frontend_bp.get("/registro")
def register_page():
    return render_template("registro.html")


@frontend_bp.get("/principal")
def principal_page():
    if session.get("user") is None:
        return redirect(url_for("frontend.login_page"))
    return render_template("principal.html")


@frontend_bp.get("/productos")
def products_page():
    return render_template("productos.html")


@frontend_bp.get("/ordenes")
def orders_page():
    if session.get("user") is None:
        return redirect(url_for("frontend.login_page"))
    return render_template("ordenes.html")


@frontend_bp.get("/consulta-pedido")
def order_status_page():
    return render_template("consulta_pedido.html")


@frontend_bp.get("/paypal/retorno")
def paypal_return_page():
    if session.get("user") is None:
        return redirect(url_for("frontend.login_page"))
    # The frontend captures the PayPal token after redirect and shows the result.
    return render_template("paypal_result.html", flow_state="approved")


@frontend_bp.get("/paypal/cancelado")
def paypal_cancel_page():
    if session.get("user") is None:
        return redirect(url_for("frontend.login_page"))
    return render_template("paypal_result.html", flow_state="cancelled")


@frontend_bp.get("/logout")
def logout_page():
    session.clear()
    return redirect(url_for("frontend.login_page"))

@frontend_bp.get("/clientes")
def clients_page():
    if session.get("user") is None:
        return redirect(url_for("frontend.login_page"))
    return render_template("clientes.html")

@frontend_bp.get("/personas")
def personas_page():
    if session.get("user") is None:
        return redirect(url_for("frontend.login_page"))
    return render_template("personas.html")