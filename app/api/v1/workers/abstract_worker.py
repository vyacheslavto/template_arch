from abc import ABC
from abc import abstractmethod


class AbstractWorker(ABC):
    """Абстрактный класс воркера. Должен реализовать метод RUN."""

    @abstractmethod
    async def run(self, *args, **kwargs):
        """Метод, который должен реализовать каждый воркер.

        Иначе хелсчек будет считаться некорректно.

        Args:
            *args: агрументы
            **kwargs: ключевые аргументы
        """
