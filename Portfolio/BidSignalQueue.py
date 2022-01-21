import uuid
from BaseType.PriorityQueue import PriorityQueue
from collections import defaultdict
from Infomation.Info import (SignalInfo, SIGNAL_PRIORITY, SIGNAL_MAP_ORDER)

# 自2022/01/11起失效
# SIGNAL_PRIORITY = defaultdict(int)
#
# SIGNAL_PRIORITY["FOK"] = 0
# SIGNAL_PRIORITY["IOC"] = 1
# SIGNAL_PRIORITY["FOW"] = 2
# SIGNAL_PRIORITY["TBF"] = 3
#
# SIGNAL_MAP_ORDER = dict()
#
# SIGNAL_MAP_ORDER["FOK"] = "TBF"
# SIGNAL_MAP_ORDER["IOC"] = "TBF"
# SIGNAL_MAP_ORDER["FOW"] = "TBF"
# SIGNAL_MAP_ORDER["TBF"] = "TBF"


# 自2022/01/11起失效
# class BidSignal:
#
#     __slots__ = ["uid", "symbol", "price", "volume", "amount", "currency", "type", "open_or_close"]
#
#     def __init__(self, uid_: uuid.UUID = None, symbol_: str = "",
#                  price_: float = 0, volume_: float = 0, amount_: float = 0, currency_: str = "CNY",
#                  type_: str = "IOC", open_or_close_: int = 1):
#         self.uid = uid_
#         self.symbol = symbol_
#         self.price = price_
#         self.volume = volume_
#         self.amount = amount_
#         self.currency = currency_
#         self.type = type_
#         self.open_or_close = open_or_close_
#
#     def __gt__(self, other):
#         return (SIGNAL_PRIORITY[self.type] > SIGNAL_PRIORITY[other.type]) or (
#                 SIGNAL_PRIORITY[self.type] == SIGNAL_PRIORITY[other.type] and self.amount < other.amount
#         )
#
#     def __repr__(self):
#         return "uid: {:s}: {:s} 买入{:s} {:s} price: {:.2f}, volume: {:.2f}, amount: {:s} {:2f}".format(
#             str(self.uid), self.type,
#             "开仓" if self.open_or_close == 1 else "平仓", self.symbol,
#             self.price, self.volume, self.currency, self.amount)


class BidSignalQueue(PriorityQueue):
    """
    BidSignalQueue(PriorityQueue)：投资组合（Portfolio）进行买入信号资金分配时使用的信号（Signal）优先队列
    """

    def __init__(self):
        # super().__init__(factory_=BidSignal)
        super().__init__(factory_=SignalInfo)

    def put(self, s: SignalInfo) -> None:

        # 仅当信号的交易方向为买入时，才将信号放入分配队列
        if s.direction == 1:
            super().put(s)

    def cancel(self, uid_: uuid.UUID):
        """
        cancel：根据给定的信号ID撤销对应信号
        @uid_(uuid.UUID)：信号ID
        @return(None)
        """

        # for i in range(self.max_index+1):
        #     if self.heap[i].uid == uid_:
        #         self.pop(i)
        #         break

        i = 0
        while i <= self.max_index:
            if self.heap[i].uid == uid_:
                self.pop(i)
            else:
                i += 1
