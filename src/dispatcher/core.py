from logging import Logger
from typing import Type, Generator, Tuple, Any
from queue import Queue

from src.step import Step
from src.collections import get_call_head, CallNode
from src.configurator import DispatcherConfigurator
from src.logging_manager import LoggingManager
from src.utils.func import get_step_types


class Dispatcher:
    """
    Класс является исполняющим ядром для классов реализующих интерфейс Step.
    """

    def __init__(
        self,
        steps: Tuple[Type[Step], ...],
        configurator: DispatcherConfigurator = DispatcherConfigurator(
            THREADS=1, MAX_TASKS=30
        ),
    ):
        # голова связного списка
        self._call_ll_head = get_call_head(steps)
        self._configurator = configurator  # TODO: add impl
        self._logger = LoggingManager.get_kernel_logger()

    def run(self) -> None:
        self._logger.info("Приложение запущено.")
        self._execute(self._call_ll_head, None)
        self._logger.info("Приложение завршено.")

    # TODO:
    #       +Поддержка потоков
    #       +Поддержка сигналов
    #       +Ограничитель глубины рекурсии и потоков
    #       +Блокирующая очередь
    #       +Рефокторинг
    #       +Декомпозиция проверки типов
    # FIXME:
    #       +Проверка типов не поддерживает None и Any за счет того что это объекты
    #       +Что если после yield ничего не будет?
    #       +Что если будет yield и потом return, или наоборот?
    #       +В yield должен быть break иначе while True
    def _execute(self, call_node: CallNode, data: Any) -> None:
        """
        Рекурсивная функция, обхода CallNode. Передает данные между листами спика.
        В случае если вместо данных был получен генератор, функция рекурсивно запускает себя с данными полученными из
        генератора, пока генератор не вернет все что у него было. Что значит рекурсивный запуск? А значит, что если генератор
        был получен на node1, и список выглядит примерно так: node1 -> node2 -> node3. То node1 будет запускать execute с node2,
        пока у него есть что отдавать.

        Arguments:
            call_node: Вызов с которого начинается обход.
            data: Данные с которыми вызовется start() у call_node.cls

        Returns:
            Ничего, т.к. предусмотреног что все дейсвия выполняються через FIXME: конвеер
        """
        self._logger.debug(
            f"Начался поток выполненения. Начальный шаг {call_node.step.__name__}."
        )
        while call_node is not None:
            module_logger = call_node.step.logger
            input_type, output_type = self._get_step_types(call_node.step)

            self._check_input_data(data, input_type, module_logger)

            module_logger.info("Вызван метод start()!")
            module_logger.debug(f"Стартовые данные: {data}")

            try:
                output = call_node.step.start(data)
            except Exception as e:
                module_logger.fatal(f"Критическая ошибка: {e}")
                self._logger.info("Программа завершена.")
                raise
            else:
                module_logger.info("Метод start() успешно завершён.")

            if isinstance(output, Generator):
                for ret in output:
                    self._check_output_data(ret, output_type, module_logger)

                    module_logger.debug("Породил поток выполнения.")
                    self._execute(call_node.next, ret)
                break  # TODO: think about it (._.)
            else:
                data = output
                self._check_output_data(data, output_type, module_logger)
                call_node = call_node.next
        self._logger.info("Поток выполения завершён.")

    def _get_step_types(self, step: Type[Step]) -> Tuple[Type[Any], Type[Any]]:
        if issubclass(step, Step):
            return get_step_types(step)
        else:
            error_mes = f"Шаг {step.__name__} не являеться наследником Step"
            self._logger.fatal(error_mes)
            raise TypeError(error_mes)

    def _check_input_data(
        self, data: Any, expected_type: Type[Any], logger: Logger
    ) -> None:
        if not isinstance(data, expected_type):
            error_mes = f"{expected_type} - ожидаемый тип входных данных. Не совпал, с типом полученных данных - {type(data)}"
            logger.fatal(error_mes)
            raise TypeError(error_mes)

    def _check_output_data(self, data: Any, expected_type: Type[Any], logger: Logger):
        if not isinstance(data, expected_type):
            error_mes = f"{expected_type} - ожидаемый тип выходных данных (return). Не совпал с типом: {type(data)}"
            logger.fatal(error_mes)
            raise TypeError(error_mes)
