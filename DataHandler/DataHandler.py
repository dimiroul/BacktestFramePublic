from abc import (ABCMeta, abstractmethod)


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
        @return(Iterator)：包含处理输入数据得到的Bar事件的迭代器
        """

        raise NotImplementedError("publish_bar_iterator not implemented")

    def __iter__(self):
        """
        使得DataHandler类满足Iterable的要求，默认返回bar_iterator()方法的结果
        """

        return self.bar_iterator()
