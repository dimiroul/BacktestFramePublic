from abc import (ABCMeta, abstractmethod)
import uuid
from BaseType.Const import CONST
from collections import defaultdict
from Information.Info import (Info, NullInfo)

# EVENT_PRIORITY：记录各类事件的优先级别的全局变量，值越大优先级越高，默认值为0
EVENT_PRIORITY = defaultdict(int)

EVENT_PRIORITY["DEFAULT"] = -1
EVENT_PRIORITY["Bar"] = 10
EVENT_PRIORITY["Price"] = 20
EVENT_PRIORITY["Cancel"] = 30
EVENT_PRIORITY["Fill"] = 40
EVENT_PRIORITY["Order"] = 50
EVENT_PRIORITY["Signal"] = 60
EVENT_PRIORITY["Clear"] = 70
EVENT_PRIORITY["END"] = 80

# EVENT_PRIORITY：记录不包含信息的空事件的类型标签
EMPTY_EVENT = {"DEFAULT", "Clear", "END"}


class Event(object):

    __slots__ = ["type", "datetime", "info"]

    def __init__(self, type_: str = "DEFAULT", datetime_=CONST["START_TIME"], info_: Info = NullInfo()):
        """
        @type_(str)：事件分类
        @datetime_(pandas.Timestamp)：信息时间戳
        @info_(Info)：事件包含的信息（信息分类应与事件分类一致）
        """
        self.type = type_
        self.datetime = datetime_

        # 除非事件属于不包含信息的空事件，否则事件分类标签和信息分类标签必须一致
        if self.type in EMPTY_EVENT or self.type == info_.type:
            self.info = info_
        else:
            raise ValueError("Info type not match")

    def __gt__(self, other):
        """
        比较事件的优先级：分类优先、时间优先
        """

        self_priority = EVENT_PRIORITY[self.type]
        other_priority = EVENT_PRIORITY[other.type]

        return self_priority > other_priority or (
                self_priority == other_priority and self.datetime < other.datetime
        )

    def __repr__(self):
        """
        datetime, type, info
        """

        return (
            "{:s},{:s},{:s}"
        ).format(str(self.datetime), self.type, str(self.info))
