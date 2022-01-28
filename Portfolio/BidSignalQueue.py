import uuid
from BaseType.PriorityQueue import PriorityQueue
from Information.Info import (SignalInfo)


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
