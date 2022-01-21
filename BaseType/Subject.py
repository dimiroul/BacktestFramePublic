from abc import (ABCMeta, abstractmethod)
from BaseType.Const import CONST
from pandas.tseries.offsets import DateOffset
from pandas import Timestamp
from BaseType.CashFlow import CashFlow
from BaseType.ExchangeRate import (from_amount_of_cny, amount_to_cny)


class Subject(object):
    """
    Subject(object)：回测框架中使用的各类实体对象的基类
    """

    __metaclass__ = ABCMeta

    def __init__(self, symbol_: str, exchange_: str, last_datetime_: Timestamp,
                 per_hand_: int, per_price_: float,
                 bid_commission_: float, bid_commission_rate_: float,
                 ask_commission_: float, ask_commission_rate_: float,
                 bid_tax_: float, bid_tax_rate_: float,
                 ask_tax_: float, ask_tax_rate_: float,
                 crt_price_: float, net_price_: float, book_value_: float,
                 volume_: float, multiplier_: int,
                 margin_rate_: float, currency_: str):
        """
        @symbol_(str)：标的代码
        @exchange_(str)：交易所
        @last_datetime_(pandas.Timestamp)：最新时间戳
        @per_hand_(int)：每手数量
        @per_price_(int)：报价单位

        @bid_commission_(float)：买入费用定额
        @bid_commission_rate_(float)：买入费用费率
        @ask_commission_(float)：卖出费用定额
        @ask_commission_rate_(float)：卖出费用费率
        @bid_tax_(float)：买入缴税定额
        @bid_tax_rate_(float)：买入缴税税率
        @ask_tax_(float)：卖出缴税定额
        @ask_tax_rate_(float)：卖出缴税税率

        @crt_price_(float)：单位现价
        @net_price_(float)：单位净值
        @book_value_(float)：单位面值
        @volume_(float)：当前数量
        @multiplier_(int)：乘数
        @margin_rate_(float)：保证金比率

        @currency_(str)：货币代码
        """

        self.symbol = symbol_
        self.exchange = exchange_
        self.last_datetime = last_datetime_
        self.per_hand = per_hand_
        self.per_price = per_price_

        self.bid_commission = bid_commission_
        self.bid_commission_rate = bid_commission_rate_
        self.ask_commission = ask_commission_
        self.ask_commission_rate = ask_commission_rate_
        self.bid_tax = bid_tax_
        self.bid_tax_rate = bid_tax_rate_
        self.ask_tax = ask_tax_
        self.ask_tax_rate = ask_tax_rate_

        self.crt_price = crt_price_
        self.net_price = net_price_
        self.book_value = book_value_
        self.volume = volume_
        self.multiplier = multiplier_
        self.margin_rate = margin_rate_

        self.crt_amount = 0.0
        self.net_amount = 0.0
        self.book_amount = 0.0

        self.currency = currency_

        self.refresh()

    def refresh(self) -> None:
        """
        refresh：更新以人民币（CNY）为单位的对象现值（crt_amount）、净值（net_amount）、面值（book_amount）
        @return(None)
        """

        self.crt_amount = amount_to_cny(currency_=self.currency,
                                        amount_=self.crt_price * self.volume * self.multiplier)
        self.net_amount = amount_to_cny(currency_=self.currency,
                                        amount_=self.net_price * self.volume * self.multiplier)
        self.book_amount = amount_to_cny(currency_=self.currency,
                                         amount_=self.book_value * self.volume * self.multiplier)

    def amount_to_volume(self, amount_: float, price_: float, direction_: int) -> float:
        """
        amount_to_volume：对于给定金额的人民币（CNY）、给定交易价格和给定交易方向，计算交易数量
        @amount_(float)：给定给定金额的人民币（CNY）
        @price_(float)：给定交易价格
        @direction_(int)：给定交易方向
        @return(float)：交易数量，按每手数量取整
        """

        ret = from_amount_of_cny(currency_=self.currency, amount_=amount_)

        # 当交易方向为买入时，计算给定金额的人民币（CNY）可买入的最大数量，按每手数量取整
        if direction_ == 1:
            ret -= (self.bid_commission + self.bid_tax)
            ret /= (1 + self.bid_commission_rate + self.bid_tax_rate)
            ret = max(ret, 0)
            ret = int(ret / price_ / self.per_hand) * self.per_hand

        # 当交易方向为卖出时，计算获得给定金额的人民币（CNY）所需卖出的最小数量，按每手数量取整
        else:
            ret += (self.ask_commission + self.ask_tax)
            ret /= (1 - self.ask_commission_rate - self.ask_tax_rate)
            ret = int(ret / price_ / self.per_hand + 1) * self.per_hand

        return ret

    def cash_flow_to_volume(self, cash_flow_: CashFlow, price_: float, direction_: int) -> float:
        """
        cash_flow_to_volume：对于给定的现金流、给定交易价格和给定交易方向，计算交易数量
        @cash_flow_(CashFlow)：给定的现金流
        @price_(float)：给定交易价格
        @direction_(int)：给定交易方向
        @return(float)：交易数量，按每手数量取整
        """

        # 将给定的现金流转换为以对象的货币代码为单位的金额
        if cash_flow_.currency == self.currency:
            ret = cash_flow_.amount
        else:
            ret = from_amount_of_cny(currency_=self.currency, amount_=cash_flow_.to_cny())

        # 当交易方向为买入时，计算给定的现金流可买入的最大数量，按每手数量取整
        if direction_ == 1:
            ret -= (self.bid_commission + self.bid_tax)
            ret /= (1 + self.bid_commission_rate + self.bid_tax_rate)
            ret = max(ret, 0)
            ret = int(ret / price_ / self.per_hand) * self.per_hand

        # 当交易方向为卖出时，计算获得给定的现金流所需卖出的最小数量，按每手数量取整
        else:
            ret += (self.ask_commission + self.ask_tax)
            ret /= (1 - self.ask_commission_rate - self.ask_tax_rate)
            ret = int(ret / price_ / self.per_hand + 1) * self.per_hand

        return ret

    def volume_to_amount(self, volume_: float, price_: float, direction_: int) -> float:
        """
        volume_to_amount：对于给定的交易数量、给定交易价格和给定交易方向，计算以人民币（CNY）为单位的交易金额
        @volume_(float)：给定的交易数量
        @price_(float)：给定交易价格
        @direction_(int)：给定交易方向
        @return(float)：以人民币（CNY）为单位的交易金额
        """

        ret = volume_ * price_

        # 当交易方向为买入时，计算买入给定数量的标的所需的以人民币（CNY）为单位的金额
        if direction_ == 1:
            ret *= (1 + self.bid_commission_rate + self.bid_tax_rate)
            ret += (self.bid_commission + self.bid_tax)

        # 当交易方向为卖出时，计算卖出给定数量的标的获得的以人民币（CNY）为单位的金额，至少为0
        else:
            ret /= (1 - self.ask_commission_rate - self.ask_tax_rate)
            ret -= (self.ask_commission + self.ask_tax)

        return amount_to_cny(currency_=self.currency, amount_=max(ret, 0))

    def volume_to_cash_flow(self, volume_: float, price_: float, direction_: int) -> CashFlow:
        """
        volume_to_amount：对于给定的交易数量、给定交易价格和给定交易方向，计算以对象的货币代码为单位的现金流
        @volume_(float)：给定的交易数量
        @price_(float)：给定交易价格
        @direction_(int)：给定交易方向
        @return(CashFlow)：以对象的货币代码为单位的现金流
        """

        ret = volume_ * price_

        # 当交易方向为买入时，现金流的金额为买入给定数量的标的所需的以对象的货币代码为单位的金额
        if direction_ == 1:
            ret *= (1 + self.bid_commission_rate + self.bid_tax_rate)
            ret += (self.bid_commission + self.bid_tax)

        # 当交易方向为卖出时，现金流的金额为卖出给定数量的标的获得的以对象的货币代码为单位的金额，至少为0
        else:
            ret /= (1 - self.ask_commission_rate - self.ask_tax_rate)
            ret -= (self.ask_commission + self.ask_tax)

        return CashFlow(currency_=self.currency, amount_=max(ret, 0))

    def set(self, args: dict) -> None:
        """
        set：设置对象的属性
        args(dict)：需要修改的属性的(name, value)键值对
        return(None)
        """

        for name, value in args.items():
            super().__setattr__(name=name, value=value)
        self.refresh()

    def time_offset(self, offset: str = CONST["TIME_OFFSET"], times: int = CONST["TIME_OFFSET_TIMES"]) -> None:
        """
        time_offset：对象内的最新时间戳的时间流逝
        @offset(str)：时间流逝的单位颗粒
        @times(int)：时间流逝的颗粒数量
        @return(None)
        """

        # 调用pandas.tseries.offsets.DateOffset方法
        self.last_datetime = self.last_datetime + DateOffset(**{offset: times})
