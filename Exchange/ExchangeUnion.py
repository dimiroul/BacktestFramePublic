from BaseType.Subject import Subject
# import Event.Event as Event
from Event.Event import Event
from Event.EventHandler import (BarHandler, PriceHandler, OrderHandler, CancelHandler, ClearHandler, ENDHandler)
from Event.EventQueue import EVENT_QUEUE
from Exchange.OrderQueue import OrderQueue
from pandas.tseries.offsets import DateOffset
# from Event.EventLogger import EVENT_LOGGER
from BaseType.Const import CONST
import Infomation.Info as Info


def day_bar_slicer(bar: Info.BarInfo):
    """
    day_bar_slicer：将给定的标的以交易日为单位的报价成交数据切片，转换成多个包含“标的在一个时刻的价格数据”信息的Price事件
    @bar(Info.BarInfo)：给定的标的以交易日为单位的报价成交数据
    @return(Generator)：包含“标的在一个时刻的价格数据”信息的Price事件的生成器，以时间戳顺序排列
    """

    datetime_ = bar.datetime

    # 将开盘价、收盘价、最高价、最低价依次指定给交易日的时点：09:30、11：30、13:00、15:00
    # 如果开盘价不高于收盘价，则采用开盘价、最低价、最高价、收盘价的顺序
    # 如果开盘价高于收盘价，则采用开盘价、最高价、最低价、收盘价的顺序
    if bar.open <= bar.close:
        datetime_ += DateOffset(minutes=570)
        yield Event(type_="Price", datetime_=datetime_,
                    info_=Info.PriceInfo(symbol_=bar.symbol, datetime_=datetime_, crt_price_=bar.open))
        datetime_ += DateOffset(minutes=120)
        yield Event(type_="Price", datetime_=datetime_,
                    info_=Info.PriceInfo(symbol_=bar.symbol, datetime_=datetime_, crt_price_=bar.low))
        datetime_ += DateOffset(minutes=90)
        yield Event(type_="Price", datetime_=datetime_,
                    info_=Info.PriceInfo(symbol_=bar.symbol, datetime_=datetime_, crt_price_=bar.high))
    else:
        datetime_ += DateOffset(minutes=570)
        yield Event(type_="Price", datetime_=datetime_,
                    info_=Info.PriceInfo(symbol_=bar.symbol, datetime_=datetime_, crt_price_=bar.open))
        datetime_ += DateOffset(minutes=120)
        yield Event(type_="Price", datetime_=datetime_,
                    info_=Info.PriceInfo(symbol_=bar.symbol, datetime_=datetime_, crt_price_=bar.high))
        datetime_ += DateOffset(minutes=90)
        yield Event(type_="Price", datetime_=datetime_,
                    info_=Info.PriceInfo(symbol_=bar.symbol, datetime_=datetime_, crt_price_=bar.low))
    datetime_ += DateOffset(minutes=120)
    yield Event(type_="Price", datetime_=datetime_,
                info_=Info.PriceInfo(symbol_=bar.symbol, datetime_=datetime_, crt_price_=bar.close))


