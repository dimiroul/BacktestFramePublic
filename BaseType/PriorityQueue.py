from BaseType.Const import CONST


def parent(i: int) -> int:
    """
    parent：对于给定二叉堆结点，获得父结点下标
    @i(int)：给定二叉堆结点的下标
    @return(int)：父结点下标
    """

    return (i - 1) // 2


def left(i: int) -> int:
    """
    left：对于给定二叉堆结点，获得左子结点下标
    @i(int)：给定二叉堆结点的下标
    @return(int)：左子结点下标
    """

    return i * 2 + 1


def right(i: int) -> int:
    """
    right：对于给定二叉堆结点，获得右子结点下标
    @i(int)：给定二叉堆结点的下标
    @return(int)：右子结点下标
    """

    return (i + 1) * 2


class PriorityQueue(object):
    """
    PriorityQueue(object)：基于最大堆（max heap）实现的优先队列（priority queue）类
    """

    def __init__(self, factory_):
        """
        @factory_(Callable[None, 队列元素类])：队列元素的默认生成函数
        """

        self.size = CONST["DEFAULT_QUEUE_SIZE"]
        self.factory = factory_
        self.heap = [None for _ in range(self.size)]
        self.max_index = -1

    def resize(self) -> None:
        """
        resize：重新分配最大堆的内存空间，使得最大堆的容量增加一倍
        @return(None)
        """

        self.heap += [None for _ in range(self.size)]
        self.size *= 2

    def is_empty(self) -> bool:
        """
        is_empty：判断优先队列当前是否为空
        @return(bool)：最大堆是否为空
        """

        return self.max_index < 0

    def clear(self) -> None:
        """
        clear：清空当前的优先队列
        @return(None)
        """

        self.max_index = -1

    def __len__(self):
        return self.max_index + 1

    def max_heapfy(self, i: int) -> None:
        if i < 0:
            return
        li = left(i)
        ri = right(i)
        largest = i
        if li <= self.max_index and self.heap[li] > self.heap[largest]:
            largest = li
        if ri <= self.max_index and self.heap[ri] > self.heap[largest]:
            largest = ri
        if largest != i:
            self.heap[i], self.heap[largest] = self.heap[largest], self.heap[i]
            self.max_heapfy(largest)

    def max_passball(self, i: int) -> None:
        if i <= 0:
            return
        while i > 0 and self.heap[i] > self.heap[parent(i)]:
            self.heap[i], self.heap[parent(i)] = self.heap[parent(i)], self.heap[i]
            i = parent(i)

    def first(self):
        """
        first：查询优先队列当前的第一个元素，队列为空时报错
        @return(队列元素类)：优先队列当前的第一个元素
        """

        if self.max_index >= 0:
            return self.heap[0]
        else:
            raise RuntimeError("Empty Queue")

    def put(self, obj) -> None:
        """
        put：将给定元素放入优先队列
        @obj(队列元素类)：放入优先队列的元素
        @return(None)
        """

        # 仅当给定元素与队列注册的类型（factory）相同时，放入优先队列
        if isinstance(obj, self.factory):
            self.max_index += 1
            if self.max_index >= self.size:
                self.resize()
            self.heap[self.max_index] = obj
            self.max_passball(self.max_index)

    def pop(self, i: int = 0):
        """
        pop：对于给定下标，弹出最大堆中对应下标的元素，下标无效时报错
        @i(int)：给定的结点下标
        @return(队列元素类)：最大堆中对应下标的元素
        """

        if 0 <= i <= self.max_index:
            ret = self.heap[i]
            self.heap[i] = self.heap[self.max_index]
            self.max_index -= 1
            self.max_heapfy(i)
            return ret
        else:
            raise IndexError("Invalid Index")

    def get(self):
        """
        get：取出优先队列当前的第一个元素，队列为空时报错，等价于调用pop()
        @return(队列元素类)：优先队列当前的第一个元素
        """

        if self.max_index < 0:
            raise RuntimeError("Empty Queue")
        else:
            return self.pop()

    def __repr__(self):
        if self.max_index < 0:
            return "Empty Queue"
        else:
            return "\n".join(str(self.heap[i]) for i in range(self.max_index + 1))
