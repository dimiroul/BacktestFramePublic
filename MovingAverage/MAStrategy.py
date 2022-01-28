from Event.Event import Event
from Event.EventQueue import EVENT_QUEUE
from Strategy.Strategy import PseudoStrategyUnit
from BaseType.Const import CONST
import Information.Info as Info
from Logger.Logger import LoggerStringUnit

# 定义默认使用5日、20日移动平均值
CONST["SHORT"] = 5
CONST["LONG"] = 20


class MAInfo(Info.Info):
    """
    MAInfo信息，用于记录移动均线策略（MovingAverage）的相关信息
    """

    type = "Portfolio"
    __slots__ = ["crt_price", "short_ma", "long_ma", "crt_direction"]

    def __init__(self, crt_price_: float, short_ma_: float, long_ma_: float, crt_direction_: int):
        """
        @crt_price_(float)：当前价格
        @short_ma_(float)：当前短周期均线值
        @long_ma_(float)：当前长周期均线值
        @crt_direction(int)：当前交易方向
        """

        self.crt_price = crt_price_
        self.short_ma = short_ma_
        self.long_ma = long_ma_
        self.crt_direction = crt_direction_

    def __repr__(self):
        """
        crt_price, short_ma, long_ma, crt_direction
        """

        return (
            "{:3f},{:4f},{:4f},{:+d}"
        ).format(self.crt_price, self.short_ma, self.long_ma, self.crt_direction)


# 定义STRATEGY_LOGGER为类LoggerStringUnit的实例，是移动均线策略使用的记录模块，作为全局变量
STRATEGY_LOGGER = LoggerStringUnit(head_="crt_price,short_ma,long_ma,crt_direction")


class MAStrategyUnit(PseudoStrategyUnit):
    """
    MAStrategyUnit(PseudoStrategyUnit)：移动均线策略的单位策略模块
    """

    __slots__ = ["prices", "idx", "long", "short", "long_sum", "short_sum", "is_act",
                 "crt_price", "last_direction", "last_datetime"]
    _name = "MAStrategy"

    def __init__(self, short_: int = CONST["SHORT"], long_: int = CONST["LONG"],
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
        @short_(int)：短周期均线的周期，默认为CONST["SHORT"]
        @long_(int)：长周期均线的周期，默认为CONST["LONG"]

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

        super().__init__(symbol_=symbol_, exchange_=exchange_, last_datetime_=last_datetime_, per_hand_=per_hand_,
                         per_price_=per_price_, bid_commission_=bid_commission_,
                         bid_commission_rate_=bid_commission_rate_, ask_commission_=ask_commission_,
                         ask_commission_rate_=ask_commission_rate_, bid_tax_=bid_tax_, bid_tax_rate_=bid_tax_rate_,
                         ask_tax_=ask_tax_, ask_tax_rate_=ask_tax_rate_, crt_price_=crt_price_,
                         net_price_=net_price_, book_value_=book_value_, volume_=volume_, multiplier_=multiplier_,
                         margin_rate_=margin_rate_, currency_=currency_)

        self.long = long_
        self.short = short_
        self.prices = [0.0 for _ in range(self.long)]
        self.idx: int = 0
        self.long_sum = 0.0
        self.short_sum = 0.0
        self.is_act = False
        self.last_direction: int = 0

    def update_price(self, price_: float) -> None:
        """
        update_price：根据给定的现价，更新策略的数据
        @price_(float)：给定的现价
        @return(None)
        """

        last_long = self.prices[self.idx]
        last_short = self.prices[(self.idx + self.long - self.short) % self.long]
        self.prices[self.idx] = price_
        self.long_sum = self.long_sum - last_long + price_
        self.short_sum = self.short_sum - last_short + price_
        self.idx: int = (self.idx + 1) % self.long

        # 当价格数据达到一个长周期之后，激活策略
        if self.idx == 0:
            self.is_act = True

    def get_info(self) -> MAInfo:
        """
        get_info：提取当前单位策略模块的信息（MAInfo）
        @return(MAInfo)：提取的单位策略模块的信息
        """

        return MAInfo(crt_price_=self.crt_price,
                      short_ma_=round(self.short_sum / self.short, 4),
                      long_ma_=round(self.long_sum / self.long, 4),
                      crt_direction_=self.last_direction)

    def on_bar(self, event: Event) -> None:
        pass

    def on_price(self, event: Event) -> None:
        """
        on_price：接收并处理Price事件
        @event(Event)：接收的Price事件
        @return(None)
        """

        price: Info.PriceInfo = event.info

        self.crt_price = price.crt_price
        self.update_price(price.crt_price)
        self.last_datetime = price.datetime

        # 仅当策略已激活时执行
        if self.is_act:
            short_ma = self.short_sum / self.short
            long_ma = self.long_sum / self.long
            last_dict = 1 if short_ma >= long_ma else -1

            # 首次触发，成交数量减半执行
            if self.last_direction == 0:

                if last_dict == 1:
                    EVENT_QUEUE.put(Event(type_="Signal", datetime_=self.last_datetime,
                                          info_=Info.SignalInfo(symbol_=price.symbol, datetime_=self.last_datetime,
                                                                direction_=1, open_or_close_=1,
                                                                price_=self.crt_price, volume_=self.volume // 2)))

                else:
                    EVENT_QUEUE.put(Event(type_="Signal", datetime_=self.last_datetime,
                                          info_=Info.SignalInfo(symbol_=price.symbol, datetime_=self.last_datetime,
                                                                direction_=-1, open_or_close_=-1,
                                                                price_=self.crt_price, volume_=self.volume // 2)))

            # 仅当短周期均线上穿或下穿长周期均线时发出交易信号
            elif self.last_direction * last_dict < 0:

                if last_dict == 1:
                    EVENT_QUEUE.put(Event(type_="Signal", datetime_=self.last_datetime,
                                          info_=Info.SignalInfo(symbol_=price.symbol, datetime_=self.last_datetime,
                                                                direction_=1, open_or_close_=1,
                                                                price_=self.crt_price, volume_=self.volume)))

                else:
                    EVENT_QUEUE.put(Event(type_="Signal", datetime_=self.last_datetime,
                                          info_=Info.SignalInfo(symbol_=price.symbol, datetime_=self.last_datetime,
                                                                direction_=-1, open_or_close_=-1,
                                                                price_=self.crt_price, volume_=self.volume)))

                print("{:s} raise signal: short: {:.4f}, long: {:.4f} -> {:+d}".format(
                    str(self.last_datetime), short_ma, long_ma, last_dict))

            self.last_direction = last_dict

    def on_fill(self, event: Event) -> None:
        pass

    def on_clear(self, event: Event) -> None:
        STRATEGY_LOGGER.log(obj=self.get_info(), committer=self._name, datetime_=self.last_datetime)

    def on_end(self, event: Event) -> None:
        pass

    def put_signals(self) -> None:
        pass
