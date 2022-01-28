import uuid
from BaseType.PriorityQueue import PriorityQueue
from Information.Info import OrderInfo


class OrderQueue(PriorityQueue):
    """
    OrderQueue(PriorityQueue)：交易所（Exchange）进行委托撮合时使用的委托优先队列
    """

    __slots__ = ["symbol", "direction"]

    def __init__(self, symbol_: str, direction_: str):
        """
        @symbol_(str)：标的代码
        @direction_(str)：交易方向，买入/卖出
        """

        super().__init__(factory_=OrderInfo)
        self.symbol = symbol_
        self.direction = 1 if direction_ == "买入" else -1

    def put(self, o: OrderInfo) -> None:

        # 仅当委托标的代码、交易方向均与委托队列一致时，才将委托放入撮合队列
        if o.symbol == self.symbol and o.direction == self.direction:
            super().put(o)

    def cancel(self, uid_: uuid.UUID) -> None:
        """
        cancel：根据给定的委托ID撤销对应委托
        @uid_(uuid.UUID)：委托ID
        @return(None)
        """

        i = 0
        while i <= self.max_index:
            if self.heap[i].uid == uid_:
                self.pop(i)
            else:
                i += 1

    def __repr__(self):
        if self.max_index < 0:
            return "Empty Queue"
        else:
            return (
                "Symbol: {:s}, Direction: {:s}: \n"
                "{:s}"
            ).format(self.symbol, "买入" if self.direction == 1 else "卖出",
                     "\n".join(str(self.heap[i]) for i in range(self.max_index + 1)))

    def cross(self, crt_price_: float):
        """
        cross：根据给定的现价进行交易撮合
        @crt_price_(float)：现价
        @return(Generator)：包含成交委托的生成器，根据成交顺序排列
        """

        # 仅根据现价与委托价格判断是否成交，暂不考虑委托数量与当前盘口的关系
        if self.direction == 1:
            while not self.is_empty() and self.heap[0].price >= crt_price_:
                yield self.pop()
        else:
            while not self.is_empty() and self.heap[0].price <= crt_price_:
                yield self.pop()
