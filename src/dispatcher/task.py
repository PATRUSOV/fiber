from typing import Any, Tuple, Type, Union, get_args, Generator, get_origin, Final

from src.step import Step
from src.logging_manager import LoggingManager
from src.collections import CallNode


class _TaskEndSentinel: ...


TASK_END: Final = _TaskEndSentinel()


class Task:
    def __init__(self, call_node: CallNode, payload: Any):
        self._call_node = call_node
        self._payload = payload
        self._kernel_logger = LoggingManager.get_kernel_logger()
        self._generator = None
        self._input_type, self._output_type = self._get_step_types(self._call_node.step)

    def step(self) -> Union["Task", _TaskEndSentinel]:
        if self._generator is None:
            self._generator = self._initialize_generator()

        try:
            data = next(self._generator)
        except StopIteration:
            return TASK_END

        self._check_output_data(data, self._output_type)

        # вызываеться после проверки, что-бы убедиться что возвращаемое последним шагом значение,
        # являеться - None.
        if self._call_node.next is None:
            return TASK_END

        return Task(self._call_node.next, data)

    def _initialize_generator(self) -> Generator[Any, None, None]:
        self._check_input_data(self._payload, self._input_type)

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
            while True:
                try:
                    ret = next(generator)
                except StopIteration:
                    break
                except Exception as e:
                    self._call_node.step.logger.fatal(f"Критическая ошибка: {e}")
                    self._kernel_logger.info("Программа завершена.")
                    raise
                yield ret
        else:
            ret = output
            yield ret

    def _get_step_types(self, step: Type[Step]) -> Tuple[Type[Any], Type[Any]]:
        if issubclass(step, Step):
            bases = getattr(step, "__orig_bases__", [])
            for base_cls in bases:
                if get_origin(base_cls) is Step:
                    input_type, output_type = get_args(base_cls)
                    return input_type, output_type

        error_mes = f"Шаг {step.__name__} не являеться наследником Step"
        self._kernel_logger.fatal(error_mes)
        raise TypeError(error_mes)

    # TODO: Возможно вынести фцнкционал в отдельную фцнкцию
    # FIXME: Слабое место проверка на None, Any и и.д.
    def _check_input_data(self, data: Any, expected_type: Type[Any]) -> None:
        if not isinstance(data, expected_type):
            error_mes = f"{expected_type} - ожидаемый тип входных данных. Не совпал, с типом полученных данных - {type(data)}"
            self._call_node.step.logger.fatal(error_mes)
            raise TypeError(error_mes)

    def _check_output_data(self, data: Any, expected_type: Type[Any]):
        if not isinstance(data, expected_type):
            error_mes = f"{expected_type} - ожидаемый тип выходных данных. Не совпал с типом: {type(data)}"
            self._call_node.step.logger.fatal(error_mes)
            raise TypeError(error_mes)
