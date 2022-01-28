from abc import (ABCMeta, abstractmethod)
import uuid
from collections import defaultdict


class Info:
    """
    Info：回测框架中使用的信息类的基类，此类为抽象类
    """

    __metaclass__ = ABCMeta
    type = None

    @abstractmethod
    def __repr__(self):
        """
        强制要求子类实现__repr__()方法
        """
        raise NotImplementedError("__repr__  not implemented")


class NullInfo(Info):
    """
    空信息，主要用于事件无需传递信息的情形
    """

    def __repr__(self):
        """
        type
        """

        return "NULL"


class BarInfo(Info):
    """
    Bar信息，用于Bar事件中传递以“标的在一定时间段内的报价成交数据”为单位的市场信息
    """

    type = "Bar"
    __slots__ = ["symbol", "datetime", "open", "high", "low", "close", "volume", "turnover"]

    def __init__(self, symbol_: str, datetime_,
                 open_: float, high_: float, low_: float, close_: float, volume_: float, turnover_: float):
        """
        @symbol_(str)：标的代码
        @datetime_(pandas.Timestamp)：信息时间戳

        @open_(float)：开盘价
        @high_(float)：最高价
        @low_(float)：最低价
        @close_(float)：收盘价

        @volume_(float)：成交数量
        @turnover_(float)：成交金额
        """

        self.symbol = symbol_
        self.datetime = datetime_
        self.open = open_
        self.high = high_
        self.low = low_
        self.close = close_
        self.volume = volume_
        self.turnover = turnover_

    def __repr__(self):
        """
        type, datetime, symbol, open, high, low, close, volume, turnover
        """

        return (
            "{:s},{:s},{:s},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f}"
        ).format(self.type, str(self.datetime), self.symbol,
                 self.open, self.high, self.low, self.close, self.volume, self.turnover)


class PriceInfo(Info):
    """
    Price信息，用于Price事件中传递以“标的在一个时刻的价格数据”为单位的市场信息
    """

    type = "Price"
    __slots__ = ["symbol", "datetime", "last_price", "crt_price", "volume"]

    def __init__(self, symbol_: str, datetime_, crt_price_: float, last_price_: float = 0, volume_: float = 0):
        """
        @symbol_(str)：标的代码
        @datetime_(pandas.Timestamp)：信息时间戳

        @crt_price_(float)：现价

        @last_price_(float)：上一个价格，默认为0
        @volume_(float)：成交数量，默认为0
        """

        self.symbol = symbol_
        self.datetime = datetime_
        self.crt_price = crt_price_
        self.last_price = last_price_
        self.volume = volume_

    def __repr__(self):
        """
        type, datetime, symbol, crt_price, last_price, volume
        """

        return (
            "{:s},{:s},{:s},{:.2f},{:.2f},{:.2f}"
        ).format(self.type, str(self.datetime), self.symbol, self.crt_price, self.last_price, self.volume)


# SIGNAL_PRIORITY：记录各类信号的优先级别的全局变量，值越大优先级越高，默认值为0
SIGNAL_PRIORITY = defaultdict(int)

# 信号按照对于信号所包含的交易行为的处理方式进行分类：
# FOK（Fill or Kill）：即时，或者全部转化为委托，或者全部作废
# IOC（Immediate or Cancel）：即时，最大限度转化为委托，其余作废
# FOW（Fill or Wait）：等待直到某一时刻，或者全部转化为委托，或者主动作废
# TBF（to be Fill）：持续有效，直至信息全部转化为委托，或者主动作废
SIGNAL_PRIORITY["FOK"] = 10
SIGNAL_PRIORITY["IOC"] = 20
SIGNAL_PRIORITY["FOW"] = 30
SIGNAL_PRIORITY["TBF"] = 40


