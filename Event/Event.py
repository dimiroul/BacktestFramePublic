from abc import (ABCMeta, abstractmethod)
import uuid
from BaseType.Const import CONST
from collections import defaultdict
from Infomation.Info import (Info, NullInfo)

# EVENT_PRIORITY：记录各类事件的优先级别的全局变量，值越大优先级越高，默认值为0
EVENT_PRIORITY = defaultdict(int)

EVENT_PRIORITY["DEFAULT"] = -1
EVENT_PRIORITY["Bar"] = 10
EVENT_PRIORITY["Price"] = 20
EVENT_PRIORITY["Cancel"] = 30
EVENT_PRIORITY["Fill"] = 40
EVENT_PRIORITY["Order"] = 50
EVENT_PRIORITY["Signal"] = 60
EVENT_PRIORITY["Clear"] = 70
EVENT_PRIORITY["END"] = 80

# EVENT_PRIORITY：记录不包含信息的空事件的类型标签
EMPTY_EVENT = {"DEFAULT", "Clear", "END"}


class Event(object):

    __slots__ = ["type", "datetime", "info"]

    def __init__(self, type_: str = "DEFAULT", datetime_=CONST["START_TIME"], info_: Info = NullInfo()):
        """
        @type_(str)：事件分类
        @datetime_(pandas.Timestamp)：信息时间戳
        @info_(Info)：事件包含的信息（信息分类应与事件分类一致）
        """
        self.type = type_
        self.datetime = datetime_

        # 除非事件属于不包含信息的空事件，否则事件分类标签和信息分类标签必须一致
        if self.type in EMPTY_EVENT or self.type == info_.type:
            self.info = info_
        else:
            raise ValueError("Info type not match")

    def __gt__(self, other):
        """
        比较事件的优先级：分类优先、时间优先
        """

        self_priority = EVENT_PRIORITY[self.type]
        other_priority = EVENT_PRIORITY[other.type]

        return self_priority > other_priority or (
                self_priority == other_priority and self.datetime < other.datetime
        )

    def __repr__(self):
        """
        datetime, type, info
        """

        return (
            "{:s},{:s},{:s}"
        ).format(str(self.datetime), self.type, str(self.info))


