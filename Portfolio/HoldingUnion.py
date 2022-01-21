from BaseType.Subject import Subject
# import Event.Event as Event
from Event.Event import Event
from Event.EventHandler import (PriceHandler, SignalHandler, FillHandler, ClearHandler, ENDHandler)
from Event.EventQueue import EVENT_QUEUE
# from Event.EventLogger import EVENT_LOGGER
from pandas.tseries.offsets import DateOffset
from Logger.Logger import LoggerStringUnit
from BaseType.Const import CONST
from collections import defaultdict
# from Portfolio.BidSignalQueue import (BidSignal, BidSignalQueue, SIGNAL_MAP_ORDER)
from Portfolio.BidSignalQueue import BidSignalQueue
from Infomation.Info import SIGNAL_MAP_ORDER
import uuid
from BaseType.CashFlow import (CashFlow, cashflow_exchange)
from Portfolio.Wallet import Wallet
import Infomation.Info as Info
from typing import Optional
from BaseType.ExchangeRate import amount_from_cny


class PortfolioInfo(Info.Info):
    """
    Portfolio信息，用于投资组合（Portfolio）体系中的投资组合/基金/集合理财产品的相关信息
    """

    type = "Portfolio"
    __slots__ = ["cash", "amount", "asset", "debt", "net_asset", "share", "net_price"]

    def __init__(self, cash_: float, amount_: float, asset_: float, debt_: float,
                 net_asset_: float, share_: float, net_price_: float):
        self.cash = cash_
        self.amount = amount_
        self.asset = asset_
        self.debt = debt_
        self.net_asset = net_asset_
        self.share = share_
        self.net_price = net_price_

    def __repr__(self):
        """
        cash, amount, asset, debt, net_asset, share, net_price
        """

        return (
            "{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:4f}"
        ).format(self.cash, self.amount, self.asset, self.debt, self.net_asset, self.share, self.net_price)

# 自2022/01/11起失效
# class PortfolioLoggerUnit(LoggerUnit):
#
#     columns = ["committer", "datetime", "cash", "amount", "asset", "debt", "net_asset", "share", "net_price"]
#
#     def log(self, obj, committer: str):
#         self.data = self.data.append({
#             "committer": committer,
#             "datetime": obj.last_datetime,
#             "cash": obj.cash,
#             "amount": obj.amount,
#             "asset": obj.asset,
#             "debt": obj.debt,
#             "net_asset": obj.net_asset,
#             "share": obj.share,
#             "net_price": obj.net_price
#             }, ignore_index=True)


# 定义PORTFOLIO_LOGGER为回测框架使用的投资组合记录模块，作为全局变量
PORTFOLIO_LOGGER: LoggerStringUnit = LoggerStringUnit(head_="cash,amount,asset,debt,net_asset,share,net_price")


class PseudoHoldingUnit(Subject, PriceHandler, FillHandler):
    """
    PseudoHoldingUnit(Subject, PriceHandler, FillHandler)：
    回测框架中，投资组合（Portfolio）体系中使用的以标的为单位的交易模块
    可处理事件：Price、Fill
    除了常规的通过参数进行初始化的方式外，提供了通过FillInfo进行初始化的简化方式
    """

    _name = "PseudoHoldingUnit"

    __slots__ = ["crt_price", "open_price", "volume", "net_price", "last_datetime"]

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
            self.open_price = crt_price_

        # 如果提供了Fill信息，则通过Fill信息初始化
        else:
            super().__init__(symbol_=init_fill.symbol, exchange_=exchange_, last_datetime_=init_fill.datetime,
                             per_hand_=per_hand_, per_price_=per_price_, bid_commission_=bid_commission_,
                             bid_commission_rate_=bid_commission_rate_, ask_commission_=ask_commission_,
                             ask_commission_rate_=ask_commission_rate_, bid_tax_=bid_tax_, bid_tax_rate_=bid_tax_rate_,
                             ask_tax_=ask_tax_, ask_tax_rate_=ask_tax_rate_, crt_price_=init_fill.filled_price,
                             net_price_=net_price_, book_value_=book_value_, volume_=init_fill.volume,
                             multiplier_=multiplier_, margin_rate_=margin_rate_, currency_=currency_)
            self.open_price = init_fill.filled_price

    def on_price(self, event: Event) -> None:
        """
        on_price：接收并处理Price事件
        @event(Event)：接收的Price事件
        @return(None)
        """

        price: Info.PriceInfo = event.info

        self.last_datetime = event.datetime
        self.crt_price = price.crt_price

        self.refresh()

    def on_fill(self, event: Event) -> None:
        """
        on_fill：接收并处理Fill事件
        @event(Event)：接收的Fill事件
        @return(None)
        """

        fill: Info.FillInfo = event.info

        self.last_datetime = fill.datetime
        self.crt_price = fill.filled_price

        tmp_volume = self.volume + (fill.volume * fill.direction)
        if tmp_volume == 0:
            self.open_price = 0
        else:
            self.open_price = (self.open_price * self.volume + fill.filled_price * fill.volume * fill.direction) \
                              / tmp_volume
        self.volume = tmp_volume

        self.refresh()