class SignalInfo(Info):
    """
    Signal信息，用于Signal事件中传递由交易策略（strategy）发出的交易信号的相关信息
    """

    type = "Signal"
    __slots__ = ["symbol", "datetime", "direction", "open_or_close",
                 "price", "volume", "amount", "currency", "signal_type", "uid"]

    def __init__(self, symbol_: str, datetime_,
                 direction_: int, open_or_close_: int, price_: float, volume_: float,
                 amount_: float = 0, currency_: str = "CNY",
                 signal_type_: str = "FOW", uid_: uuid.UUID = None):
        """
        @symbol_(str)：标的代码
        @datetime_(pandas.Timestamp)：信息时间戳

        @direction_(int)：交易方向，买入为1，卖出为-1
        @open_or_close_(int)：开平仓标志，开仓为1，平仓为-1
        @price_(float)：交易价格
        @volume_(float)：交易数量

        @amount_(float)：预算交易金额，默认为0
        @currency_(str)：交易货币代码，默认为CNY
        @signal_type_(str)：信号分类，默认为FOW
        @uid_(uuid.UUID)：信号ID，默认为None
        """

        self.symbol = symbol_
        self.datetime = datetime_
        self.direction = 1 if direction_ >= 0 else -1
        self.open_or_close = 1 if open_or_close_ >= 0 else -1
        self.price = price_
        self.volume = volume_
        self.amount = amount_
        self.currency = currency_
        self.signal_type = signal_type_
        if uid_ is None:
            self.uid = uuid.uuid4()
        else:
            self.uid = uid_

    def __gt__(self, other):
        """
        比较信号的优先级：分类优先、预算金额较少优先
        """

        self_priority = SIGNAL_PRIORITY[self.signal_type]
        other_priority = SIGNAL_PRIORITY[other.signal_type]

        return (self_priority > other_priority) or (
                self_priority == other_priority and self.amount < other.amount
        )

    def __repr__(self):
        """
        type, datetime, symbol, direction, open_or_close, price, volume, amount, currency, signal_type, uid
        """
        
        return (
            "{:s},{:s},{:s},{:s},{:s},{:.2f},{:.2f},{:.2f},{:s},{:s},{:s}"
        ).format(self.type, str(self.datetime), self.symbol,
                 "买入" if self.direction == 1 else "卖出",
                 "开仓" if self.open_or_close == 1 else "平仓",
                 self.price, self.volume, self.amount, self.currency, self.signal_type, str(self.uid))


# 委托按照交易所撮合系统对于委托的处理方式进行分类：
# FOK（Fill or Kill）：即时，或者全部成交，或者全部撤回
# IOC（Immediate or Cancel）：即时，最大限度成交，其余撤回
# TBF（to be Fill）：持续有效，直至全部成交，或者主动撤回
# GFD（good for day）：当日有效，持续至全部成交，或者主动撤回，或者当日清算时撤回

# SIGNAL_MAP_ORDER：记录由各类信号生成各类委托时的类型映射关系
SIGNAL_MAP_ORDER = dict()

# 考虑到回测系统连续运作的便利性，暂不自动生成GFD委托
SIGNAL_MAP_ORDER["FOK"] = "FOK"
SIGNAL_MAP_ORDER["IOC"] = "IOC"
SIGNAL_MAP_ORDER["FOW"] = "TBF"
SIGNAL_MAP_ORDER["TBF"] = "TBF"


class OrderInfo(Info):
    """
    Order信息，用于Order事件中传递由持仓组合（Portfolio）发出的委托的相关信息
    """

    type = "Order"
    __slots__ = ["uid", "symbol", "datetime", "direction", "open_or_close", "price", "volume", "order_type"]

    def __init__(self, symbol_: str, datetime_, direction_: int, open_or_close_: int, price_: float, volume_: float,
                 uid_: uuid.UUID = None, order_type_: str = "TBF"):
        """
        @symbol_(str)：标的代码
        @datetime_(pandas.Timestamp)：信息时间戳

        @direction_(int)：交易方向，买入为1，卖出为-1
        @open_or_close_(int)：开平仓标志，开仓为1，平仓为-1
        @price_(float)：交易价格
        @volume_(float)：交易数量

        @uid_(uuid.UUID)：委托ID，默认为None
        @order_type_(str)：委托分类，默认为TBF
        """

        self.symbol = symbol_
        self.datetime = datetime_
        self.direction = 1 if direction_ >= 0 else -1
        self.open_or_close = 1 if open_or_close_ >= 0 else -1
        self.price = price_
        self.volume = volume_
        if uid_ is None:
            self.uid = uuid.uuid4()
        else:
            self.uid = uid_
        self.order_type = order_type_

    def get_uuid(self) -> uuid.UUID:
        """
        get_uuid：获取委托信息的ID
        @return(uuid.UUID)：委托信息的ID
        """

        return self.uid

    def __gt__(self, other):
        """
        比较委托的优先级：价格优先、时间优先
        """

        if self.direction != other.direction:
            raise RuntimeWarning("Different direction")

        # 买入方向
        elif self.direction == 1:
            return self.price > other.price or (
                    self.price == other.price and self.datetime < other.datetime
            )

        # 卖出方向
        else:
            return self.price < other.price or (
                    self.price == other.price and self.datetime < other.datetime
            )

    def __repr__(self):
        """
        type, datetime, uid, symbol, direction, open_or_close, price, volume, order_type
        """

        return (
            "{:s},{:s},{:s},{:s},{:s},{:s},{:.2f},{:.2f},{:s}"
        ).format(self.type, str(self.datetime), str(self.uid), self.symbol,
                 "买入" if self.direction == 1 else "卖出",
                 "开仓" if self.open_or_close == 1 else "平仓",
                 self.price, self.volume, self.order_type)