def minute_bar_slicer(bar: Info.BarInfo):
    """
    minute_bar_slicer：将给定的标的以1分钟为单位的报价成交数据切片，转换成多个包含“标的在一个时刻的价格数据”信息的Price事件
    @bar(Info.BarInfo)：给定的标的以1分钟为单位的报价成交数据
    @return(Generator)：包含“标的在一个时刻的价格数据”信息的Price事件的生成器，以时间戳顺序排列
    """

    datetime_ = bar.datetime

    # 将开盘价、收盘价、最高价、最低价依次指定给1分钟内的时点：+0S、+15S、+30S、+45S
    # 如果开盘价不高于收盘价，则采用开盘价、最低价、最高价、收盘价的顺序
    # 如果开盘价高于收盘价，则采用开盘价、最高价、最低价、收盘价的顺序
    if bar.open <= bar.close:
        datetime_ += DateOffset(seconds=0)
        yield Event(type_="Price", datetime_=datetime_,
                    info_=Info.PriceInfo(symbol_=bar.symbol, datetime_=datetime_, crt_price_=bar.open))
        datetime_ += DateOffset(seconds=15)
        yield Event(type_="Price", datetime_=datetime_,
                    info_=Info.PriceInfo(symbol_=bar.symbol, datetime_=datetime_, crt_price_=bar.low))
        datetime_ += DateOffset(seconds=15)
        yield Event(type_="Price", datetime_=datetime_,
                    info_=Info.PriceInfo(symbol_=bar.symbol, datetime_=datetime_, crt_price_=bar.high))
    else:
        datetime_ += DateOffset(seconds=0)
        yield Event(type_="Price", datetime_=datetime_,
                    info_=Info.PriceInfo(symbol_=bar.symbol, datetime_=datetime_, crt_price_=bar.open))
        datetime_ += DateOffset(seconds=15)
        yield Event(type_="Price", datetime_=datetime_,
                    info_=Info.PriceInfo(symbol_=bar.symbol, datetime_=datetime_, crt_price_=bar.high))
        datetime_ += DateOffset(seconds=15)
        yield Event(type_="Price", datetime_=datetime_,
                    info_=Info.PriceInfo(symbol_=bar.symbol, datetime_=datetime_, crt_price_=bar.low))
    datetime_ += DateOffset(seconds=15)
    yield Event(type_="Price", datetime_=datetime_,
                info_=Info.PriceInfo(symbol_=bar.symbol, datetime_=datetime_, crt_price_=bar.close))


def order_to_fill(order_: Info.OrderInfo, datetime_,
                  filled_price_: float = None, volume_: float = None) -> Info.FillInfo:
    """
    order_to_fill：根据给定的交易委托信息（OrderInfo）、成交时间、成交价格、成交数量，生成委托成交信息（FillInfo）
    @order_(Info.OrderInfo)：给定的交易委托信息（OrderInfo）
    @datetime_(pandas.Timestamp)：给定的成交时间
    @filled_price_(float)：给定的成交价格，默认为None
    @volume_(float)：给定的成交数量，默认为None
    @return(Info.FillInfo)：生成委托成交信息（FillInfo）
    """

    # 如果没有提供成交价格或成交数量，则使用交易委托信息（OrderInfo）中的成交价格或成交数量
    if filled_price_ is None:
        filled_price_ = order_.price
    if volume_ is None:
        volume_ = order_.volume

    return Info.FillInfo(uid_=order_.uid, symbol_=order_.symbol, datetime_=datetime_,
                         direction_=order_.direction, open_or_close_=order_.open_or_close,
                         filled_price_=filled_price_, volume_=volume_)


