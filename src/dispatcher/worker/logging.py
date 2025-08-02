import src.logman as lm

from logging import Logger

worker_counter = 0


def get_worker_logger() -> Logger:
    """
    Функция выдвает логгер для Worker(), ведет учет количества
    логгер и при создании увиличивает глобальную переменную worker_counter.

    Returns:
        Logger унаследованный от логера ядра.
    """
    global worker_counter
    kernel_logger = lm.get_kernel_logger()
    worker_logger = kernel_logger.getChild(f"worker-{worker_counter}")
    worker_counter += 1
    return worker_logger