class CancelInfo(Info):
    """
    Cancel信息，用于Cancel事件中传递由持仓组合（portfolio）发出的撤回委托的相关信息
    """

    type = "Cancel"
    __slots__ = ["uid", "symbol", "datetime", "direction"]

    def __init__(self, uid_: uuid.UUID, symbol_: str, datetime_, direction_: int):
        """
        @uid_(uuid.UUID)：委托ID
        @symbol_(str)：标的代码
        @datetime_(pandas.Timestamp)：信息时间戳
        @direction_(int)：交易方向，买入为1，卖出为-1
        """

        self.uid = uid_
        self.symbol = symbol_
        self.datetime = datetime_
        self.direction = 1 if direction_ >= 0 else -1

    def get_uuid(self) -> uuid.UUID:
        """
        get_uuid：获取撤回委托的ID
        @return(uuid.UUID)：撤回委托的ID
        """

        return self.uid

    def __repr__(self):
        """
        type, datetime, uid, symbol, direction
        """

        return (
            "{:s},{:s},{:s},{:s},{:s}"
        ).format(self.type, str(self.datetime), str(self.uid), self.symbol,
                 "买入" if self.direction == 1 else "卖出")


class FillInfo(Info):
    """
    Fill信息，用于Fill事件中传递由交易所（exchange）返回的委托成交的相关信息
    """

    type = "Fill"
    __slots__ = ["uid", "symbol", "datetime", "direction", "open_or_close", "filled_price", "volume", "partial"]

    def __init__(self, uid_: uuid.UUID, symbol_: str, datetime_,
                 direction_: int, open_or_close_: int, filled_price_: float, volume_: float, partial_: bool = False):
        """
        @uid_(uuid.UUID)：委托ID
        @symbol_(str)：标的代码
        @datetime_(pandas.Timestamp)：信息时间戳

        @direction_(int)：交易方向，买入为1，卖出为-1
        @open_or_close_(int)：开平仓标志，开仓为1，平仓为-1
        @filled_price_(float)：成交价格
        @volume_(float)：成交数量

        @partial_(bool)：是否部分成交，默认为False
        """

        self.uid = uid_
        self.symbol = symbol_
        self.datetime = datetime_
        self.direction = 1 if direction_ >= 0 else -1
        self.open_or_close = 1 if open_or_close_ >= 0 else -1
        self.filled_price = filled_price_
        self.volume = volume_
        self.partial = partial_

    def get_uuid(self) -> uuid.UUID:
        """
        get_uuid：获取成交委托的ID
        @return(uuid.UUID)：成交委托的ID
        """

        return self.uid

    def __repr__(self):
        """
        type, datetime, uid, symbol, direction, open_or_close, filled_price, volume, partial
        """

        return (
            "{:s},{:s},{:s},{:s},{:s},{:s},{:.2f},{:.2f},{:s}"
        ).format(self.type, str(self.datetime), str(self.uid), self.symbol,
                 "买入" if self.direction == 1 else "卖出",
                 "开仓" if self.open_or_close == 1 else "平仓",
                 self.filled_price, self.volume, "partial" if self.partial else "")