class PseudoExchangeUnit(Subject, BarHandler, PriceHandler, OrderHandler, CancelHandler, ClearHandler, ENDHandler):
    """
    PseudoExchangeUnit(Subject, BarHandler, PriceHandler, OrderHandler, CancelHandler, ClearHandler, ENDHandler)：
    回测框架中，交易所（Exchange）体系中使用的以标的为单位的交易模块
    可处理事件：Bar、Price、Order、Cancel、Clear、END
    除了常规的通过参数进行初始化的方式外，提供了三种简化的初始化方式：
    分别通过BarInfo、PriceInfo、OrderInfo进行初始化
    """

    _name = "PseudoExchangeUnit"
    __slots__ = ["crt_price", "last_price", "last_datetime", "last_bar", "bar_slicer"]

    def __init__(self, bar: Info.BarInfo = None, price: Info.PriceInfo = None, order: Info.OrderInfo = None,
                 symbol_: str = CONST["SYMBOL"], exchange_: str = CONST["EXCHANGE"],
                 last_datetime_=CONST["START_TIME"],
                 per_hand_: int = CONST["PER_HAND"], per_price_: float = CONST["PER_PRICE"],
                 bid_commission_: float = CONST["BID_COMMISSION"],
                 bid_commission_rate_: float = CONST["BID_COMMISSION_RATE"],
                 ask_commission_: float = CONST["ASK_COMMISSION"],
                 ask_commission_rate_: float = CONST["ASK_COMMISSION_RATE"],
                 bid_tax_: float = CONST["BID_TAX"], bid_tax_rate_: float = CONST["BID_TAX_RATE"],
                 ask_tax_: float = CONST["ASK_TAX"], ask_tax_rate_: float = CONST["ASK_TAX_RATE"],
                 crt_price_: float = CONST["CRT_PRICE"], net_price_: float = CONST["NET_PRICE"],
                 book_value_: float = CONST["BOOK_VALUE"], volume_: float = CONST["VOLUME"],
                 multiplier_: int = CONST["MULTIPLIER"], margin_rate_: float = CONST["MARGIN_RATE"],
                 currency_: str = CONST["CURRENCY"], bar_slicer_=minute_bar_slicer):
        """
        @bar(Info.BarInfo)：用于初始化的Bar信息，默认为None
        @price(Info.PriceInfo)：用于初始化的Price信息，默认为None
        @order(Info.OrderInfo)：用于初始化的Order信息，默认为None

        @symbol_(str)：标的代码，默认为CONST["SYMBOL"]
        @exchange_(str)：交易所，默认为CONST["EXCHANGE"]
        @last_datetime_(pandas.Timestamp)：最新时间戳，默认为CONST["START_TIME"]
        @per_hand_(int)：每手数量，默认为CONST["PER_HAND"]
        @per_price_(int)：报价单位，默认为CONST["PER_PRICE"]

        @bid_commission_(float)：买入费用定额，默认为CONST["BID_COMMISSION"]
        @bid_commission_rate_(float)：买入费用费率，默认为CONST["BID_COMMISSION_RATE"]
        @ask_commission_(float)：卖出费用定额，默认为CONST["ASK_COMMISSION"]
        @ask_commission_rate_(float)：卖出费用费率，默认为CONST["ASK_COMMISSION_RATE"]
        @bid_tax_(float)：买入缴税定额，默认为CONST["BID_TAX"]
        @bid_tax_rate_(float)：买入缴税税率，默认为CONST["BID_TAX_RATE"]
        @ask_tax_(float)：卖出缴税定额，默认为CONST["ASK_TAX"]
        @ask_tax_rate_(float)：卖出缴税税率，默认为CONST["ASK_TAX_RATE"]

        @crt_price_(float)：单位现价，默认为CONST["CRT_PRICE"]
        @net_price_(float)：单位净值，默认为CONST["NET_PRICE"]
        @book_value_(float)：单位面值，默认为CONST["BOOK_VALUE"]
        @volume_(float)：当前数量，默认为CONST["VOLUME"]
        @multiplier_(int)：乘数，默认为CONST["MULTIPLIER"]
        @margin_rate_(float)：保证金比率，默认为CONST["MARGIN_RATE"]

        @currency_(str)：货币代码，默认为CONST["CURRENCY"]

        @bar_slicer_(BarInfo->Iterable[Event])：Bar信息到Price事件的切片器，默认为minute_bar_slicer
        """

        self.bar_slicer = bar_slicer_

        # 如果提供了Bar信息，则通过Bar信息初始化
        if bar is not None:
            super().__init__(symbol_=bar.symbol, exchange_=bar.symbol[-2:], last_datetime_=bar.datetime,
                             per_hand_=per_hand_, per_price_=per_price_, bid_commission_=bid_commission_,
                             bid_commission_rate_=bid_commission_rate_, ask_commission_=ask_commission_,
                             ask_commission_rate_=ask_commission_rate_, bid_tax_=bid_tax_, bid_tax_rate_=bid_tax_rate_,
                             ask_tax_=ask_tax_, ask_tax_rate_=ask_tax_rate_, crt_price_=bar.close,
                             net_price_=net_price_, book_value_=book_value_, volume_=volume_, multiplier_=multiplier_,
                             margin_rate_=margin_rate_, currency_=currency_)

            self._name = "ExchangeUnit_{:s}".format(bar.symbol)
            self.last_price = bar.close
            self.last_bar = bar

        # 如果提供了Price信息，则通过Price信息初始化
        elif price is not None:
            super().__init__(symbol_=price.symbol, exchange_=price.symbol[-2:], last_datetime_=price.datetime,
                             per_hand_=per_hand_, per_price_=per_price_, bid_commission_=bid_commission_,
                             bid_commission_rate_=bid_commission_rate_, ask_commission_=ask_commission_,
                             ask_commission_rate_=ask_commission_rate_, bid_tax_=bid_tax_, bid_tax_rate_=bid_tax_rate_,
                             ask_tax_=ask_tax_, ask_tax_rate_=ask_tax_rate_, crt_price_=price.crt_price,
                             net_price_=net_price_, book_value_=book_value_, volume_=volume_, multiplier_=multiplier_,
                             margin_rate_=margin_rate_, currency_=currency_)
            self._name = "ExchangeUnit_{:s}".format(price.symbol)
            self.last_price = price.crt_price
            self.last_bar = None

        # 如果提供了Order信息，则通过Order信息初始化，同时记录对Order事件的处理
        elif order is not None:
            super().__init__(symbol_=order.symbol, exchange_=order.symbol[-2:], last_datetime_=order.datetime,
                             per_hand_=per_hand_, per_price_=per_price_, bid_commission_=bid_commission_,
                             bid_commission_rate_=bid_commission_rate_, ask_commission_=ask_commission_,
                             ask_commission_rate_=ask_commission_rate_, bid_tax_=bid_tax_, bid_tax_rate_=bid_tax_rate_,
                             ask_tax_=ask_tax_, ask_tax_rate_=ask_tax_rate_, crt_price_=crt_price_,
                             net_price_=net_price_, book_value_=book_value_, volume_=volume_, multiplier_=multiplier_,
                             margin_rate_=margin_rate_, currency_=currency_)
            self._name = "ExchangeUnit_{:s}".format(order.symbol)
            # EVENT_LOGGER.log(obj=order, committer=self._name, date_time_=self.last_datetime)

            self.last_price = self.crt_price
            self.last_bar = None

        # 如果上述信息均未提供，则进行常规的参数初始化
        else:
            super().__init__(symbol_=symbol_, exchange_=exchange_, last_datetime_=last_datetime_, per_hand_=per_hand_,
                             per_price_=per_price_, bid_commission_=bid_commission_,
                             bid_commission_rate_=bid_commission_rate_, ask_commission_=ask_commission_,
                             ask_commission_rate_=ask_commission_rate_, bid_tax_=bid_tax_, bid_tax_rate_=bid_tax_rate_,
                             ask_tax_=ask_tax_, ask_tax_rate_=ask_tax_rate_, crt_price_=crt_price_,
                             net_price_=net_price_, book_value_=book_value_, volume_=volume_, multiplier_=multiplier_,
                             margin_rate_=margin_rate_, currency_=currency_)

            self.last_price = self.crt_price
            self.last_bar = None

        # 买入委托、卖出委托的撮合队列
        self.bid_queue = OrderQueue(self.symbol, "买入")
        self.ask_queue = OrderQueue(self.symbol, "卖出")

        # if order is not None:
        #     tmp_order = Order(order)
        #     if tmp_order.direction == 1:
        #         self.bid_queue.put(tmp_order)
        #     else:
        #         self.ask_queue.put(tmp_order)

        # 如果提供了Order信息，则将Order信息放入委托撮合队列
        if order is not None:
            if order.direction == 1:
                self.bid_queue.put(order)
            else:
                self.ask_queue.put(order)

    def cross(self) -> None:
        """
        cross：当前交易模块进行交易撮合，成交结果作为Fill事件放入事件队列
        @return(None)
        """

        # if self.crt_price != 0 and self.crt_price < self.last_price:
        #     # tmp_order: Order = self.bid_queue.first()
        #     # while tmp_order.valid and tmp_order.price >= self.crt_price:
        #     #     self.time_offset()
        #     #     EVENT_QUEUE.put(Event.FillEvent(uid_=tmp_order.uid, symbol_=self.symbol, datetime_=self.last_datetime,
        #     #                                     direction_=tmp_order.direction, open_or_close_=tmp_order.open_or_close,
        #     #                                     filled_price_=tmp_order.price, volume_=tmp_order.volume))
        #     #     self.bid_queue.pop()
        #     #     tmp_order: Order = self.bid_queue.first()
        #
        #     while not self.bid_queue.is_empty() and self.bid_queue.heap[0].price >= self.crt_price:
        #         self.time_offset()
        #         tmp_order: Order = self.bid_queue.pop()
        #         EVENT_QUEUE.put(Event.FillEvent(uid_=tmp_order.uid, symbol_=self.symbol, datetime_=self.last_datetime,
        #                                         direction_=tmp_order.direction, open_or_close_=tmp_order.open_or_close,
        #                                         filled_price_=tmp_order.price, volume_=tmp_order.volume))
        #
        # if self.crt_price != 0 and self.crt_price > self.last_price:
        #     # tmp_order: Order = self.ask_queue.first()
        #     # while tmp_order.valid and tmp_order.price <= self.crt_price:
        #     #     self.time_offset()
        #     #     EVENT_QUEUE.put(Event.FillEvent(uid_=tmp_order.uid, symbol_=self.symbol, datetime_=self.last_datetime,
        #     #                                     direction_=tmp_order.direction, open_or_close_=tmp_order.open_or_close,
        #     #                                     filled_price_=tmp_order.price, volume_=tmp_order.volume))
        #     #     self.ask_queue.pop()
        #     #     tmp_order: Order = self.ask_queue.first()
        #
        #     while not self.ask_queue.is_empty() and self.ask_queue.heap[0].price <= self.crt_price:
        #         self.time_offset()
        #         tmp_order: Order = self.ask_queue.pop()
        #         EVENT_QUEUE.put(Event.FillEvent(uid_=tmp_order.uid, symbol_=self.symbol, datetime_=self.last_datetime,
        #                                         direction_=tmp_order.direction, open_or_close_=tmp_order.open_or_close,
        #                                         filled_price_=tmp_order.price, volume_=tmp_order.volume))

        # 如果没有现价（crt_price）数据，则不进行撮合
        if self.crt_price == 0:
            return

        # 如果现价（crt_price）低于前一价格（last_price），则对买入委托队列进行撮合
        if self.crt_price < self.last_price:
            for order_ in self.bid_queue.cross(crt_price_=self.crt_price):
                self.time_offset()
                EVENT_QUEUE.put(Event(type_="Fill", datetime_=self.last_datetime,
                                      info_=order_to_fill(order_=order_, datetime_=self.last_datetime)))

        # 如果现价（crt_price）高于前一价格（last_price），则对卖出委托队列进行撮合
        if self.crt_price > self.last_price:
            for order_ in self.ask_queue.cross(crt_price_=self.crt_price):
                self.time_offset()
                EVENT_QUEUE.put(Event(type_="Fill", datetime_=self.last_datetime,
                                      info_=order_to_fill(order_=order_, datetime_=self.last_datetime)))

    def on_bar(self, event: Event) -> None:
        """
        on_bar：接收并处理Bar事件
        @event(Event)：接收的Bar事件
        @return(None)
        """
        # EVENT_LOGGER.log(obj=order, committer=self._name, date_time_=self.last_datetime)

        bar: Info.BarInfo = event.info
        # EVENT_LOGGER.log(obj=bar, committer=self._name, date_time_=self.last_datetime)

        self.last_datetime = bar.datetime
        self.last_bar = bar

        # 使用bar_slicer方法，将Bar事件包含的信息拆分为若干个Price事件并放入事件队列
        for price in self.bar_slicer(bar):
            EVENT_QUEUE.put(price)

    def on_price(self, event: Event) -> None:
        """
        on_price：接收并处理Price事件
        @event(Event)：接收的Price事件
        @return(None)
        """
        # EVENT_LOGGER.log(event, event.type, self._name)

        price: Info.PriceInfo = event.info
        # EVENT_LOGGER.log(obj=price, committer=self._name, date_time_=self.last_datetime)

        self.last_datetime = price.datetime
        self.last_price = self.crt_price
        self.crt_price = price.crt_price

        # 根据Price事件包含的信息更新后，进行一次撮合
        self.cross()

    def on_order(self, event: Event) -> None:
        """
        on_order：接收并处理Order事件，注意默认设计不区分委托类别，统一按照TBF类型处理
        @event(Event)：接收的Order事件
        @return(None)
        """
        # EVENT_LOGGER.log(event, event.type, self._name)

        order: Info.OrderInfo = event.info
        # EVENT_LOGGER.log(obj=order, committer=self._name, date_time_=self.last_datetime)

        self.last_datetime = order.datetime

        # 如果Order信息包含的委托可以即时成交，则将成交结果作为Fill事件放入事件队列
        if self.crt_price != 0 and ((order.direction == 1 and order.price >= self.crt_price) or
                                    (order.direction == -1 and order.price <= self.crt_price)):
            self.time_offset()
            EVENT_QUEUE.put(Event(type_="Fill", datetime_=self.last_datetime,
                                  info_=order_to_fill(order_=order, datetime_=self.last_datetime)))

        # 否则，根据交易方向放入对应的交易委托队列，等待撮合
        elif order.direction == 1:
            self.bid_queue.put(order)
        else:
            self.ask_queue.put(order)

    def on_cancel(self, event: Event) -> None:
        """
        on_cancel：接收并处理Cancel事件
        @event(Event)：接收的Cancel事件
        @return(None)
        """
        # EVENT_LOGGER.log(event, event.type, self._name)

        cancel: Info.CancelInfo = event.info
        # EVENT_LOGGER.log(obj=cancel, committer=self._name, date_time_=self.last_datetime)

        # 根据Cancel事件中包含的交易委托ID，从交易委托队列中撤回对应委托
        self.last_datetime = cancel.datetime
        if cancel.direction == 1:
            self.bid_queue.cancel(cancel.uid)
        else:
            self.ask_queue.cancel(cancel.uid)

    def on_clear(self, event: Event) -> None:
        """
        on_clear：接收并处理Clear事件
        @event(Event)：接收的Clear事件
        @return(None)
        """

        pass

    def on_end(self, event: Event) -> None:
        """
        on_end：接收并处理END事件
        @event(Event)：接收的END事件
        @return(None)
        """

        pass

    def cancel_all(self):
        """
        cancel_all：撤回当前交易委托队列中的所有委托
        @return(None)
        """

        self.bid_queue.clear()
        self.ask_queue.clear()


