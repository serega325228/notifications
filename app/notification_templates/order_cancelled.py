from app.notification_templates.base import NotificationTemplate

class OrderCancelledTemplate(NotificationTemplate):
    def render(self, payload: dict) -> str:
        return f"Заказ №{payload["order_id"]} завершен! Можете оставить отзыв..."