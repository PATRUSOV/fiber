from typing import Any, Type, Union, Generator, Final, Generic
from enum import Enum, auto

from src.step.types import I, O, get_step_types
from src.logging_manager import LoggingManager
from src.collections import CallNode


class _TaskEndSentinel:
    """
    Сентинел-объект, обозначающий завершение исполнения задачи (Task).
    Используется как флаг окончания исполнения цепочки шагов.
    """


# Обозначает конец исполнения Task()
TASK_END: Final = _TaskEndSentinel()


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

    def step(self) -> Union["Task", _TaskEndSentinel]:
        """
        Выполняет один шаг исполнения. Получает следующее значение от Step.start(),
        проверяет его тип и возвращает новый Task, либо TASK_END, если исполнение завершено.

        Returns:
            Union[Task, _TaskEndSentinel]:
                - Новый Task с выходными данными, если выполнение продолжается.
                - TASK_END, если генератор исчерпан или текущая вершина последняя.
        """
        if self._is_done:
            error_msg = "Нельзя вызвать step() у завершённого Task."
            self._call_node.step.logger.fatal(error_msg)
            raise RuntimeError(error_msg)

        if self._generator is None:
            self._generator = self._initialize_generator()

        try:
            data = next(self._generator)
        except StopIteration:
            self._is_done = True
            return TASK_END

        self._check_data(data, self._output_type, self._IorO.O)

        if self._call_node.next is None:
            self._is_done = True
            return TASK_END

        return Task(self._call_node.next, data)

    def _initialize_generator(self) -> Generator[O, None, None]:
        """
        Инициализирует генератор из метода Step.start(), обеспечивая поэтапную обработку
        входных данных с возможностью yield или прямого return.

        Returns:
            Generator[O, None, None]: генератор выходных значений.
        """
        self._check_data(self._payload, self._input_type, self._IorO.I)

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

    class _IorO(Enum):
        """
        Перечисление, определяющее направление проверки типов:
            - I: проверка входных данных
            - O: проверка выходных данных
        """

        I = auto()
        O = auto()

    def _check_data(
        self, data: I | O, expected_type: Type[I | O], target_of_checking: _IorO
    ) -> None:
        """
        Выполняет проверку типа данных (входных или выходных).

        Args:
            data (I | O): Проверяемое значение.
            expected_type (Type): Ожидаемый тип, извлечённый из Step.
            target_of_checking (_IorO): Указывает, что проверяется: вход или выход.

        Raises:
            TypeError: если тип `data` не соответствует ожидаемому.
        """
        if expected_type is not Any and not isinstance(
            data, (type(None), expected_type)
        ):
            kind = "входных" if target_of_checking is self._IorO.I else "выходных"
            error_msg = (
                f"{expected_type} - ожидаемый тип {kind} данных. "
                f"Не совпал с типом полученных данных - {type(data)}"
            )
            self._call_node.step.logger.fatal(error_msg)
            raise TypeError(error_msg)
