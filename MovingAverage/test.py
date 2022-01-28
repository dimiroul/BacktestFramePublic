from Event.EventQueue import EVENT_QUEUE

from Exchange.Exchange import (ExchangeUnion, PseudoExchangeUnit)
from Portfolio.Holding import (PORTFOLIO_LOGGER, HoldingUnion, PseudoHoldingUnit)
from MovingAverage.MAStrategy import (MAStrategyUnit, STRATEGY_LOGGER)
from MovingAverage.MADataHandler import MADataHandler
from Strategy.Strategy import StrategyUnion

from Event.EventLogger import EVENT_LOGGER
from BaseType.Const import CONST
import pandas
import uuid
import Information.Info as Info
from Event.Event import Event

# 定义回测样例的起始时间：2021-01-01 00:00:00
CONST["START_TIME"] = pandas.to_datetime("2021-01-01", format="%Y-%m-%d")

# 定义投资组合的起始资金：1,000,000.00
INIT_CASH = 1000000.00


# 由于回测样例采用日线级别数据，则仅适用收盘价生成Price事件
def bar_slicer(bar: Info.BarInfo):
    """
    @bar(Info.BarInfo)：给定的标的以交易日为单位的报价成交数据
    @return(Generator)：包含“标的在一个时刻的价格数据”信息的Price事件的生成器
    """

    yield Event(type_="Price", datetime_=bar.datetime,
                info_=Info.PriceInfo(symbol_=bar.symbol, datetime_=bar.datetime, crt_price_=bar.close))


def test():

    print("Hello World!")
    print(EVENT_QUEUE, "\n")

    # 初始化数据处理模块
    file_engine = MADataHandler()

    # 读入输入数据，并将生成的Bar事件放入事件优先队列
    file_engine.load_file(CONST["THIS_PATH"] + "/MovingAverage/510300_20210101_20211231.csv")
    file_engine.publish_bar()

    # 初始化交易所、投资组合、投资顾问模块
    executor = ExchangeUnion()
    portfolio = HoldingUnion()
    strategy = StrategyUnion(factory_=MAStrategyUnit)

    # 投资组合注入起始资金
    portfolio.subscribe(amount_=INIT_CASH)

    # 初始化回测样例使用的标的的单位模块
    executor.register(PseudoExchangeUnit(symbol_="510300.SH", crt_price_=5.131,
                                         last_datetime_=executor.last_datetime, bar_slicer_=bar_slicer))
    portfolio.register(PseudoHoldingUnit(symbol_="510300.SH", crt_price_=5.131,
                                         last_datetime_=executor.last_datetime))
    strategy.register(MAStrategyUnit(symbol_="510300.SH", short_=7, long_=23, volume_=100000))

    # 投资组合买入标的的起始持仓
    portfolio.on_fill(Event(type_="Fill", datetime_=executor.last_datetime,
                            info_=Info.FillInfo(uid_=uuid.uuid4(), symbol_="510300.SH",
                                                datetime_=executor.last_datetime,
                                                direction_=1, open_or_close_=1,
                                                filled_price_=5.131, volume_=100000)))

    # 运行事件队列
    EVENT_QUEUE.run()

    # 保存结果
    EVENT_LOGGER.to_file(path_=CONST["QUEUE_PATH"])
    STRATEGY_LOGGER.to_file(path_=CONST["STRATEGY_PATH"])
    PORTFOLIO_LOGGER.to_file(path_=CONST["PORTFOLIO_PATH"])
