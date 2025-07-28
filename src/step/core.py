import src.logman as lm

from src.step.vars import I, O
from abc import abstractmethod, ABC
from logging import Logger
from typing import Generic, Generator, Union, get_args, get_origin
from step.exceptions import (
    StepTypeParameterCountMismatch,
    StepTypeParametersMissing,
    StepTypeExtractionError,
)


class Step(ABC, Generic[I, O]):
    """
    Абстрактный класс являющийся базовая единица исполнения.
    Цепочка исполнения предусматривается как самодостаточная единица.
    Следовательно данные получают в цепочке и работают с ними только там.
    То есть первый шаг принимает, а последний возвращает None.

    - Многопоточность: шаги могут исполнятся как и в одном потоке так и в нескольких.
    Тобиш развилки (yield) можно распараллелить. Но отвсетсвенность за ресурсы,
    к которым могут попытаться обратиться сразу несколько шагов из нескольких потоков одновременно (например:
    файлы, базы данных и т.д.), полностью лежит на mutex-ах, очередях и прочих ThreadSafe механизмах, реализованных внутри шагов.

    - Особенности: вся валидация происходит при наследование -> класс наследника гарантировано будет корректным.

    Аттрибуты:
        start(): абстрактный статический метод, вызываемый у наследника при выполнении цепочки.
        logger (Logger): Логгер выделяемый шагу. Рекомнедуется при разработки ипользовать именно его
        и его наследников для централизованого и безопасного логгирования.

    Исключения:
        StepTypeParametersMissing:
            Параметры типов не указаны (Step без [I, O]).

        StepTypeParameterCountMismatch:
            Количесво параметров типов не равно двуx (например, Step[int], Step[int, str, float]).

        StepTypeExtractionError:
            Step[...] не найден в __orig_bases__, вероятно, скрыт в глубокой иерархии.


    Примеры:
        >>> class Something: ...
        >>> class Anything: ...

        >>> #При наследовании обязательно указывать что класс принимает и что возвращает.
        >>> class TestingStep(Step[Something, Anything]):

        >>>     # start(), можно переопределить или так:
        >>>     @classmethod
        >>>     def start(data: Something) -> Anything:
        >>>         return Anything()

        >>>     # или так:
        >>>     @classmethod
        >>>     def start(data: Something) -> Generator[Anything, None, None]:

        >>>         some_data_arr = [Anything(), Anything()]

        >>>         for ret in some_data_arr:
        >>>             yield ret

    """

    logger: Logger

    @classmethod
    @abstractmethod
    def start(cls, data: I) -> Union[O, Generator[O, None, None]]:
        """
        Абстрактный классовый метод. Является основной точкой входа для каждого шага.
        В случае если шаг первый первый, то он не должен принимать None в качестве I, а если последний
        то O.

        Arguments:
            data (I): Входные данные, полученные от предыдущего шага пайплайна.

        Returns:
            O или Generator[O, None, None]:
                - Если возвращается O — шаг выполняется один раз и передаёт результат дальше.
                - Если используется yield и возвращается генератор — шаг может передать несколько результатов.

        Особенности yield:
            - Каждый yield запускает все оставшиеся шаги в цепочке, начиная со следующего.
            - После завершения цепочки пайплайн возвращается к текущему шагу и продолжает генератор.
            - Так продолжается, пока генератор не будет исчерпан.
            - Это позволяет реализовать разветвлённую или поэтапную обработку данных с минимальной связностью.

        Пример:

            # Возвращает один результат — шаг завершает выполнение:
            return result

            # Возвращает генератор — шаг вызывает оставшуюся цепочку несколько раз:
            yield part1  # Вся цепочка выполняется с part1
            yield part2  # Затем снова с part2
            yield part3  # И так далее...

        """

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)

        cls._init_logger()
        cls._validate_generic_params()

    @classmethod
    def _init_logger(cls) -> None:
        """Передает наследнику логгер."""
        cls.logger = lm.get_main_step_logger().getChild(cls.__name__)

    @classmethod
    def _validate_generic_params(cls) -> None:
        """Проверяет корректно ли наследник унаследовал Step."""

        # for-else - питоновская кострукция работающая по приниципу:
        # break не было, и цикл завершен - вызов else
        for base in getattr(cls, "__orig_bases__", []):
            # получение обекта класса
            if get_origin(base) is Step:
                # получение аргументов Generic-а
                args = get_args(base)

                # проверка на отсутствие аргументов
                if len(args) == 0:
                    error_msg = f"{cls.__name__} унаследован от Step, но параметры типа не указаны."
                    cls.logger.fatal(error_msg)
                    raise StepTypeParametersMissing(error_msg)

                # проверка на недостаточное или избыточное количество аргументов
                if len(args) != 2:
                    error_msg = f"{cls.__name__} должен наследовать Step с двумя параметрами типа, но получено {len(args)}: {args}"
                    cls.logger.fatal(error_msg)
                    raise StepTypeParameterCountMismatch(error_msg)

                break
        else:
            # если Step[I, O] вообще не нашёлся
            error_msg = f"{cls.__name__} не содержит Step[...] в __orig_bases__."
            cls.logger.fatal(error_msg)
            raise StepTypeExtractionError(error_msg)