# 自2022/01/11起失效
# class Event:
#
#     __metaclass__ = ABCMeta
#     type = "DEFAULT"
#     datetime = CONST["START_TIME"]
#
#     def __gt__(self, other):
#         return EVENT_PRIORITY[self.type] > EVENT_PRIORITY[other.type] or (
#                 EVENT_PRIORITY[self.type] == EVENT_PRIORITY[other.type] and self.datetime < other.datetime
#         )
#
#     @abstractmethod
#     def __repr__(self):
#         raise NotImplementedError('__repr__  not implemented')
#
#
# class BarEvent(Event):
#     type = "Bar"
#
#     __slots__ = ["symbol", "datetime", "open", "high", "low", "close", "volume", "turnover"]
#
#     def __init__(self, symbol_: str, datetime_,
#                  open_: float, high_: float, low_: float, close_: float, volume_: float, turnover_: float):
#         self.symbol = symbol_
#         self.datetime = datetime_
#         self.open = open_
#         self.high = high_
#         self.low = low_
#         self.close = close_
#         self.volume = volume_
#         self.turnover = turnover_
#
#     def __repr__(self):
#         return (
#             "Type: {:s}\n"
#             "Symbol: {:s}, Datetime: {:s}\n"
#             "Open: {:.2f}, High: {:.2f}, Low {:.2f}, Close: {:.2f}, Volume: {:.2f}, Turnover: {:.2f}"
#         ).format(self.type, self.symbol, str(self.datetime),
#                  self.open, self.high, self.low, self.close, self.volume, self.turnover)
#
#
# class PriceEvent(Event):
#     type = "Price"
#
#     __slots__ = ["symbol", "datetime", "crt_price", "next_price"]
#
#     def __init__(self, symbol_: str, datetime_, crt_price_: float, next_price_: float = 0):
#         self.symbol = symbol_
#         self.datetime = datetime_
#         self.crt_price = crt_price_
#         self.next_price = next_price_
#
#     def __repr__(self):
#         return (
#             "Type: {:s}\n"
#             "Symbol: {:s}, Datetime: {:s}, CrtPrice: {:.2f}, NextPrice: {:.2f}"
#         ).format(self.type, self.symbol, str(self.datetime), self.crt_price, self.next_price)
#
#
# class ClearEvent(Event):
#     type = "Clear"
#
#     __slots__ = ["datetime"]
#
#     def __init__(self, datetime_):
#         self.datetime = datetime_
#
#     def __repr__(self):
#         return (
#             "Type: {:s}, Datetime: {:s}"
#         ).format(self.type, str(self.datetime))
#
#
# class SignalEvent(Event):
#     type = "Signal"
#
#     __slots__ = ["symbol", "datetime", "direction", "open_or_close", "price", "volume", "signal_type", "uid"]
#
#     def __init__(self, symbol_: str, datetime_,
#                  direction_: int, open_or_close_: int, price_: float, volume_: float,
#                  signal_type_: str = "FOW", uid_: uuid.UUID = None):
#         self.symbol = symbol_
#         self.datetime = datetime_
#         self.direction = 1 if direction_ >= 0 else -1
#         self.open_or_close = 1 if open_or_close_ >= 0 else -1
#         self.price = price_
#         self.volume = volume_
#         self.signal_type = signal_type_
#         self.uid = uid_
#
#     def __repr__(self):
#         return (
#             "Type: {:s}, Uid: {:s}\n"
#             "Symbol: {:s}, Datetime: {:s}, Signal_type: {:s}\n"
#             "Direction: {:s}, Open_or_close: {:s}, Price: {:.2f}, Volume: {:.2f}"
#         ).format(self.type, str(self.uid),
#                  self.symbol, str(self.datetime), self.signal_type,
#                  "买入" if self.direction == 1 else "卖出",
#                  "开仓" if self.open_or_close == 1 else "平仓",
#                  self.price, self.volume)
#
#
# class OrderEvent(Event):
#     type = "Order"
#
#     __slots__ = ["uid", "symbol", "datetime", "direction", "open_or_close", "price", "volume", "order_type"]
#
#     def __init__(self, symbol_: str, datetime_, direction_: int, open_or_close_: int, price_: float, volume_: float,
#                  uid_: uuid.UUID = None, order_type_: str = "GFD"):
#         self.symbol = symbol_
#         self.datetime = datetime_
#         self.direction = 1 if direction_ >= 0 else -1
#         self.open_or_close = 1 if open_or_close_ >= 0 else -1
#         self.price = price_
#         self.volume = volume_
#         if uid_ is None:
#             self.uid = uuid.uuid4()
#         else:
#             self.uid = uid_
#         self.order_type = order_type_
#
#     def get_uuid(self) -> uuid.UUID:
#         return self.uid
#
#     def __repr__(self):
#         return (
#             "Type: {:s}, Uid: {:s}\n"
#             "Symbol: {:s}, Datetime: {:s}, Order_type: {:s}\n"
#             "Direction: {:s}, Open_or_close: {:s}, Price: {:.2f}, Volume: {:.2f}"
#         ).format(self.type, str(self.uid), self.symbol, str(self.datetime), self.order_type,
#                  "买入" if self.direction == 1 else "卖出",
#                  "开仓" if self.open_or_close == 1 else "平仓",
#                  self.price, self.volume)
#
#
# class CancelEvent(Event):
#     type = "Cancel"
#
#     __slots__ = ["uid", "symbol", "datetime", "direction"]
#
#     def __init__(self, uid_: uuid.UUID, symbol_: str, datetime_, direction_: int):
#         self.uid = uid_
#         self.symbol = symbol_
#         self.datetime = datetime_
#         self.direction = 1 if direction_ >= 0 else -1
#
#     def get_uuid(self) -> uuid.UUID:
#         return self.uid
#
#     def __repr__(self):
#         return (
#             "Type: {:s}, Uid: {:g}\n"
#             "Symbol: {:s}, Datetime: {:s}, Direction: {:s}"
#         ).format(self.type, self.uid, self.symbol, str(self.datetime),
#                  "买入" if self.direction == 1 else "卖出")
#
#
# class FillEvent(Event):
#     type = "Fill"
#
#     __slots__ = ["uid", "symbol", "datetime", "direction", "open_or_close", "filled_price", "volume", "partial"]
#
#     def __init__(self, uid_: uuid.UUID, symbol_: str, datetime_,
#                  direction_: int, open_or_close_: int, filled_price_: float, volume_: float, partial_: bool = False):
#         self.uid = uid_
#         self.symbol = symbol_
#         self.datetime = datetime_
#         self.direction = 1 if direction_ >= 0 else -1
#         self.open_or_close = 1 if open_or_close_ >= 0 else -1
#         self.filled_price = filled_price_
#         self.volume = volume_
#         self.partial = partial_
#
#     def get_uuid(self) -> uuid.UUID:
#         return self.uid
#
#     def __repr__(self):
#         return (
#             "Type: {:s}, Uid: {:s}\n"
#             "Symbol: {:s}, Datetime: {:s}, {:s}\n"
#             "Direction: {:s}, Open_or_close: {:s}, Price: {:.2f}, Volume: {:.2f}"
#         ).format(self.type, str(self.uid),
#                  self.symbol, str(self.datetime), "partial" if self.partial else "",
#                  "买入" if self.direction == 1 else "卖出",
#                  "开仓" if self.open_or_close == 1 else "平仓",
#                  self.filled_price, self.volume)
#
#
# class END(Event):
#     type = "END"
#     datetime = CONST["END_TIME"]
#
#     def __repr__(self):
#         return "Type: {}".format(self.type)
