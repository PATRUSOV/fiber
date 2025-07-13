from typing import Generator, Generic

from src.step.types import I, O, get_step_types
from src.utils.types import impr_isinstance
from src.logging_manager import LoggingManager
from src.collections import CallNode


class TaskDone(Exception): ...


class Task(Generic[I, O]):
    """
    Представляет собой универсальную и самодостаточную единицу исполнения.
    Связывает шаг (Step), его входные данные и следующую вершину вызова (CallNode).

    Отвечает за поэтапное выполнение метода Step.start(), включая генерацию
    следующих Task-ов и завершение цепочки.
    """

    def __init__(self, call_node: CallNode[I, O], payload: I):
        """
        Инициализация задачи.

        Args:
            call_node (CallNode): Текущая вершина вызова, содержащая Step и ссылку на следующую.
            payload (I): Входные данные, передаваемые в Step.start().
        """
        self._call_node = call_node
        self._payload = payload
        self._kernel_logger = LoggingManager.get_kernel_logger()
        self._is_done = False
        self._generator = None  # Отложенно инициализируемый генератор
        self._input_type, self._output_type = get_step_types(self._call_node.step)

    def step(self) -> "Task":
        """
        Выполняет один шаг исполнения. Получает следующее значение от Step.start(),
        проверяет его тип и возвращает новый Task.

        Returns:
            Task - Новый Task с выходными данными.

        Raises:
            TaskDone: если генератор исчерпан или текущая вершина последняя.
        """
        if self._is_done:
            raise TaskDone()

        if self._generator is None:
            self._generator = self._initialize_generator()

        try:
            data = next(self._generator)
        except StopIteration:
            self._is_done = True
            raise TaskDone()

        impr_isinstance(
            data=data,
            expected_type=self._output_type,
            error_msg=f"{self._output_type} - ожидаемый тип выходных данных. Не совпал с типом полученных данных - {type(data)}",
            logger=self._call_node.step.logger,
        )

        if self._call_node.next is None:
            self._is_done = True
            raise TaskDone()

        return Task(self._call_node.next, data)

    def _initialize_generator(self) -> Generator[O, None, None]:
        """
        Инициализирует генератор из метода Step.start(), обеспечивая поэтапную обработку
        входных данных с возможностью yield или прямого return.

        Returns:
            Generator[O, None, None]: генератор выходных значений.
        """
        impr_isinstance(
            data=self._payload,
            expected_type=self._input_type,
            error_msg=f"{self._input_type} - ожидаемый тип входных данных. Не совпал с типом полученных данных - {type(self._payload)}",
            logger=self._call_node.step.logger,
        )

        self._call_node.step.logger.info("Вызван метод start()!")
        self._call_node.step.logger.debug(f"Стартовые данные: {self._payload}")

        try:
            output = self._call_node.step.start(self._payload)
        except Exception as e:
            self._call_node.step.logger.fatal(f"Критическая ошибка: {e}")
            self._kernel_logger.info("Программа завершена.")
            raise
        else:
            self._call_node.step.logger.info("Метод start() успешно завершён.")

        if isinstance(output, Generator):
            generator = output
            try:
                yield from generator
            except Exception as e:
                self._call_node.step.logger.fatal(f"Критическая ошибка: {e}")
                self._kernel_logger.info("Программа завершена.")
                raise
        else:
            yield output
