from abc import ABC, abstractmethod
from typing import Optional


class HealthCheckService(ABC):
    @abstractmethod
    async def check(self) -> Optional[str]:  # Return error or None
        ...
