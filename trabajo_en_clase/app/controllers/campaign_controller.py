from datetime import date

from app.database import db
from app.models.campaign import Campaign


class CampaignController:
    @staticmethod
    def list_campaigns() -> list[Campaign]:
        return Campaign.query.order_by(Campaign.id_campania.desc()).all()

    @staticmethod
    def get_campaign_by_id(campaign_id: int) -> Campaign | None:
        return Campaign.query.filter_by(id_campania=campaign_id).first()

    @staticmethod
    def create_campaign(*, nombre: str, fecha_inicio=None, fecha_fin=None, descripcion=None) -> Campaign:
        start_date = CampaignController._parse_date(fecha_inicio, "fecha_inicio")
        end_date = CampaignController._parse_date(fecha_fin, "fecha_fin")
        if start_date and end_date and end_date < start_date:
            raise ValueError("fecha_fin no puede ser menor que fecha_inicio")

        campaign = Campaign(
            nombre=CampaignController._require_text(nombre, "nombre"),
            fecha_inicio=start_date,
            fecha_fin=end_date,
            descripcion=(descripcion or "").strip() or None,
        )
        db.session.add(campaign)
        db.session.commit()
        return campaign

    @staticmethod
    def update_campaign(campaign: Campaign, **fields) -> Campaign:
        nombre = fields.get("nombre", campaign.nombre)
        fecha_inicio = CampaignController._parse_date(
            fields.get("fecha_inicio", campaign.fecha_inicio), "fecha_inicio"
        )
        fecha_fin = CampaignController._parse_date(
            fields.get("fecha_fin", campaign.fecha_fin), "fecha_fin"
        )
        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise ValueError("fecha_fin no puede ser menor que fecha_inicio")

        campaign.nombre = CampaignController._require_text(nombre, "nombre")
        campaign.fecha_inicio = fecha_inicio
        campaign.fecha_fin = fecha_fin
        if "descripcion" in fields:
            campaign.descripcion = (fields.get("descripcion") or "").strip() or None

        db.session.add(campaign)
        db.session.commit()
        return campaign

    @staticmethod
    def delete_campaign(campaign: Campaign) -> None:
        db.session.delete(campaign)
        db.session.commit()

    @staticmethod
    def _require_text(value: str, field_name: str) -> str:
        parsed = (value or "").strip()
        if not parsed:
            raise ValueError(f"{field_name} es obligatorio")
        return parsed

    @staticmethod
    def _parse_date(value, field_name: str):
        if value in (None, ""):
            return None
        if isinstance(value, date):
            return value
        try:
            return date.fromisoformat(str(value))
        except ValueError as exc:
            raise ValueError(f"{field_name} debe tener formato YYYY-MM-DD") from exc
