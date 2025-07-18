from abc import abstractmethod, ABC
from logging import Logger
from typing import Generic, TypeVar, Generator, Union

from src.logging_manager import LoggingManager

I = TypeVar("I")
O = TypeVar("O")


class Step(ABC, Generic[I, O]):
    """
    Абстрактный класс являющийся базовая единица исполнения.
    Цепочка исполнения предусматривается как самодостаточная единица.
    Следовательно данные получают в цепочке и работают с ними только там.
    То есть первый шаг принимает, а последний возвращает None.

    Attributes:
        start(): абстрактный статический метод, вызываемый у наследника при выполнении цепочки.

    Example:

        >>> class Something: ...
        >>> class Anything: ...

        >>> #При наследовании обязательно указывать что класс принимает и что возвращает.
        >>> class TestingStep(Step[Something, Anything]):

        >>>     # start(), можно переопределить или так:
        >>>     @staticmethod
        >>>     def start(data: Something) -> Anything:
        >>>         return Anything()

        >>>     # или так:
        >>>     def start(data: Something) -> Generator[Anything, None, None]:

        >>>         some_data_arr = [Anything(), Anything()]

        >>>         for ret in some_data_arr:
        >>>             yield ret

    """

    logger: Logger

    @staticmethod
    @abstractmethod
    def start(data: I) -> Union[O, Generator[O, None, None]]:
        """
        Абстрактный статический метод. Является основной точкой входа для каждого шага.
        В случае если шаг первый первый, то он не должен принимать None в качестве I, а если последний
        то O.

        Arguments:
            data (I): Входные данные, полученные от предыдущего шага пайплайна.

        Returns:
            O или Generator[O, None, None]:
                - Если возвращается StepResult — шаг выполняется один раз и передаёт результат дальше.
                - Если используется yield и возвращается генератор — шаг может передать несколько результатов.

        Особенности yield:
            - Каждый yield сразу запускает **все оставшиеся шаги в цепочке**, начиная со следующего.
            - После завершения цепочки пайплайн возвращается к текущему шагу и продолжает генератор.
            - Так продолжается, пока генератор не будет исчерпан.
            - Это позволяет реализовать разветвлённую или поэтапную обработку данных с минимальной связностью.

        Пример:

            # Возвращает один результат — шаг завершает выполнение:
            return StepResult(result)

            # Возвращает генератор — шаг вызывает оставшуюся цепочку несколько раз:
            yield StepResult(part1)  # Вся цепочка выполняется с part1
            yield StepResult(part2)  # Затем снова с part2
            yield StepResult(part3)  # И так далее...

        """

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        cls.logger = LoggingManager.get_module_logger(cls.__name__)