# 自2022/01/11起失效
# def create_bid_signal(signal: Event.SignalEvent, holding: PseudoHoldingUnit) -> BidSignal:
#     return BidSignal(uid_=signal.uid, symbol_=signal.symbol, price_=signal.price, volume_=signal.volume,
#                      amount_=holding.volume_to_amount(volume_=signal.volume, price_=signal.price, direction_=1),
#                      type_=signal.signal_type, open_or_close_=signal.open_or_close)


class HoldingUnion(PriceHandler, SignalHandler, FillHandler, ClearHandler, ENDHandler):
    """
    HoldingUnion(PriceHandler, SignalHandler, FillHandler, ClearHandler, ENDHandler)：
    回测框架中，投资组合（Portfolio）体系中使用的以投资组合/基金/集合理财产品为单位的交易模块
    可处理事件：Price、Signal、Fill、Clear、END
    如果有继承PseudoHoldingUnit类的自定义单位交易模块，初始化时需要提交单位交易模块的初始化方法
    """

    _name = "HoldingUnion"

    __slots__ = ["last_datetime", "share", "cash_available", "net_price",
                 "amount", "asset", "debt", "net_asset", "net_last"]

    def __init__(self, factory_=PseudoHoldingUnit):
        """
        @factory_(单位交易模块初始化方法)：继承PseudoHoldingUnit类的自定义单位交易模块，默认为PseudoHoldingUnit
        """

        EVENT_QUEUE.register("Price", self.on_price)
        EVENT_QUEUE.register("Signal", self.on_signal)
        EVENT_QUEUE.register("Fill", self.on_fill)
        EVENT_QUEUE.register("Clear", self.on_clear)
        EVENT_QUEUE.register("END", self.on_end)

        self.unit_factory = factory_

        self.share = 0

        self.cash = 0
        self.wallet = Wallet()

        self.amount = 0
        self.asset = 0
        self.debt = 0
        self.net_asset = 0
        self.net_price = 1
        self.net_last = 1
        self.holdings = dict()
        self.handlers = dict()
        self.bid_queue = BidSignalQueue()
        self.active_orders = defaultdict(set)
        self.active_symbols = defaultdict(set)

        self.last_datetime = CONST["START_TIME"]

    def time_offset(self, offset: str = CONST["TIME_OFFSET"], times: int = CONST["TIME_OFFSET_TIMES"]) -> None:
        """
        time_offset：模块内的最新时间戳的时间流逝
        @offset(str)：时间流逝的单位颗粒
        @times(int)：时间流逝的颗粒数量
        @return(None)
        """

        # 调用pandas.tseries.offsets.DateOffset方法
        self.last_datetime = self.last_datetime + DateOffset(**{offset: times})

    def refresh(self) -> None:
        """
        refresh：更新模块的现金余额（cash）、持仓总额（amount）、总资产（asset）、净资产（net_asset）、净值（net_price）
        @return(None)
        """

        # self.cash = self.cash_available + sum(self.cash_frozen.values())
        # print("{:.2f} {:.2f}".format(self.cash, self.wallet.get_total()))

        # 现金余额为现金管理模块中以人民币（CNY）为单位的现金余额
        self.cash = self.wallet.get_total()

        # 持仓总额为包含的所有标的单位模块的以人民币（CNY）为单位的现值总和
        self.amount = 0
        for holding in self.holdings.values():
            self.amount += holding.crt_amount

        # 总资产为现金余额和持仓总额的求和，保留2位小数
        self.asset = round(self.cash + self.amount, 2)

        # 净资产为总资产减去投资组合的当前负债
        self.net_asset = self.asset - self.debt

        # 净值为净资产除以当前份额，保留4位小数
        self.net_last = self.net_price
        self.net_price = round(self.net_asset / self.share, 4)

    def get_info(self) -> PortfolioInfo:
        """
        get_info：提取当前交易模块的信息（PortfolioInfo）
        @return(PortfolioInfo)：提取的交易模块信息
        """

        return PortfolioInfo(cash_=self.cash, amount_=self.amount, asset_=self.asset, debt_=self.debt,
                             net_asset_=self.net_asset, share_=self.share, net_price_=self.net_price)

    def reset_price(self) -> None:
        """
        reset_price：将模块的净值重置为1.0000，当前份额设置为当前净资产的值
        @return(None)
        """

        self.refresh()
        self.share = self.net_asset
        self.net_price = 1

    def set_share(self, share_: float) -> None:
        """
        set_share：根据给定的份额数据，设置当前份额
        @share_(float)：给定的份额数据
        @return(None)
        """

        # 如果给定的份额数据非正数，则不作处理
        if share_ > 0:
            self.share = share_

            self.refresh()
            PORTFOLIO_LOGGER.log(obj=self.get_info(), committer=self._name, datetime_=self.last_datetime)

    def subscribe(self, amount_: float, currency_: str = "CNY") -> None:
        """
        subscribe：使用给定金额的给定货币的现金申购当前投资组合
        @amount_(float)：给定金额
        @currency_(str)：货币代码，默认为CNY
        @return(None)
        """
        # if amount_ >= 0:
        #     self.cash_available += amount_

        flow = CashFlow(currency_=currency_, amount_=amount_)
        self.wallet.input(cash_flow_=flow)

        # 以当前净值计算申购所增加的份额，保留2位小数
        self.share += round(flow.to_cny() / self.net_price, 2)
        # self.share += round(amount_ / self.net_price, 2)

        self.refresh()
        PORTFOLIO_LOGGER.log(obj=self.get_info(), committer=self._name, datetime_=self.last_datetime)

    def redeem_amount(self, amount_: float, currency_: str = "CNY") -> Optional[CashFlow]:
        """
        redeem_amount：从当前投资组合中赎回给定金额的给定货币
        @amount_(float)：给定金额
        @currency_(str)：货币代码，默认为CNY
        @return(Optional[CashFlow])：对赎回需求的处理结果，成功则返回一笔现金流（CashFlow），失败则返回None
        """

        # 如果当前可用资金不足用于赎回需求，则赎回失败
        flow = self.wallet.output(currency_=currency_, amount_=amount_)

        # 如果赎回成功，以当前净值计算赎回所减少的份额，保留2位小数
        if flow is not None:
            self.share -= round(amount_from_cny(currency_=currency_, amount_=amount_) / self.net_price, 2)
        return flow

        # if 0 < amount_ <= self.cash_available:
        #     self.cash_available -= amount_
        #     self.share -= round(amount_ / self.net_price, 2)
        #     # PORTFOLIO_LOGGER.log(obj=self, committer=self._name)

    def redeem_share(self, share_: float, currency_: str = "CNY") -> Optional[CashFlow]:
        """
        redeem_share：从当前投资组合中赎回给定份额，并以给定货币为单位
        @share_(float)：给定赎回份额
        @currency_(str)：货币代码，默认为CNY
        @return(Optional[CashFlow])：对赎回需求的处理结果，成功则返回一笔现金流（CashFlow），失败则返回None
        """

        # 以当前净值计算赎回所需的资金，如果当前可用资金不足用于赎回需求，则赎回失败
        share_ = round(share_, ndigits=2)
        flow = self.wallet.output(currency_="CNY", amount_=share_ * self.net_price)

        if flow is not None:
            self.share -= share_
        return cashflow_exchange(cash_flow_=flow, currency_=currency_)

        # if 0 < share_ * self.net_price <= self.cash_available:
        #     self.cash_available -= (share_ * self.net_price)
        #     self.share = round(self.share - share_, 2)
        #     # PORTFOLIO_LOGGER.log(obj=self, committer=self._name)

    def borrow(self, amount_: float, currency_: str = "CNY") -> None:
        """
        borrow：投资组合借入给定金额的给定货币的现金
        @amount_(float)：给定金额
        @currency_(str)：货币代码，默认为CNY
        @return(None)
        """
        # if amount_ > 0:
        #     self.cash_available += amount_
        #     self.debt += amount_

        flow = CashFlow(currency_=currency_, amount_=amount_)
        self.wallet.input(cash_flow_=flow)
        self.debt += flow.to_cny()

        self.refresh()
        PORTFOLIO_LOGGER.log(obj=self.get_info(), committer=self._name, datetime_=self.last_datetime)

    def repay(self, amount_: float, currency_: str = "CNY") -> Optional[CashFlow]:
        """
        repay：投资组合偿还负债，以给定金额的给定货币支付
        @amount_(float)：给定金额
        @currency_(str)：货币代码，默认为CNY
        @return(Optional[CashFlow])：对偿还需求的处理结果，成功则返回一笔现金流（CashFlow），失败则返回None
        """

        # 如果当前可用资金不足用于偿还需求，则偿还负债失败
        flow = self.wallet.output(currency_=currency_, amount_=amount_)
        if flow is not None:
            self.debt -= amount_from_cny(currency_=currency_, amount_=amount_)
        return flow

        # if 0 < amount_ <= self.cash_available:
        #     self.cash_available -= amount_
        #     self.debt -= amount_

    def register(self, holding: PseudoHoldingUnit) -> None:
        """
        register：当前的投资组合/基金/集合理财产品模块中，注册给定的单位持仓模块
        @holding(PseudoHoldingUnit)：给定的单位持仓模块
        @return(None)
        """

        if holding.symbol not in self.holdings:
            self.holdings[holding.symbol] = holding
            self.handlers[(holding.symbol, "Price")] = holding.on_price
            self.handlers[(holding.symbol, "Fill")] = holding.on_fill

    def get_holding(self, symbol_: str) -> PseudoHoldingUnit:
        """
        get_holding：获取给定标的代码对应的单位持仓模块
        @symbol_(str)：给定的标的代码
        @return(PseudoHoldingUnit)：给定标的代码对应的单位持仓模块
        """

        # 如果标的代码（symbol）未注册，则根据给定的标的代码生成单位持仓模块并注册
        if symbol_ not in self.holdings:
            ret = self.unit_factory(symbol_=symbol_, last_datetime_=self.last_datetime)
            self.register(ret)

        # 否则，获取标的代码（symbol）对应的单位持仓模块
        else:
            ret = self.holdings[symbol_]
        return ret

    def on_price(self, event: Event) -> None:
        """
        on_price：接收并处理Price事件
        @event(Event)：接收的Price事件
        @return(None)
        """

        price: Info.PriceInfo = event.info

        self.last_datetime = price.datetime

        # 将Price事件交给标的代码（symbol）对应的单位持仓模块处理
        if price.symbol in self.holdings:
            self.handlers[(price.symbol, "Price")](event)

    def cancel(self, uid_: uuid.UUID, symbol_: str) -> None:
        """
        cancel：根据给定的委托ID、标的代码，撤回对应的交易委托
        @uid_(uuid.UUID)：委托ID
        @symbol_(str)：标的代码
        @return(None)
        """

        # if (uid_, symbol_) in self.cash_frozen.keys():
        #     self.cash_available += self.cash_frozen.pop((uid_, symbol_))

        # 根据给定的委托ID、标的代码，释放对应的冻结资金
        self.wallet.release(uid_=uid_, symbol_=symbol_)

        # 如果存在委托ID（uid）的进行中的委托，且进行中的委托中包含标的代码（symbol），则撤回对应的交易委托
        if uid_ in self.active_orders and symbol_ in self.active_orders[uid_]:
            self.time_offset()
            # EVENT_QUEUE.put(Event.CancelEvent(uid_=uid_, symbol_=symbol_,
            #                                   datetime_=self.last_datetime, direction_=1))
            # EVENT_QUEUE.put(Event.CancelEvent(uid_=uid_, symbol_=symbol_,
            #                                   datetime_=self.last_datetime, direction_=-1))
            EVENT_QUEUE.put(Event(type_="Cancel", datetime_=self.last_datetime,
                                  info_=Info.CancelInfo(uid_=uid_, symbol_=symbol_,
                                                        datetime_=self.last_datetime, direction_=1)))
            EVENT_QUEUE.put(Event(type_="Cancel", datetime_=self.last_datetime,
                                  info_=Info.CancelInfo(uid_=uid_, symbol_=symbol_,
                                                        datetime_=self.last_datetime, direction_=-1)))
            self.active_orders[uid_].remove(symbol_)

    def cancel_symbol(self, symbol_: str) -> None:
        """
        cancel_symbol：根据给定的标的代码，撤回对应的交易委托
        @symbol_(str)：标的代码
        @return(None)
        """

        for uid_ in self.active_symbols[symbol_]:
            self.cancel(uid_=uid_, symbol_=symbol_)

        self.active_symbols[symbol_].clear()

    # def process_partial_fill(self, fill: Event.FillEvent, amount_: float):
    #     if fill.direction == 1 and (fill.uid, fill.symbol) in self.cash_frozen:
    #         self.cash_frozen[(fill.uid, fill.symbol)] -= amount_
    #     else:
    #         self.cash_available -= (amount_ * fill.direction)
    #
    # def process_full_fill(self, fill: Event.FillEvent, amount_: float):
    #     self.cash_available -= (amount_ * fill.direction)
    #
    #     self.cancel(uid_=fill.uid, symbol_=fill.symbol)

    def cancel_all(self) -> None:
        """
        cancel_all：撤回当前投资组合的所有交易委托
        @return(None)
        """
        # self.cash_available += sum(self.cash_frozen.values())
        # self.cash_frozen = defaultdict(float)

        # 释放所有冻结资金
        self.wallet.release_all()

        for uid_, symbols in self.active_orders.items():
            for symbol_ in symbols:
                # EVENT_QUEUE.put(Event.CancelEvent(uid_=uid_, symbol_=symbol_,
                #                                   datetime_=self.last_datetime, direction_=1))
                # EVENT_QUEUE.put(Event.CancelEvent(uid_=uid_, symbol_=symbol_,
                #                                   datetime_=self.last_datetime, direction_=-1))
                EVENT_QUEUE.put(Event(type_="Cancel", datetime_=self.last_datetime,
                                      info_=Info.CancelInfo(uid_=uid_, symbol_=symbol_,
                                                            datetime_=self.last_datetime, direction_=1)))
                EVENT_QUEUE.put(Event(type_="Cancel", datetime_=self.last_datetime,
                                      info_=Info.CancelInfo(uid_=uid_, symbol_=symbol_,
                                                            datetime_=self.last_datetime, direction_=-1)))
        self.active_orders = defaultdict(set)

    def on_fill(self, event: Event) -> None:
        """
        on_fill：接收并处理Fill事件
        @event(Event)：接收的Fill事件
        @return(None)
        """

        fill: Info.FillInfo = event.info

        # EVENT_LOGGER.log(event=event, log_type=event.type, committer=self._name)

        self.last_datetime = fill.datetime

        # 如果标的代码（symbol）未注册，且Fill事件为买入开仓委托成交，则通过事件中的FillInfo生成单位持仓模块并注册
        if fill.symbol not in self.holdings and (
                fill.direction == 1 and fill.open_or_close == 1
        ):
            self.register(self.unit_factory(init_fill=fill))

        # 否则，将Fill事件交给标的代码（symbol）对应的单位持仓模块处理
        elif fill.symbol in self.holdings:
            self.handlers[(fill.symbol, "Fill")](event)

        # 获取标的代码（symbol）对应的单位持仓模块
        holding = self.get_holding(symbol_=fill.symbol)

        # amount_ = holding.volume_to_amount(volume_=fill.volume, price_=fill.filled_price, direction_=fill.direction)
        # flow = CashFlow(currency_="CNY", amount_=amount_)

        # 根据给定单位持仓模块和事件中的FillInfo，计算成交所涉及的现金变动
        flow = holding.volume_to_cash_flow(volume_=fill.volume, price_=fill.filled_price, direction_=fill.direction)

        # if fill.partial:
        #     self.process_partial_fill(fill=fill, amount_=amount_)
        # else:
        #     self.process_full_fill(fill=fill, amount_=amount_)

        # 根据委托成交是部分成交/完全成交，分别处理现金变动
        if fill.partial:
            self.wallet.process_partial_fill(fill=fill, cash_flow_=flow)

        # 如果委托成交是完全成交，则撤回同一委托ID（uid）且同一标的代码（symbol）对应的交易委托
        else:
            self.wallet.process_full_fill(fill=fill, cash_flow_=flow)
            self.cancel(uid_=fill.uid, symbol_=fill.symbol)

        # self.refresh()
        # PORTFOLIO_LOGGER.log(obj=self, committer=self._name)

    # 自2022/01/11起失效
    # def put_bid_order(self, symbol_: str, open_or_close_: int, uid_: uuid.UUID, type_: str,
    #                   price_: float, volume_: float, amount_: float):
    #     self.time_offset()
    #     EVENT_QUEUE.put(Event.OrderEvent(symbol_=symbol_, datetime_=self.last_datetime,
    #                                      direction_=1, open_or_close_=open_or_close_,
    #                                      price_=price_, volume_=volume_, uid_=uid_,
    #                                      order_type_=SIGNAL_MAP_ORDER[type_]))
    #     # self.cash_available -= amount_
    #     # self.cash_frozen[(uid_, symbol_)] += amount_
    #     self.wallet.freeze(uid_=uid_, symbol_=symbol_, currency_="CNY", amount_=amount_)
    #     self.active_orders[uid_].add(symbol_)
    #     self.active_symbols[symbol_].add(uid_)

    def put_bid_order(self, order: Info.OrderInfo, amount_: float) -> None:
        """
        put_bid_order：根据给定的买入交易委托信息和预计冻结金额，发出交易委托并冻结相应资金
        @order(Info.OrderInfo)：给定的买入交易委托信息
        @amount_(float)：预计冻结金额
        @return(None)
        """

        # 向交易所（Exchange）发出买入交易委托
        self.time_offset()
        EVENT_QUEUE.put(Event(type_="Order", datetime_=self.last_datetime, info_=order))

        # self.cash_available -= amount_
        # self.cash_frozen[(uid_, symbol_)] += amount_

        # 按照买入委托预计占用的金额冻结资金
        self.wallet.freeze(uid_=order.uid, symbol_=order.symbol, currency_="CNY", amount_=amount_)
        self.active_orders[order.uid].add(order.symbol)
        self.active_symbols[order.symbol].add(order.uid)

    # 自2022/01/11起失效
    # def process_bid_signal(self, signal: Event.SignalEvent, holding: PseudoHoldingUnit):
    #
    #     tmp_volume = holding.amount_to_volume(amount_=self.wallet.cash_available, price_=signal.price, direction_=1)
    #
    #     if tmp_volume >= signal.volume:
    #         tmp_amount = holding.volume_to_amount(volume_=signal.volume, price_=signal.price, direction_=1)
    #         self.put_bid_order(symbol_=signal.symbol, open_or_close_=signal.open_or_close,
    #                            uid_=signal.uid, type_=signal.signal_type,
    #                            price_=signal.price, volume_=signal.volume, amount_=tmp_amount)
    #
    #         rest_volume = 0
    #
    #     elif tmp_volume > 0 and signal.signal_type in {"TBF", "IOC"}:
    #         tmp_amount = holding.volume_to_amount(volume_=tmp_volume, price_=signal.price, direction_=1)
    #         self.put_bid_order(symbol_=signal.symbol, open_or_close_=signal.open_or_close,
    #                            uid_=signal.uid, type_=signal.signal_type,
    #                            price_=signal.price, volume_=tmp_volume, amount_=tmp_amount)
    #
    #         rest_volume = signal.volume - tmp_volume
    #
    #     else:
    #         rest_volume = signal.volume
    #
    #     if rest_volume > 0 and signal.signal_type in {"TBF", "FOW"}:
    #         rest_amount = holding.volume_to_amount(volume_=rest_volume, price_=signal.price, direction_=1)
    #         self.bid_queue.put(BidSignal(uid_=signal.uid, symbol_=signal.symbol, price_=signal.price,
    #                                      volume_=rest_volume, amount_=rest_amount,
    #                                      type_=signal.signal_type, open_or_close_=signal.open_or_close))

    def process_bid_signal(self, signal: Info.SignalInfo, holding: PseudoHoldingUnit) -> None:
        """
        process_bid_signal：根据给定的单位持仓模块，处理给定的买入信号（Signal）信息
        @signal(Info.SignalInfo)：给定的买入信号（Signal）信息
        @holding(PseudoHoldingUnit)：给定的单位持仓模块
        @return(None)
        """

        # 根据给定的单位持仓模块，计算买入信号（Signal）预计占用的资金
        signal.amount = holding.volume_to_amount(volume_=signal.volume, price_=signal.price, direction_=1)

        # 如果投资组合有足够的可用资金用于买入信号（Signal），则发出相应的买入委托
        if self.wallet.cash_available >= signal.amount:
            self.put_bid_order(order=Info.OrderInfo(symbol_=signal.symbol, datetime_=self.last_datetime,
                                                    direction_=signal.direction, open_or_close_=signal.open_or_close,
                                                    price_=signal.price, volume_=signal.volume,
                                                    uid_=signal.uid, order_type_=SIGNAL_MAP_ORDER[signal.signal_type]),
                               amount_=signal.amount)

            rest_volume = 0

        # 否则，如果买入信号（Signal）分类为TBF或IOC，则根据可用资金计算可申报的买入数量，并申报相应的买入委托
        elif signal.signal_type in {"TBF", "IOC"}:
            tmp_volume = holding.amount_to_volume(amount_=self.wallet.cash_available,
                                                  price_=signal.price, direction_=1)

            if tmp_volume > 0:
                self.put_bid_order(order=Info.OrderInfo(symbol_=signal.symbol, datetime_=self.last_datetime,
                                                        direction_=signal.direction,
                                                        open_or_close_=signal.open_or_close,
                                                        price_=signal.price, volume_=tmp_volume, uid_=uuid.UUID(),
                                                        order_type_=SIGNAL_MAP_ORDER[signal.signal_type]),
                                   amount_=holding.volume_to_amount(volume_=tmp_volume,
                                                                    price_=signal.price, direction_=1))

            rest_volume = signal.volume - tmp_volume

        # 未申报的买入数量计入余量
        else:
            rest_volume = signal.volume

        # 如果有余量，且买入信号（Signal）分类为TBF或FOW，则将买入信号（Signal）剩余部分放入买入信号优先队列（BidSignalQueue）
        if rest_volume > 0 and signal.signal_type in {"TBF", "FOW"}:
            if rest_volume < signal.volume:
                signal.volume = rest_volume
                signal.amount = holding.volume_to_amount(volume_=rest_volume, price_=signal.price, direction_=1)

            self.bid_queue.put(signal)

    # 自2022/01/11起失效
    # def process_bid_signal_queue(self):
    #
    #     while not self.bid_queue.is_empty() and self.wallet.cash_available >= self.bid_queue.heap[0].amount:
    #         tmp_signal = self.bid_queue.pop()
    #         self.put_bid_order(symbol_=tmp_signal.symbol, open_or_close_=tmp_signal.open_or_close,
    #                            uid_=tmp_signal.uid, type_=tmp_signal.type, price_=tmp_signal.price,
    #                            volume_=tmp_signal.volume, amount_=tmp_signal.amount)
    #
    #     if self.bid_queue.is_empty():
    #         return
    #
    #     tmp_signal = self.bid_queue.first()
    #     holding = self.get_holding(symbol_=tmp_signal.symbol)
    #
    #     tmp_volume = holding.amount_to_volume(amount_=self.wallet.cash_available, price_=tmp_signal.price, direction_=1)
    #
    #     if tmp_volume > 0 and tmp_signal.type == "TBF":
    #         tmp_amount = holding.volume_to_amount(volume_=tmp_volume, price_=tmp_signal.price, direction_=1)
    #         self.put_bid_order(symbol_=tmp_signal.symbol, open_or_close_=tmp_signal.open_or_close,
    #                            uid_=tmp_signal.uid, type_=tmp_signal.type, price_=tmp_signal.price,
    #                            volume_=tmp_volume, amount_=tmp_amount)
    #
    #         self.bid_queue.heap[0].volume -= tmp_volume
    #         self.bid_queue.heap[0].amount -= tmp_amount

    def process_bid_signal_queue(self) -> None:
        """
        process_bid_signal_queue：处理买入信号优先队列（BidSignalQueue）中的买入信号
        @return(None)
        """

        # 持续申报买入委托，直至买入信号优先队列（BidSignalQueue）为空，或者投资组合可用资金不足以用于当前优先第一的买入信号
        while not self.bid_queue.is_empty() and self.wallet.cash_available >= self.bid_queue.heap[0].amount:
            signal = self.bid_queue.pop()
            self.put_bid_order(order=Info.OrderInfo(symbol_=signal.symbol, datetime_=self.last_datetime,
                                                    direction_=signal.direction, open_or_close_=signal.open_or_close,
                                                    price_=signal.price, volume_=signal.volume,
                                                    uid_=signal.uid, order_type_=SIGNAL_MAP_ORDER[signal.signal_type]),
                               amount_=signal.amount)

        if self.bid_queue.is_empty():
            return

        # 获取当前优先第一的买入信号包含的标的代码（symbol）对应的单位持仓模块，并根据可用资金计算可申报的买入数量
        signal: Info.SignalInfo = self.bid_queue.first()
        holding = self.get_holding(symbol_=signal.symbol)
        tmp_volume = holding.amount_to_volume(amount_=self.wallet.cash_available,
                                              price_=signal.price, direction_=1)

        # 如果有可申报买入数量，且买入信号（Signal）分类为TBF，则申报相应的买入委托
        if tmp_volume > 0 and signal.signal_type == "TBF":
            self.put_bid_order(order=Info.OrderInfo(symbol_=signal.symbol, datetime_=self.last_datetime,
                                                    direction_=signal.direction,
                                                    open_or_close_=signal.open_or_close,
                                                    price_=signal.price, volume_=tmp_volume, uid_=uuid.UUID(),
                                                    order_type_=SIGNAL_MAP_ORDER[signal.signal_type]),
                               amount_=holding.volume_to_amount(volume_=tmp_volume,
                                                                price_=signal.price, direction_=1))

            self.bid_queue.heap[0].volume -= tmp_volume
            self.bid_queue.heap[0].amount = holding.volume_to_amount(volume_=self.bid_queue.heap[0].volume,
                                                                     price_=signal.price, direction_=1)

    def process_ask_signal(self, signal: Info.SignalInfo, holding: PseudoHoldingUnit):
        """
        process_ask_signal：根据给定的单位持仓模块，处理给定的卖出信号（Signal）信息
        @signal(Info.SignalInfo)：给定的卖出信号（Signal）信息
        @holding(PseudoHoldingUnit)：给定的单位持仓模块
        @return(None)
        """

        if holding.volume >= signal.volume:
            tmp_volume = signal.volume

        # 当单位持仓模块中的数量少于卖出信号（Signal）的需求，如果卖出信号（Signal）分类为TBF或IOC，则按照剩余数量申报卖出委托
        elif holding.volume > 0 and signal.signal_type in {"TBF", "IOC"}:
            tmp_volume = holding.volume

        # 否则，忽略卖出信号（Signal）
        else:
            tmp_volume = 0

        if tmp_volume > 0:
            self.time_offset()
            EVENT_QUEUE.put(Event(type_="Order", datetime_=self.last_datetime,
                                  info_=Info.OrderInfo(symbol_=signal.symbol, datetime_=self.last_datetime,
                                                       direction_=signal.direction,
                                                       open_or_close_=signal.open_or_close,
                                                       price_=signal.price, volume_=tmp_volume, uid_=signal.uid,
                                                       order_type_=SIGNAL_MAP_ORDER[signal.signal_type])))
            self.active_orders[signal.uid].add(signal.symbol)
            self.active_symbols[signal.symbol].add(signal.uid)

    def on_signal(self, event: Event) -> None:
        """
        on_signal：接收并处理Signal事件
        @event(Event)：接收的Signal事件
        @return(None)
        """

        signal: Info.SignalInfo = event.info

        # EVENT_LOGGER.log(event=event, log_type=event.type, committer=self._name)

        self.last_datetime = signal.datetime

        # 获取标的代码（symbol）对应的单位持仓模块
        holding = self.get_holding(symbol_=signal.symbol)

        # 根据Signal事件中包含的交易方向，以及标的代码（symbol）对应的单位持仓模块，处理信号（SignalInfo）
        if signal.direction == 1:
            self.process_bid_signal(signal=signal, holding=holding)
        else:
            self.process_ask_signal(signal=signal, holding=holding)

    def on_clear(self, event: Event) -> None:
        """
        on_clear：接收并处理Clear事件
        @event(Event)：接收的Clear事件
        @return(None)
        """

        self.last_datetime = event.datetime

        self.refresh()
        self.process_bid_signal_queue()

        PORTFOLIO_LOGGER.log(obj=self.get_info(), committer=self._name, datetime_=self.last_datetime)

        print("{:s}: {:4f}".format(str(self.last_datetime), self.net_price))

    def on_end(self, event: Event) -> None:
        """
        on_end：接收并处理END事件
        @event(Event)：接收的END事件
        @return(None)
        """

        pass
