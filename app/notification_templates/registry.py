from app.db.models.enums import EventType
from app.notification_templates.order_cancelled import OrderCancelledTemplate
from app.notification_templates.order_paid import OrderPaidTemplate
from app.notification_templates.user_registered import UserRegisteredTemplate

notification_templates = {
    EventType.USER_REGISTERED: UserRegisteredTemplate,
    EventType.ORDER_PAID: OrderPaidTemplate,
    EventType.ORDER_CANCELLED: OrderCancelledTemplate
}