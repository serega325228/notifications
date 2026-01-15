from app.notification_templates.base import NotificationTemplate

class OrderPaidTemplate(NotificationTemplate):
    def render(self, payload: dict) -> str:
        return f"Заказ №{payload["order_id"]} успешно оплачен"