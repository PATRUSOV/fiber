class TaskBuildError(Exception):
    """Базовое исключение ошибки сборки Task."""


class SequenceIsEmpty(TaskBuildError):
    """Последовательность шагов должна не должна быть пустой"""


class IncompatibleStepTypesError(TaskBuildError):
    """Возвращаемый тип первого шага не совпадает с принимаемым типом второго."""


class InvalidPipelineEndpointsError(TaskBuildError):
    """Первый шаг должен принимать None, а последний возвращать None."""
