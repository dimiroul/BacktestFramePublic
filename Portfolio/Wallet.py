from BaseType.CashFlow import CashFlow
from BaseType.ExchangeRate import (amount_to_cny, amount_from_cny)
from collections import defaultdict
from typing import Optional
# import Event.Event as Event
from Event.Event import Event
import Infomation.Info as Info
import uuid


class Wallet(object):
    """
    Wallet(object)：回测框架中，投资组合（Portfolio）体系中用于进行现金管理的模块
    Wallet类中管理的现金统一以人民币（CNY）的形式存在
    对于其他货币的现金流入，以即时的结汇汇率进行结汇
    对于其他货币的现金流出，以即时的购汇汇率进行购汇
    """

    def __init__(self):
        self.cash_available = 0
        self.cash_frozen = defaultdict(float)

    def get_total(self) -> float:
        """
        get_total：获取当前以人民币（CNY）为单位的现金余额，包括可用资金和处于冻结状态的资金
        """
        return self.cash_available + sum(self.cash_frozen.values())

    def has_available(self, currency_: str, amount_: float) -> bool:
        """
        has_available：对于给定金额的给定货币的现金流出，判断是否有足够的以人民币（CNY）计算的可用资金
        @currency_(str)：货币代码
        @amount_(float)：给定金额
        @return(bool)：是否有足够的以人民币（CNY）计算的可用资金
        """

        return amount_to_cny(currency_=currency_, amount_=amount_) <= self.cash_available

    def input(self, cash_flow_: CashFlow) -> None:
        """
        input：处理给定的现金流入
        @cash_flow_(CashFlow)：给定的现金流入
        @return(None)
        """

        # 将给定的现金流入结汇成人民币（CNY）后，计入可用资金
        self.cash_available += cash_flow_.to_cny()

    def output(self, currency_: str, amount_: float) -> Optional[CashFlow]:
        """
        output：处理给定金额的给定货币的现金流出需求
        @currency_(str)：货币代码
        @amount_(float)：给定金额
        @return(Optional[CashFlow])：对现金流出需求的处理结果，成功则返回一笔现金流（CashFlow），失败则返回None
        """

        tmp_amount = amount_from_cny(currency_=currency_, amount_=amount_)

        # 如果有足够的以人民币（CNY）计算的可用资金，则从可用资金中扣除现金流出需求，并返回一笔现金流（CashFlow）
        if 0 < tmp_amount <= self.cash_available:
            self.cash_available -= tmp_amount
            return CashFlow(currency_=currency_, amount_=amount_)

        # 否则，则返回None
        else:
            return None

    def freeze(self, uid_: uuid.UUID, symbol_: str, currency_: str, amount_: float) -> None:
        """
        freeze：根据给定的委托ID、标的代码、货币代码和委托金额，冻结可用的人民币（CNY）
        @uid_(uuid.UUID)：委托ID
        @symbol_(str)：标的代码
        @currency_(str)：货币代码
        @amount_(float)：给定金额
        @return(None)
        """

        tmp_amount = amount_to_cny(currency_=currency_, amount_=amount_)
        self.cash_available -= tmp_amount
        self.cash_frozen[(uid_, symbol_)] += tmp_amount

    def release(self, uid_: uuid.UUID, symbol_: str) -> None:
        """
        release：根据给定的委托ID、标的代码，释放对应的冻结资金
        @uid_(uuid.UUID)：委托ID
        @symbol_(str)：标的代码
        @return(None)
        """

        # 如果委托ID、标的代码不存在对应的冻结资金，则不作处理
        if (uid_, symbol_) in self.cash_frozen.keys():
            self.cash_available += self.cash_frozen.pop((uid_, symbol_))

    def release_all(self) -> None:
        """
        release_all：释放所有冻结资金
        @return(None)
        """

        self.cash_available += sum(self.cash_frozen.values())
        self.cash_frozen = defaultdict(float)

    def process_partial_fill(self, fill: Info.FillInfo, cash_flow_: CashFlow) -> None:
        """
        process_partial_fill：根据给定的部分成交的委托成交信息、给定的现金流，处理资金变动
        @fill(Info.FillInfo)：给定的部分成交的委托成交信息
        @cash_flow_(CashFlow)：给定的现金流
        @return(None)
        """

        amount_ = cash_flow_.to_cny()

        # 如果部分成交的是买入委托，且存在委托ID、标的代码对应的冻结资金，则直接扣减冻结资金
        if fill.direction == 1 and (fill.uid, fill.symbol) in self.cash_frozen:
            self.cash_frozen[(fill.uid, fill.symbol)] -= amount_

        # 否则，直接增减可用资金
        else:
            self.cash_available -= (amount_ * fill.direction)

    def process_full_fill(self, fill: Info.FillInfo, cash_flow_: CashFlow):
        """
        process_full_fill：根据给定的完全成交的委托成交信息、给定的现金流，处理资金变动
        @fill(Info.FillInfo)：给定的部分成交的委托成交信息
        @cash_flow_(CashFlow)：给定的现金流
        @return(None)
        """

        # 如果成交的是买入委托，且存在委托ID、标的代码对应的冻结资金，则先释放冻结资金
        if fill.direction == 1 and (fill.uid, fill.symbol) in self.cash_frozen:
            self.release(uid_=fill.uid, symbol_=fill.symbol)

        amount_ = cash_flow_.to_cny()
        self.cash_available -= (amount_ * fill.direction)

