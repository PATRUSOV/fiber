from typing import Generic, NoReturn, Type

from fiber.logging import get_kernel_logger
from fiber.step import Step, I, O, get_step_types
from fiber.pipeline.task.exceptions import (
    TaskDone,
    TaskRuntimeError,
    TaskTypeRuntimeError,
)
from fiber.pipeline.task.utils.types import impr_isinstance
from fiber.pipeline.task.utils.datastructs import Node
from fiber.pipeline.task.utils.functools import invoke_as_generator


class Task(Generic[I, O]):
    """
    Представляет собой универсальную и самодостаточную единицу исполнения.
    Связывает шаг (Step), его входные данные и следующую вершину вызова (Node).

    Отвечает за поэтапное выполнение метода Step.start(), включая генерацию
    следующих Task-ов и завершение цепочки.
    """

    def __init__(
        self, call_node: Node[Type[Step[I, O]]], payload: I, strict_types: bool
    ):
        """
        Инициализация задачи.

        Args:
            call_node (Node): Текущая вершина вызова, содержащая Step и ссылку на следующую.
            payload (I): Входные данные, передаваемые в Step.start().
        """
        self._call_node = call_node
        self._payload = payload
        self._kernel_logger = get_kernel_logger()
        self._strict_types = strict_types
        self._is_done = False
        self._generator = None  # отложенно инициализируемый генератор
        inp_t, self._out_t = get_step_types(self._call_node.item)

        if self._strict_types:
            if not impr_isinstance(data=self._payload, expected_type=inp_t):
                self._is_done = True
                err_msg = f"{inp_t} - ожидаемый тип входных данных. Не совпал с типом полученных данных - {type(self._payload)}"
                self._call_node.item.logger.critical(err_msg)
                raise TaskTypeRuntimeError(err_msg)

    def is_done(self) -> bool:
        """
        Returns:
            bool: Завершена ли задача.
        """
        return self._is_done

    def step(self) -> "Task":
        """
        Выполняет один шаг исполнения. Получает следующее значение от Step.start(),
        проверяет его тип и возвращает новый Task.

        Returns:
            Task - Новый Task с выходными данными.

        Raises:
            TaskDone: если генератор исчерпан или текущая вершина последняя.
        """
        # Проверка на завершенность (защита от вызова на пустом генераторе)
        if self._is_done:
            raise TaskDone()

        # Инициализация генератора
        if self._generator is None:
            self._call_node.item.logger.info("Вызван метод start()!")
            self._call_node.item.logger.debug(f"Стартовые данные: {self._payload}.")

            self._generator = invoke_as_generator(
                lambda: self._call_node.item.start(self._payload)
            )

        # Обработка значения с генератора
        try:
            data = next(self._generator)
        except StopIteration:
            self._call_node.item.logger.info("Метод start() успешно завершён.")
            self._raise_done()
        except Exception as e:
            self._is_done = True
            self._call_node.item.logger.fatal(f"{e}", exc_info=True)
            raise TaskRuntimeError(f"{e}") from e

        if self._strict_types:
            if not impr_isinstance(data=data, expected_type=self._out_t):
                self._is_done = True
                err_msg = (
                    f"{self._out_t} - ожидаемый тип выходных данных. Не совпал с типом полученных данных - {type(data)}",
                )
                self._call_node.item.logger.critical(err_msg, exc_info=True)
                raise TaskTypeRuntimeError(err_msg)

        # Последний Step доходит до первого return / yeild и завершается
        if self._call_node.next is None:
            self._call_node.item.logger.info("Метод start() успешно завершён.")
            self._raise_done()

        return Task(
            call_node=self._call_node.next,
            payload=data,  # type: ignore (линтер воспринимает Generic слишком буквально.)
            strict_types=self._strict_types,
        )

    def _raise_done(self) -> NoReturn:
        """Сигнализирует об остановкке таска."""
        self._is_done = True
        raise TaskDone()
