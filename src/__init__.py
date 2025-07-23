__version__ = "0.3.0"
__author__ = "kotmarkot"
__appname__ = "Fiber"

__all__ = []

import src.logman as lm

from logging import Formatter, StreamHandler

stream_hdlr = StreamHandler()
stream_hdlr.setFormatter(
    Formatter("%(asctime)s - %(levelname)s - %(name)s - %(lineno)d - %(message)s")
)
lm.get_main_logger().addHandler(stream_hdlr)
