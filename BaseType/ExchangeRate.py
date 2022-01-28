
# FROM_CNY：记录各个货币的购汇汇率的全局变量
# TO_CNY：记录各个货币的结汇汇率的全局变量
FROM_CNY = dict()
TO_CNY = dict()

# 默认人民币（CNY）汇率为1
FROM_CNY["CNY"] = 1
TO_CNY["CNY"] = 1

# 设置默认港币（HKD）汇率
FROM_CNY["HKD"] = 0.82510
TO_CNY["HKD"] = 0.82490


def set_exchange_rate(currency_: str, from_cny_: float = None, to_cny_: float = None) -> None:
    """
    set_exchange_rate：设置给定货币的购汇和/或结汇汇率
    @currency_(str)：货币代码
    @from_cny_(float)：购汇汇率，默认为None
    @to_cny_(float)：结汇汇率，默认为None
    return(None)
    """

    if from_cny_ is not None:
        FROM_CNY[currency_] = from_cny_

    if to_cny_ is not None:
        TO_CNY[currency_] = to_cny_


def is_valid_currency(currency_: str) -> bool:
    """
    is_valid_currency：判断给定货币是否有效
    @currency_(str)：货币代码
    return(bool)：FROM_CNY、TO_CNY均有currency_记录
    """

    return currency_ in FROM_CNY and currency_ in TO_CNY


def amount_from_cny(currency_: str, amount_: float) -> float:
    """
    amount_from_cny：对于给定金额的给定货币，计算购汇所需的人民币（CNY）金额
    @currency_(str)：货币代码
    @amount_(float)：给定金额
    return(float)：购汇所需的人民币（CNY）金额，保留2位小数
    """

    if currency_ not in FROM_CNY:
        raise RuntimeError("FROM_CNY {:s} not defined".format(currency_))
    else:
        return round(amount_ * FROM_CNY[currency_], ndigits=2)


def from_amount_of_cny(currency_: str, amount_: float) -> float:
    """
    from_amount_of_cny：对于给定金额的人民币（CNY），计算购汇所得的给定货币金额
    @currency_(str)：货币代码
    @amount_(float)：给定金额
    return(float)：购汇所得的给定货币金额，保留2位小数
    """

    if currency_ not in FROM_CNY:
        raise RuntimeError("FROM_CNY {:s} not defined".format(currency_))
    else:
        return round(amount_ / FROM_CNY[currency_], ndigits=2)


def amount_to_cny(currency_: str, amount_: float) -> float:
    """
    amount_to_cny：对于给定金额的给定货币，计算结汇所得的人民币（CNY）金额
    @currency_(str)：货币代码
    @amount_(float)：给定金额
    return(float)：结汇所得的人民币（CNY）金额，保留2位小数
    """

    if currency_ not in TO_CNY:
        raise RuntimeError("TO_CNY {:s} not defined".format(currency_))
    else:
        return round(amount_ * TO_CNY[currency_], ndigits=2)


def to_amount_of_cny(currency_: str, amount_: float) -> float:
    """
    to_amount_of_cny：对于给定金额的人民币（CNY），计算结汇所需的给定货币金额
    @currency_(str)：货币代码
    @amount_(float)：给定金额
    return(float)：结汇所需的给定货币金额，保留2位小数
    """
    
    if currency_ not in TO_CNY:
        raise RuntimeError("TO_CNY {:s} not defined".format(currency_))
    else:
        return round(amount_ / TO_CNY[currency_], ndigits=2)