class ExchangeUnion(BarHandler, PriceHandler, OrderHandler, CancelHandler, ClearHandler, ENDHandler):
    """
    ExchangeUnion(BarHandler, PriceHandler, OrderHandler, CancelHandler, ClearHandler, ENDHandler)：
    回测框架中，交易所（Exchange）体系中使用的以交易所为单位的交易模块
    可处理事件：Bar、Price、Order、Cancel、Clear、END
    如果有继承PseudoExchangeUnit类的自定义单位交易模块，初始化时需要提交单位交易模块的初始化方法
    """

    _name = "ExchangeUnion"

    def __init__(self, factory_=PseudoExchangeUnit):
        """
        @factory_(单位交易模块初始化方法)：继承PseudoExchangeUnit类的自定义单位交易模块，默认为PseudoExchangeUnit
        """

        EVENT_QUEUE.register("Bar", self.on_bar)
        EVENT_QUEUE.register("Price", self.on_price)
        EVENT_QUEUE.register("Order", self.on_order)
        EVENT_QUEUE.register("Cancel", self.on_cancel)
        EVENT_QUEUE.register("Clear", self.on_clear)
        EVENT_QUEUE.register("END", self.on_end)

        self.units = dict()
        self.handlers = dict()
        self.last_datetime = CONST["START_TIME"]

        self.unit_factory = factory_

    def register(self, unit: PseudoExchangeUnit):
        """
        register：当前的交易所模块中，注册给定的单位交易模块
        @unit(PseudoExchangeUnit)：给定的单位交易模块
        @return(None)
        """

        if unit.symbol not in self.units:
            self.units[unit.symbol] = unit
            self.handlers[(unit.symbol, "Bar")] = unit.on_bar
            self.handlers[(unit.symbol, "Price")] = unit.on_price
            self.handlers[(unit.symbol, "Order")] = unit.on_order
            self.handlers[(unit.symbol, "Cancel")] = unit.on_cancel
            self.handlers[(unit.symbol, "Clear")] = unit.on_clear
            self.handlers[(unit.symbol, "END")] = unit.on_end

    def on_bar(self, event: Event) -> None:
        """
        on_bar：接收并处理Bar事件
        @event(Event)：接收的Bar事件
        @return(None)
        """

        bar: Info.BarInfo = event.info

        # 如果标的代码（symbol）未注册，则通过事件中的BarInfo生成单位交易模块并注册
        if bar.symbol not in self.units:
            self.register(self.unit_factory(bar=bar))

        # 如果交易日发生变更，则向事件队列放入前一交易日的Clear事件
        if self.last_datetime.day != bar.datetime.day:
            self.last_datetime += DateOffset(minutes=59)
            EVENT_QUEUE.put(Event(type_="Clear", datetime_=self.last_datetime))
        self.last_datetime = bar.datetime

        # 将Bar事件交给标的代码（symbol）对应的单位交易模块处理
        self.handlers[(bar.symbol, "Bar")](event)

    def on_price(self, event: Event) -> None:
        """
        on_price：接收并处理Price事件
        @event(Event)：接收的Price事件
        @return(None)
        """

        price: Info.PriceInfo = event.info

        self.last_datetime = price.datetime

        # 如果标的代码（symbol）未注册，则通过事件中的PriceInfo生成单位交易模块并注册
        if price.symbol not in self.units:
            self.register(self.unit_factory(price=price))

        # 将Price事件交给标的代码（symbol）对应的单位交易模块处理
        self.handlers[(price.symbol, "Price")](event)

    def on_order(self, event: Event) -> None:
        """
        on_order：接收并处理Order事件
        @event(Event)：接收的Order事件
        @return(None)
        """

        order: Info.OrderInfo = event.info

        self.last_datetime = order.datetime

        # 如果标的代码（symbol）未注册，则通过事件中的OrderInfo生成单位交易模块并注册，同时处理OrderInfo中包含的交易委托
        if order.symbol not in self.units:
            self.register(self.unit_factory(order=order))

        # 否则，将Order事件交给标的代码（symbol）对应的单位交易模块处理
        else:
            self.handlers[(order.symbol, "Order")](event)

    def on_cancel(self, event: Event) -> None:
        """
        on_cancel：接收并处理Cancel事件
        @event(Event)：接收的Cancel事件
        @return(None)
        """

        cancel: Info.CancelInfo = event.info

        self.last_datetime = cancel.datetime

        # 如果标的代码（symbol）已注册，将Cancel事件交给标的代码（symbol）对应的单位交易模块处理
        if cancel.symbol in self.units:
            self.handlers[(cancel.symbol, "Cancel")](event)

    def on_clear(self, event: Event) -> None:
        """
        on_clear：接收并处理Clear事件
        @event(Event)：接收的Clear事件
        @return(None)
        """

        # 将Clear事件交给已注册的所有单位交易模块处理
        for symbol in self.units.keys():
            self.handlers[(symbol, "Clear")](event)

    def on_end(self, event: Event) -> None:
        """
        on_end：接收并处理END事件
        @event(Event)：接收的END事件
        @return(None)
        """

        # for symbol in self.units.keys():
        #     self.handlers[(symbol, "END")](event)

        # if self.last_datetime is not None:
        #     self.last_datetime += DateOffset(minutes=60)
        #     EVENT_QUEUE.put(Event(type_="Clear", datetime_=self.last_datetime))

        # 向事件队列放入当前易日的Clear事件
        self.last_datetime += DateOffset(minutes=60)
        EVENT_QUEUE.put(Event(type_="Clear", datetime_=self.last_datetime))

    def cancel_all(self):
        """
        cancel_all：撤回所有单位交易模块当前交易委托队列中的所有委托
        @return(None)
        """

        for unit in self.units.values():
            unit.cancel_all()
