from BaseType.Subject import Subject
# import Event.Event as Event
from Event.Event import Event
from Event.EventHandler import (BarHandler, PriceHandler, FillHandler, ClearHandler, ENDHandler)
from Event.EventQueue import EVENT_QUEUE
from BaseType.Const import CONST
from abc import (abstractmethod)
import Infomation.Info as Info


class PseudoStrategyUnit(Subject, PriceHandler, BarHandler, FillHandler, ClearHandler, ENDHandler):
    """
    PseudoStrategyUnit(Subject, PriceHandler, BarHandler, FillHandler, ClearHandler, ENDHandler)：
    回测框架中，交易策略（Strategy）体系中使用的以单一策略为单位的交易模块
    可处理事件：Bar、Price、Fill、Clear、END
    除了常规的通过参数进行初始化的方式外，提供了通过FillInfo进行初始化的简化方式
    """

    _name = "PseudoStrategyUnit"

    def __init__(self, init_fill: Info.FillInfo = None,
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
                 currency_: str = CONST["CURRENCY"]):
        """
        @init_fill(Info.FillInfo)：用于初始化的Fill信息，默认为None

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
        """

        # 如果未提供Fill信息，则进行常规的参数初始化
        if init_fill is None:
            super().__init__(symbol_=symbol_, exchange_=exchange_, last_datetime_=last_datetime_, per_hand_=per_hand_,
                             per_price_=per_price_, bid_commission_=bid_commission_,
                             bid_commission_rate_=bid_commission_rate_, ask_commission_=ask_commission_,
                             ask_commission_rate_=ask_commission_rate_, bid_tax_=bid_tax_, bid_tax_rate_=bid_tax_rate_,
                             ask_tax_=ask_tax_, ask_tax_rate_=ask_tax_rate_, crt_price_=crt_price_,
                             net_price_=net_price_, book_value_=book_value_, volume_=volume_, multiplier_=multiplier_,
                             margin_rate_=margin_rate_, currency_=currency_)

        # 如果提供了Fill信息，则通过Fill信息初始化
        else:
            super().__init__(symbol_=init_fill.symbol, exchange_=exchange_, last_datetime_=init_fill.datetime,
                             per_hand_=per_hand_, per_price_=per_price_, bid_commission_=bid_commission_,
                             bid_commission_rate_=bid_commission_rate_, ask_commission_=ask_commission_,
                             ask_commission_rate_=ask_commission_rate_, bid_tax_=bid_tax_, bid_tax_rate_=bid_tax_rate_,
                             ask_tax_=ask_tax_, ask_tax_rate_=ask_tax_rate_, crt_price_=init_fill.filled_price,
                             net_price_=net_price_, book_value_=book_value_, volume_=init_fill.volume,
                             multiplier_=multiplier_, margin_rate_=margin_rate_, currency_=currency_)

    @abstractmethod
    def put_signals(self):
        """
        强制继承PseudoStrategyUnit类的子类实现put_signals方法
        回测框架使用的交易策略单位模块，应该至少实现一种生成信号（Signal）的方法
        """

        raise NotImplementedError("on_bar not implemented")


class StrategyUnion(PriceHandler, BarHandler, FillHandler, ClearHandler, ENDHandler):
    """
    StrategyUnion(PriceHandler, BarHandler, FillHandler, ClearHandler, ENDHandler)：
    回测框架中，交易策略（Strategy）体系中使用的以投资顾问/基金经理为单位的交易模块
    可处理事件：Bar、Price、Fill、Clear、END
    如果有继承PseudoStrategyUnit类的自定义单位策略模块，初始化时需要提交单位策略模块的初始化方法
    """

    _name = "StrategyUnion"

    def __init__(self, factory_=PseudoStrategyUnit):
        """
        @factory_(单位策略模块初始化方法)：继承PseudoStrategyUnit类的自定义单位策略模块，默认为PseudoStrategyUnit
        """

        EVENT_QUEUE.register("Price", self.on_price)
        EVENT_QUEUE.register("Bar", self.on_bar)
        EVENT_QUEUE.register("Fill", self.on_fill)
        EVENT_QUEUE.register("Clear", self.on_clear)
        EVENT_QUEUE.register("END", self.on_end)

        self.strategies = dict()
        self.handlers = dict()

        self.strategy_factory = factory_

    def register(self, strategy: PseudoStrategyUnit):
        """
        register：当前的投资顾问/基金经理模块中，注册给定的单位策略模块
        @strategy(PseudoStrategyUnit)：给定的单位策略模块
        @return(None)
        """

        if strategy.symbol not in self.strategies:
            self.strategies[strategy.symbol] = strategy
            self.handlers[(strategy.symbol, "Price")] = strategy.on_price
            self.handlers[(strategy.symbol, "Bar")] = strategy.on_bar
            self.handlers[(strategy.symbol, "Fill")] = strategy.on_fill
            self.handlers[(strategy.symbol, "Clear")] = strategy.on_clear
            self.handlers[(strategy.symbol, "END")] = strategy.on_end

    def on_price(self, event: Event) -> None:
        """
        on_price：接收并处理Price事件
        @event(Event)：接收的Price事件
        @return(None)
        """

        price: Info.PriceInfo = event.info

        # 将Price事件交给标的代码（symbol）对应的单位策略模块处理
        if price.symbol in self.strategies:
            self.handlers[(price.symbol, "Price")](event)

    def on_bar(self, event: Event) -> None:
        """
        on_bar：接收并处理Bar事件
        @event(Event)：接收的Bar事件
        @return(None)
        """

        bar: Info.BarInfo = event.info

        # 将Bar事件交给标的代码（symbol）对应的单位策略模块处理
        if bar.symbol in self.strategies:
            self.handlers[(bar.symbol, "Bar")](event)

    def on_fill(self, event: Event) -> None:
        """
        on_fill：接收并处理Fill事件
        @event(Event)：接收的Fill事件
        @return(None)
        """

        fill: Info.FillInfo = event.info

        # 如果标的代码（symbol）未注册，且Fill事件为买入开仓委托成交，则通过事件中的FillInfo生成单位策略模块并注册
        if fill.symbol not in self.strategies and (
                fill.direction == 1 and fill.open_or_close == 1
        ):
            self.register(self.strategy_factory(init_fill=fill))

        # 将Fill事件交给标的代码（symbol）对应的单位策略模块处理
        if fill.symbol in self.strategies:
            self.handlers[(fill.symbol, "Fill")](event)

    def on_clear(self, event: Event) -> None:
        """
        on_clear：接收并处理Clear事件
        @event(Event)：接收的Clear事件
        @return(None)
        """

        # 将Clear事件交给已注册的所有单位策略模块处理
        for symbol in self.strategies.keys():
            self.handlers[(symbol, "Clear")](event)

    def on_end(self, event: Event) -> None:
        """
        on_end：接收并处理END事件
        @event(Event)：接收的END事件
        @return(None)
        """

        # 将END事件交给已注册的所有单位策略模块处理
        for symbol in self.strategies.keys():
            self.handlers[(symbol, "END")](event)
