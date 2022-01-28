from Event.Event import Event
from BaseType.PriorityQueue import PriorityQueue
from typing import Callable
from collections import defaultdict
from Event.EventHandler import (DEFAULTHandler, ENDHandler)
from BaseType.Const import CONST
from Event.EventLogger import EVENT_LOGGER
import time


# HANDLER_TYPE(Event -> None)：对于事件处理接口所实现的函数类型的定义
HANDLER_TYPE = Callable[[Event], None]

# IGNORE_LIST：忽略记录的事件标签
IGNORE_LIST = {"Price"}


class EventQueue(PriorityQueue, DEFAULTHandler, ENDHandler):
    """
    EventQueue(PriorityQueue)：回测框架使用的事件优先队列
    可处理事件：DEFAULT、END
    """

    __slots__ = ["handlers"]
    _name = "EVENT_QUEUE"

    def __init__(self, default_handler: HANDLER_TYPE = None, end_handler: HANDLER_TYPE = None):
        """
        @default_handler(HANDLER_TYPE)：自定义DEFAULT事件处理方法，默认为None
        @end_handler(HANDLER_TYPE)：自定义END事件处理方法，默认为None
        """

        super().__init__(factory_=Event)
        self.handlers = defaultdict(list)

        # 如果未提供自定义DEFAULT事件处理方法，则使用self.on_default方法
        if default_handler is not None:
            self.register("DEFAULT", default_handler)
        else:
            self.register("DEFAULT", self.on_default)

        # 如果未提供自定义END事件处理方法，则使用self.on_end方法
        if end_handler is not None:
            self.register("END", end_handler)
        else:
            self.register("END", self.on_end)

    def register(self, event_type_: str, handler_: HANDLER_TYPE) -> None:
        """
        register：将给定事件处理方法，加入给定事件分类标签的处理方法列表中
        @event_type_(str)：给定事件分类标签
        @handler_(HANDLER_TYPE)：给定事件处理方法
        @return(None)
        """

        handler_list = self.handlers[event_type_]
        if handler_ not in handler_list:
            handler_list.append(handler_)

    def process_next(self) -> None:
        """
        process_next：处理下一事件，根据事件的分类标签，依次应用于标签对应的处理方法列表中的方法
        @return(None)
        """

        # if not self.is_empty():
        next_event: Event = self.get()

        # 如果下一事件的分类不在忽略记录的列表中，则在事件记录模块中记录事件
        if next_event.type not in IGNORE_LIST:
            EVENT_LOGGER.log(obj=next_event, committer=self._name,
                             datetime_=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

        handler_list = self.handlers[next_event.type]
        # print(next_event.type, len(handler_list))
        for handler in handler_list:
            handler(next_event)

    def process_through(self) -> None:
        """
        process_through：处理事件，直至事件队列为空
        @return(None)
        """

        while not self.is_empty():
            self.process_next()

    def run(self, iter_=None) -> None:
        """
        run：根据给定的事件迭代器（如有），运行事件队列
        @iter_(Iterator)：给定的事件（Event）迭代器，默认为None
        @return(None)
        """

        # 如果提供了事件迭代器，则每次向事件队列中装入一个迭代器提供的事件，并运行至事件队列为空
        if iter_ is not None:
            for event_ in iter_:
                self.put(event_)
                # while not self.is_empty():
                #     self.process_next()
                self.process_through()

        # 如果未提供事件迭代器，或提供的事件迭代器已处理完，则装入一个DEFAULT事件，并运行至事件队列为空
        self.put(Event())
        # while not self.is_empty():
        #     self.process_next()
        self.process_through()

    def run_until(self, datetime_) -> None:
        """
        run_until：运行事件队列，直至给定的时间戳之前
        @datetime_(pandas.Timestamp)：处理截止时间戳
        @return(None)
        """

        # 停止标准为事件队列已空，或队列中下一个事件的时间戳晚于给定的时间戳
        while not self.is_empty() and self.heap[0].datetime <= datetime_:
            self.process_next()

    def on_default(self, event: Event) -> None:
        """
        on_default：处理给定DEFAULT事件的方法
        @event(Event)：给定的DEFAULT事件
        @return(None)
        """

        # 向事件队列装入一个END事件
        self.put(Event(type_="END", datetime_=CONST["END_TIME"]))

    def on_end(self, event: Event) -> None:
        """
        on_end：处理给定END事件的方法
        @event(Event)：给定的END事件
        @return(None)
        """

        pass


# 定义EventQueue类的实例EVENT_QUEUE，作为全局变量
EVENT_QUEUE = EventQueue()
