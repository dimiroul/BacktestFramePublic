from Logger.Logger import (LoggerUnit, Logger)
from abc import (ABCMeta, abstractmethod)
from Portfolio.HoldingUnion import (HoldingUnion, PseudoHoldingUnit)


class HoldingLoggerUnit(LoggerUnit):

    @abstractmethod
    def log(self, holding: PseudoHoldingUnit, committer: str):
        raise NotImplementedError("log not implemented")


class PortfolioLoggerUnit(LoggerUnit):

    @abstractmethod
    def log(self, portfolio: HoldingUnion, committer: str):
        raise NotImplementedError("log not implemented")


class HoldingLogger(Logger):

    def __init__(self):
        super().__init__()
