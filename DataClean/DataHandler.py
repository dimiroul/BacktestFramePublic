from abc import (ABCMeta, abstractmethod)
from Event.EventQueue import EventQueue
import pandas
from DataClean.RawData import get_min_dataframe
import os
from BaseType.Const import CONST


class DataHandler:
    """
    回测框架中使用的处理输入数据的基类，此类为抽象类
    """

    __metaclass__ = ABCMeta

    # 自2022/01/11起失效
    # @abstractmethod
    # def get_latest_bars(self, n: int = 1):
    #     raise NotImplementedError("get_latest_bars not implemented")

    @abstractmethod
    def publish_bar(self):
        """
        强制要求子类实现publish_bar()方法
        publish_bar：将处理输入数据得到的Bar事件放入回测框架的事件队列（EVENT_QUEUE）
        """

        raise NotImplementedError("publish_bar not implemented")

    @abstractmethod
    def bar_iterator(self):
        """
        强制要求子类实现bar_iterator()方法
        bar_iterator：将处理输入数据得到的Bar事件装入迭代器（Iterator）并返回
        return(Iterator)：包含处理输入数据得到的Bar事件的迭代器
        """

        raise NotImplementedError("publish_bar_iterator not implemented")

    def __iter__(self):
        """
        使得DataHandler类满足Iterable的要求，默认返回bar_iterator()方法的结果
        """

        return self.bar_iterator()


# 自2022/01/11起失效
# class FileMDEngine(MDEngine):
#
#     __slots__ = ["symbol", "event_queue", "dataframe"]
#
#     def __init__(self, symbol_, event_queue_: EventQueue):
#         self.symbol = symbol_
#         self.event_queue = event_queue_
#         self.dataframe = pandas.DataFrame()
#
#     def load_file(self, file_: str, encoding: str = CONST["ENCODING"], sample: str = CONST["RESAMPLE"]):
#         self.dataframe = self.dataframe.append(get_min_dataframe(file_, asset=self.symbol,
#                                                                  encoding=encoding, sample=sample))
#
#     def load_path(self, path_: str, encoding: str = CONST["ENCODING"], sample: str = CONST["RESAMPLE"]):
#         for file in os.listdir(path_):
#             self.load_file(path_+file, encoding=encoding, sample=sample)
#
#     def get_latest_bars(self, n: int = 1):
#         pass
#
#     def publish_bar(self):
#         tmp = self.dataframe.iterrows()
#         self.dataframe = pandas.DataFrame()
#         for _, row in tmp:
#             self.event_queue.put(self.series_to_bar(row))
#
#     def series_to_bar(self, row: pandas.Series) -> BarEvent:
#         return BarEvent(symbol_=self.symbol, datetime_=row["UpdateDateTime"],
#                         open_=row["open"], high_=row["high"], low_=row["low"], close_=row["close"],
#                         volume_=row["Volume"], turnover_=row["Turnover"])
#
#     def publish_bar_iterator(self):
#         return None
