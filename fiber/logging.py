import logging


_main_logger = None


def get_main_logger() -> logging.Logger:
    """
    Возвращает:
        Логгер для всего приложения.
    """
    global _main_logger

    if _main_logger is None:
        import fiber

        logger = logging.getLogger(fiber.__appname__)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False

        from colorama import Fore, Style, init

        class ColoredFormatter(logging.Formatter):
            COLOR_MAP = {
                logging.DEBUG: Fore.CYAN,
                logging.INFO: Fore.GREEN,
                logging.WARNING: Fore.YELLOW,
                logging.ERROR: Fore.RED,
                logging.CRITICAL: Fore.RED + Style.BRIGHT,
                logging.FATAL: Fore.RED + Style.DIM,
            }

            def format(self, record: logging.LogRecord):
                color = self.COLOR_MAP.get(record.levelno, "")
                record.name = record.name.upper()
                record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
                record.msg = f"{color}{record.getMessage()}{Style.RESET_ALL}"
                return super().format(record)

        init(autoreset=True)

        hdlr = logging.StreamHandler()

        formatter = ColoredFormatter(
            fmt="[%(name)s] %(asctime)s | %(levelname)s | %(message)s",
            datefmt="%H:%M:%S",
        )
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)

        _main_logger = logger

    return _main_logger


def get_main_step_logger() -> logging.Logger:
    """
    Возвращает:
        Базовый логгер для от которого наследуются логгеры для каждого Step.
    """
    return get_main_logger().getChild("step")


def get_kernel_logger() -> logging.Logger:
    """
    Возвращает:
        Логгер используемый "под капотом" у фремворка.
    """
    return get_main_logger().getChild("kernel")
