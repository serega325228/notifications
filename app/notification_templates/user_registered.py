from app.notification_templates.base import NotificationTemplate

class UserRegisteredTemplate(NotificationTemplate):
    def render(self, payload: dict | None) -> str:
        return f"Вы успешно зарегестрировались! Добро пожаловать)"