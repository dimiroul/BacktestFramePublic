from DataHandler.DataHandler import DataHandler
import pandas
from Event.EventQueue import EVENT_QUEUE
from Event.Event import Event
import Information.Info as Info


# DEFAULT_COLUMN为默认的读取数据文件的列
DEFAULT_COLUMN = ["Symbol", "Date", "Time",
                  "Open", "High", "Low", "Close", "Volume", "Turnover"]


def series_to_bar(row: pandas.Series) -> Event:
    """
    series_to_bar：根据给定的一行数据（pandas.Series），生成一个Bar事件
    @row(pandas.Series)：给定的一行数据（pandas.Series）
    @return(Event)：生成的Bar事件
    """
    return Event(type_="Bar", datetime_=row["UpdateDateTime"],
                 info_=Info.BarInfo(symbol_=row["Symbol"], datetime_=row["UpdateDateTime"],
                                    open_=float(row["Open"]), high_=float(row["High"]),
                                    low_=float(row["Low"]), close_=float(row["Close"]),
                                    volume_=0, turnover_=0))


class MADataHandler(DataHandler):
    """
    MADataHandler(DataHandler)：移动均线策略的输入数据处理模块
    """

    __slots__ = ["symbol", "event_queue", "dataframe"]

    def __init__(self):
        self.dataframe = pandas.DataFrame()

    def load_file(self, file_: str, encoding: str = "GB2312") -> None:
        """
        load_file：根据给定的.csv文件路径和文件编码方式，读取行情数据
        @file_(str)：给定.csv文件地址
        @encoding_(str)：给定.csv文件编码方式，默认为GB2312
        @return(None)
        """

        self.dataframe = pandas.read_csv(filepath_or_buffer=file_, encoding=encoding)
        self.dataframe.columns = DEFAULT_COLUMN
        self.dataframe["UpdateDateTime"] = pandas.to_datetime(
            self.dataframe["Date"].map(str) + " " + self.dataframe["Time"].map(str),
            format="%Y/%m/%d %H:%M:%S")

        self.dataframe["index"] = self.dataframe["UpdateDateTime"]
        self.dataframe = self.dataframe.set_index("index")
        self.dataframe = self.dataframe.sort_index()

    def publish_bar(self):
        tmp = self.dataframe.iterrows()
        self.dataframe = pandas.DataFrame()
        for _, row in tmp:
            EVENT_QUEUE.put(series_to_bar(row))
        # EVENT_QUEUE.put(Event())

    def bar_iterator(self):
        tmp = self.dataframe.iterrows()
        self.dataframe = pandas.DataFrame()
        return (series_to_bar(row) for _, row in tmp)
