from dataclasses import dataclass


@dataclass
class DispatcherConfigurator:
    THREADS: int
    MAX_TASKS: int
