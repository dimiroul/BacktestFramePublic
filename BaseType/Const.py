import pandas
import os


class const(object):
    """
    const(object)：用于保存回测框架使用的各种常量的类
    """

    def __init__(self):
        self.constants = dict()

    def __getitem__(self, item):
        if item not in self.constants:
            raise RuntimeError("const {:s} not defined".format(str(item)))
        else:
            return self.constants[item]

    def __setitem__(self, key, value):
        self.constants[key] = value


# 定义const类的实例CONST，作为全局变量
CONST = const()

# CURRENCY（默认货币）：人民币（CNY）
CONST["CURRENCY"] = "CNY"

# START_TIME（默认起始时间）：1900/01/01 00:00:00
# END_TIME（默认结束时间）：2099/12/31 23:59:59
CONST["START_TIME"] = pandas.to_datetime("1900/01/01 00:00:00", format="%Y%m%d %H:%M:%S")
CONST["END_TIME"] = pandas.to_datetime("2099/12/31 23:59:59", format="%Y%m%d %H:%M:%S")

# DEFAULT_QUEUE_SIZE（默认队列长度）：16
CONST["DEFAULT_QUEUE_SIZE"] = 16

# ENCODING（默认文件编码）：GB2312
# RESAMPLE（默认合并tick时间周期）：1分钟
CONST["ENCODING"] = "GB2312"
CONST["RESAMPLE"] = "1min"

# THIS_PATH（项目本地地址）
# QUEUE_PATH（事件队列记录地址）：/log/QueueLog.csv
# DEFAULT_PATH（默认事件记录地址）：/log/DefaultLog.csv
# BAR_PATH（Bar事件记录地址）：/log/BarLog.csv
# PRICE_PATH（Price事件记录地址）：/log/PriceLog.csv
# SIGNAL_PATH（Signal事件记录地址）：/log/SignalLog.csv
# ORDER_PATH（Order事件记录地址）：/log/OrderLog.csv
# CANCEL_PATH（Cancel事件记录地址）：/log/CancelLog.csv
# FILL_PATH（Fill事件记录地址）：/log/FillLog.csv
# PORTFOLIO_PATH（Portfolio信息记录地址）：/log/PortfolioLog.csv
# STRATEGY_PATH（Strategy信息记录地址）：/log/StrategyLog.csv
CONST["THIS_PATH"] = os.getcwd()
CONST["QUEUE_PATH"] = CONST["THIS_PATH"] + "/log/QueueLog.csv"
CONST["DEFAULT_PATH"] = CONST["THIS_PATH"] + "/log/DefaultLog.csv"
CONST["BAR_PATH"] = CONST["THIS_PATH"] + "/log/BarLog.csv"
CONST["PRICE_PATH"] = CONST["THIS_PATH"] + "/log/PriceLog.csv"
CONST["SIGNAL_PATH"] = CONST["THIS_PATH"] + "/log/SignalLog.csv"
CONST["ORDER_PATH"] = CONST["THIS_PATH"] + "/log/OrderLog.csv"
CONST["CANCEL_PATH"] = CONST["THIS_PATH"] + "/log/CancelLog.csv"
CONST["FILL_PATH"] = CONST["THIS_PATH"] + "/log/FillLog.csv"
CONST["PORTFOLIO_PATH"] = CONST["THIS_PATH"] + "/log/PortfolioLog.csv"
CONST["STRATEGY_PATH"] = CONST["THIS_PATH"] + "/log/StrategyLog.csv"

# SYMBOL（默认标的代码）：NULL
# EXCHANGE（默认交易所）：NULL
# PER_HAND（默认每手数量）：100
# PER_PRICE（默认报价单位）：0.01
CONST["SYMBOL"] = "NULL"
CONST["EXCHANGE"] = "NULL"
CONST["PER_HAND"] = 100
CONST["PER_PRICE"] = 0.01

# BID_COMMISSION（默认买入费用定额）：0.0
# BID_COMMISSION_RATE（默认买入费用费率）：0.00015
# BID_TAX（默认买入缴税定额）：0.0
# BID_TAX_RATE（默认买入缴税税率）：0.0
CONST["BID_COMMISSION"] = 0.0
CONST["BID_COMMISSION_RATE"] = 0.00015
CONST["BID_TAX"] = 0.0
CONST["BID_TAX_RATE"] = 0.0

# ASK_COMMISSION（默认卖出费用定额）：0.0
# ASK_COMMISSION_RATE（默认卖出费用费率）：0.00015
# ASK_TAX（默认卖出缴税定额）：0.0
# ASK_TAX_RATE（默认卖出缴税税率）：0.001
CONST["ASK_COMMISSION"] = 0.0
CONST["ASK_COMMISSION_RATE"] = 0.00015
CONST["ASK_TAX"] = 0.0
CONST["ASK_TAX_RATE"] = 0.001

# CRT_PRICE（默认单位现价）：0.0
# NET_PRICE（默认单位净值）：0.0
# BOOK_PRICE（默认单位面值）：1.0
# VOLUME（默认数量）：0.0
CONST["CRT_PRICE"] = 0.0
CONST["NET_PRICE"] = 0.0
CONST["BOOK_VALUE"] = 1.0
CONST["VOLUME"] = 0.0

# MULTIPLIER（默认乘数）：1
# MARGIN_RATE（默认保证金比例）：1
CONST["MULTIPLIER"] = 1
CONST["MARGIN_RATE"] = 1

# TIME_OFFSET（默认时间流逝单位）：seconds
# TIME_OFFSET_TIMES（默认时间流逝量）：1
CONST["TIME_OFFSET"] = "seconds"
CONST["TIME_OFFSET_TIMES"] = 1
