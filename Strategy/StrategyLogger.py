from Logger.Logger import (LoggerUnit, Logger)
from abc import (ABCMeta, abstractmethod)
from Strategy.StrategyUnion import PseudoStrategyUnit


class StrategyLoggerUnit(LoggerUnit):

    @abstractmethod
    def log(self, strategy: PseudoStrategyUnit, committer: str):
        raise NotImplementedError("log not implemented")


class StrategyLogger(Logger):

    def __init__(self):
        super().__init__()
