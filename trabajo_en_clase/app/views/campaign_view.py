from flask import render_template


class CampaignView:
    @staticmethod
    def render_lista(campanias, error=None):
        return render_template("campanias/lista.html", campanias=campanias, error=error)

    @staticmethod
    def render_form(campania, action, title, campania_id=None):
        return render_template(
            "campanias/form.html",
            campania=campania,
            action=action,
            title=title,
            campania_id=campania_id,
        )

    @staticmethod
    def render_detalle(campania):
        return render_template("campanias/detalle.html", campania=campania)
