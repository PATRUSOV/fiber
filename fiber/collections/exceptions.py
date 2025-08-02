class CallNodeCompileError(Exception): ...


class IncompatibleStepTypesError(CallNodeCompileError):
    """
    Шаги несовместимы по типам данных: выходной тип первого шага
    не совпадает с входным типом второго.
    Используется в статической проверке связности цепочки.
    """

    ...
