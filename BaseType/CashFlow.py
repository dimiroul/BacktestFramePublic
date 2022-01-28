from BaseType.ExchangeRate import (amount_to_cny, is_valid_currency, from_amount_of_cny)
from typing import Optional


class CashFlow:
    """
    CashFlow：回测框架中用于表示现金流（cashflow）数据的类
    """

    def __init__(self, currency_: str, amount_: float):
        """
        @currency_(str)：现金流的货币代码（已在回测框架设置）
        @amount_(float)：现金流的金额（非负）
        """

        if not is_valid_currency(currency_=currency_):
            raise ValueError("{:s} not valid currency".format(currency_))
        elif amount_ < 0:
            raise ValueError("{:.2f} not valid amount".format(amount_))
        else:
            self.currency = currency_
            self.amount = amount_

    def __repr__(self):
        return "{:3s} {:.2f}".format(self.currency, self.amount)

    def to_cny(self) -> float:
        """
        to_cny：对于当前现金流，计算结汇所得的人民币（CNY）金额
        return(float)：结汇所得的人民币（CNY）金额，保留2位小数
        """

        return self.__float__()

    def __gt__(self, other):
        """
        比较两笔现金流结汇所得的人民币（CNY）金额
        """

        return self.__float__() > other.__float__()

    def __lt__(self, other):
        return self.__float__() < other.__float__()

    def __float__(self):
        return amount_to_cny(currency_=self.currency, amount_=self.amount)


def cashflow_exchange(cash_flow_: CashFlow = None, currency_: str = "CNY") -> Optional[CashFlow]:
    """
    cashflow_exchange：将给定的现金流，换汇成给定货币的现金流
    @cash_flow_(CashFlow)：给定的现金流，默认为None
    @currency_(str)：货币代码，默认为CNY
    @return(Optional[CashFlow])：如果换汇成功，则返回一笔现金流（CashFlow），失败则返回None
    """

    # 如果给定现金流为None，或者给定货币代码未在回测框架内设置，则返回None
    if cash_flow_ is None or not is_valid_currency(currency_=currency_):
        return None

    # 如果给定现金流已经是以给定货币为单位，则直接返回
    elif currency_ == cash_flow_.currency:
        return cash_flow_

    # 否则，返回换汇后的现金流
    else:
        tmp_amount = cash_flow_.to_cny()
        if currency_ == "CNY":
            return CashFlow(currency_=currency_, amount_=tmp_amount)
        else:
            return CashFlow(currency_=currency_,
                            amount_=from_amount_of_cny(currency_=currency_, amount_=tmp_amount))
