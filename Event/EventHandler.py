from Event.Event import Event
from abc import (ABCMeta, abstractmethod)


class DEFAULTHandler:
    """
    针对处理DEFAULT事件的接口类
    """

    __metaclass__ = ABCMeta
    _name = "DEFAULTHandler"

    @abstractmethod
    def on_default(self, event: Event) -> None:
        """
        强制要求包含DEFAULTHandler接口的子类实现on_default方法
        """

        raise NotImplementedError("on_default not implemented")


class ENDHandler:
    """
    针对处理END事件的接口类
    """

    __metaclass__ = ABCMeta
    _name = "ENDHandler"

    @abstractmethod
    def on_end(self, event: Event) -> None:
        """
        强制要求包含ENDHandler接口的子类实现on_end方法
        """

        raise NotImplementedError("on_end not implemented")


class BarHandler:
    """
    针对处理Bar事件的接口类
    """

    __metaclass__ = ABCMeta
    _name = "BarHandler"

    @abstractmethod
    def on_bar(self, event: Event) -> None:
        """
        强制要求包含BarHandler接口的子类实现on_bar方法
        """

        raise NotImplementedError("on_bar not implemented")


class PriceHandler:
    """
    针对处理Price事件的接口类
    """

    __metaclass__ = ABCMeta
    _name = "PriceHandler"

    @abstractmethod
    def on_price(self, event: Event) -> None:
        """
        强制要求包含PriceHandler接口的子类实现on_price方法
        """

        raise NotImplementedError("on_price not implemented")


class ClearHandler:
    """
    针对处理Clear事件的接口类
    """

    __metaclass__ = ABCMeta
    _name = "ClearHandler"

    @abstractmethod
    def on_clear(self, event: Event) -> None:
        """
        强制要求包含ClearHandler接口的子类实现on_clear方法
        """

        raise NotImplementedError("on_clear not implemented")


class SignalHandler:
    """
    针对处理Signal事件的接口类
    """

    __metaclass__ = ABCMeta
    _name = "SignalHandler"

    @abstractmethod
    def on_signal(self, event: Event) -> None:
        """
        强制要求包含SignalHandler接口的子类实现on_signal方法
        """

        raise NotImplementedError("on_signal not implemented")


class OrderHandler:
    """
    针对处理Order事件的接口类
    """

    __metaclass__ = ABCMeta
    _name = "OrderHandler"

    @abstractmethod
    def on_order(self, event: Event) -> None:
        """
        强制要求包含OrderHandler接口的子类实现on_order方法
        """

        raise NotImplementedError("on_order not implemented")


class CancelHandler:
    """
    针对处理Cancel事件的接口类
    """

    __metaclass__ = ABCMeta
    _name = "CancelHandler"

    @abstractmethod
    def on_cancel(self, event: Event) -> None:
        """
        强制要求包含CancelHandler接口的子类实现on_cancel方法
        """

        raise NotImplementedError("on_cancel not implemented")


class FillHandler:
    """
    针对处理Fill事件的接口类
    """

    __metaclass__ = ABCMeta
    _name = "FillHandler"

    @abstractmethod
    def on_fill(self, event: Event) -> None:
        """
        强制要求包含FillHandler接口的子类实现on_fill方法
        """

        raise NotImplementedError("on_fill not implemented")
