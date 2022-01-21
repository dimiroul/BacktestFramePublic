import pandas
from abc import (ABCMeta, abstractmethod)
from collections import defaultdict


class LoggerUnit:
    """
    LoggerUnit：回测框架中，用于记录的单位模块的抽象类，记录结果的存储方式为pandas.DataFrame
    """
    __metaclass__ = ABCMeta

    columns = ["data"]

    def __init__(self):
        self.data = pandas.DataFrame(columns=self.columns)

    @abstractmethod
    def log(self, obj, committer: str) -> None:
        """
        强制要求子类实现log()方法
        log：根据给定记录者提交的记录对象，记录一行数据
        @obj(object)：提交的记录对象
        @committer(str)：给定的记录者
        @return(None)
        """

        raise NotImplementedError("log not implemented")

    def to_csv(self, path_: str, encoding_: str = "GB2312") -> None:
        """
        to_csv：以给定的编码方式，将保存的记录结果输出到给定的.csv文件
        @path_(str)：给定.csv输出文件地址
        @encoding_(str)：给定.csv输出文件编码方式，默认为GB2312
        @return(None)
        """

        self.data.to_csv(path_or_buf=path_, encoding=encoding_)


class LoggerStringUnit:
    """
    LoggerStringUnit：回测框架中，用于记录的单位模块，记录结果的存储方式为字符串
    """

    __slots__ = ["data", "row"]

    def __init__(self, head_: str = "info"):
        """
        @head_(str)：输出结果的首行，默认为“info”
        """

        self.data = "index,committer,datetime,{:s}\n".format(head_)
        self.row = 1

    def log(self, obj: object, committer: str, datetime_) -> None:
        """
        log：根据给定记录者在给定时间提交的记录对象，记录一行数据
        @obj(object)：提交的记录对象
        @committer(str)：给定的记录者
        @datetime_(pandas.Timestamp)：给定的记录时间
        @return(None)
        """
        self.data += (
            "{:d},{:s},{:s},{:s}\n"
        ).format(self.row, committer, str(datetime_), str(obj))
        self.row += 1

    def to_file(self, path_: str, encoding_: str = "GB2312") -> None:
        """
        to_file：以给定的编码方式，将保存的记录结果输出到给定的文件
        @path_(str)：给定输出文件地址
        @encoding_(str)：给定输出文件编码方式，默认为GB2312
        @return(None)
        """

        with open(file=path_, mode="w", encoding=encoding_) as file:
            file.write(self.data)
            file.close()


class Logger:
    """
    Logger：回测框架中，用于记录的模块，管理多个单位记录模块
    """

    def __init__(self):
        self.logs = defaultdict(list)

    def register(self, log_type: str, unit: LoggerUnit, path_: str, encoding_: str = "GB2312") -> None:
        """
        register：根据给定的记录类型及其对应的单位记录模块，注册模块及其.csv输出文件路径和文件编码方式
        @log_type_(str)：给定的记录类型
        @unit(LoggerUnit)：对应的单位记录模块
        @path_(str)：给定.csv输出文件地址
        @encoding_(str)：给定.csv输出文件编码方式，默认为GB2312
        @return(None)
        """

        self.logs[log_type] = [unit, path_, encoding_]

    def log(self, obj, log_type: str, committer: str) -> None:
        """
        log：根据给定记录者提交的记录对象，由给定的记录类型对应的单位记录模块记录一行数据
        @obj(object)：提交的记录对象
        @log_type_(str)：给定的记录类型
        @committer(str)：给定的记录者
        @return(None)
        """

        # 如果记录类型对应的单位记录模块未注册，则不做记录
        if log_type in self.logs:
            self.logs[log_type][0].log(obj, committer)

    def to_csv(self) -> None:
        """
        to_csv：将已注册的所有单位记录模块，以注册的编码方式，将保存的记录结果输出到注册的.csv文件
        @return(None)
        """

        for unit, path_, encoding_ in self.logs.values():
            unit.to_csv(path_=path_, encoding_=encoding_)
