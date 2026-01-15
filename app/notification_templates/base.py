from abc import ABC, abstractmethod

class NotificationTemplate(ABC):
    @abstractmethod
    def render(self, payload: dict | None) -> str:
        pass