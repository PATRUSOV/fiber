from typing import Type, Generator, Tuple, Any

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
        configurator: DispatcherConfigurator = DispatcherConfigurator(),
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
            f"Начался поток выполненения. Начальный шаг {call_node.cls.__name__}."
        )
        while call_node is not None:
            module_logger = call_node.cls.logger

            input_type = Type[Any]
            output_type = Type[Any]
            if issubclass(call_node.cls, Step):
                input_type, output_type = get_step_types(call_node.cls)
            else:
                error_mes = (
                    f"Шаг {call_node.cls.__name__} не являеться наследником Step"
                )
                self._logger.fatal(error_mes)
                raise TypeError(error_mes)

            module_logger.info("Вызван метод start()!")
            module_logger.debug(f"Стартовые данные: {data}")

            if not isinstance(data, input_type):
                error_mes = f"{input_type} - ожидаемый тип входных данных. Не совпал, с типом полученных данных - {type(data)}"
                module_logger.fatal(error_mes)
                raise TypeError(error_mes)

            try:
                output = call_node.cls.start(data)
            except Exception as e:
                module_logger.fatal(f"Критическая ошибка: {e}")
                self._logger.info("Программа завершена.")
                raise
            else:
                module_logger.info("Метод start() успешно завершён.")

            if isinstance(output, Generator):
                for ret in output:
                    if not isinstance(ret, output_type):
                        error_mes = f"{output_type} - ожидаемый тип выходных данных (yield). Не совпал с типом: {type(ret)}"
                        module_logger.fatal(error_mes)
                        raise TypeError(error_mes)

                    module_logger.debug("Породил поток выполнения.")
                    self._execute(call_node.next, ret)
            else:
                if not isinstance(output, output_type):
                    error_mes = f"{output_type} - ожидаемый тип выходных данных (return). Не совпал с типом: {type(output)}"
                    module_logger.fatal(error_mes)
                    raise TypeError(error_mes)

                data = output
                call_node = call_node.next
        self._logger.info("Поток выполения завершён.")
