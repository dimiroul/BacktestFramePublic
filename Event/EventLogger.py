from Logger.Logger import (LoggerUnit, Logger, LoggerStringUnit)
import Event.Event as Event
from BaseType.Const import CONST


# 自2022/01/11起失效
# class DEFAULTLoggerUnit(LoggerUnit):
#
#     columns = ["committer", "datetime"]
#
#     def log(self, event: Event.Event, committer: str):
#         self.data = self.data.append({
#             "datetime": event.datetime,
#             "committer": committer
#         }, ignore_index=True)
#
#
# class BarLoggerUnit(LoggerUnit):
#
#     columns = ["committer", "datetime", "symbol", "open", "high", "low", "close", "volume", "turnover"]
#
#     def log(self, event: Event.BarEvent, committer: str):
#         self.data = self.data.append({
#             "committer": committer,
#             "datetime": event.datetime,
#             "symbol": event.symbol,
#             "open": event.open,
#             "high": event.high,
#             "low": event.low,
#             "close": event.close,
#             "volume": event.volume,
#             "turnover": event.turnover
#         }, ignore_index=True)
#
#
# class PriceLoggerUnit(LoggerUnit):
#
#     columns = ["committer", "datetime", "symbol", "crt_price", "next_price"]
#
#     def log(self, event: Event.PriceEvent, committer: str):
#         self.data = self.data.append({
#             "committer": committer,
#             "datetime": event.datetime,
#             "symbol": event.symbol,
#             "crt_price": event.crt_price,
#             "next_price": event.next_price
#         }, ignore_index=True)
#
#
# class ClearLoggerUnit(LoggerUnit):
#
#     columns = ["committer", "datetime"]
#
#     def log(self, event: Event.ClearEvent, committer: str):
#         self.data = self.data.append({
#             "committer": committer,
#             "datetime": event.datetime
#         }, ignore_index=True)
#
#
# class SignalLoggerUnit(LoggerUnit):
#
#     columns = ["committer", "datetime", "symbol", "direction", "open_or_close", "price", "volume", "signal_type", "uid"]
#
#     def log(self, event: Event.SignalEvent, committer: str):
#         self.data = self.data.append({
#             "committer": committer,
#             "datetime": event.datetime,
#             "symbol": event.symbol,
#             "direction": "买入" if event.direction == 1 else "卖出",
#             "open_or_close": "开仓" if event.open_or_close == 1 else "平仓",
#             "price": event.price,
#             "volume": event.volume,
#             "signal_type": event.signal_type,
#             "uid": event.uid
#         }, ignore_index=True)
#
#
# class OrderLoggerUnit(LoggerUnit):
#
#     columns = ["committer", "datetime", "uid", "symbol", "direction", "open_or_close", "price", "volume", "order_type"]
#
#     def log(self, event: Event.OrderEvent, committer: str):
#         self.data = self.data.append({
#             "committer": committer,
#             "datetime": event.datetime,
#             "uid": event.uid,
#             "symbol": event.symbol,
#             "direction": "买入" if event.direction == 1 else "卖出",
#             "open_or_close": "开仓" if event.open_or_close == 1 else "平仓",
#             "price": event.price,
#             "volume": event.volume,
#             "order_type": event.order_type
#         }, ignore_index=True)
#
#
# class CancelLoggerUnit(LoggerUnit):
#
#     columns = ["committer", "datetime", "uid", "symbol", "direction"]
#
#     def log(self, event: Event.CancelEvent, committer: str):
#         self.data = self.data.append({
#             "committer": committer,
#             "datetime": event.datetime,
#             "uid": event.uid,
#             "symbol": event.symbol,
#             "direction": "买入" if event.direction == 1 else "卖出"
#         }, ignore_index=True)
#
#
# class FillLoggerUnit(LoggerUnit):
#
#     columns = ["committer", "datetime", "uid", "symbol",
#                "direction", "open_or_close", "filled_price", "volume", "partial"]
#
#     def log(self, event: Event.FillEvent, committer: str):
#         self.data = self.data.append({
#             "committer": committer,
#             "datetime": event.datetime,
#             "uid": event.uid,
#             "symbol": event.symbol,
#             "direction": "买入" if event.direction == 1 else "卖出",
#             "open_or_close": "开仓" if event.open_or_close == 1 else "平仓",
#             "filled_price": event.filled_price,
#             "volume": event.volume,
#             "partial": "partial" if event.partial else ""
#         }, ignore_index=True)
#
#
# class QueueLoggerUnit(LoggerUnit):
#
#     columns = ["committer", "datetime", "type"]
#
#     def log(self, event: Event.Event, committer: str):
#         self.data = self.data.append({
#             "committer": committer,
#             "datetime": event.datetime,
#             "type": event.type
#         }, ignore_index=True)
#
#
# class EventLogger(Logger):
#
#     def __init__(self):
#         super().__init__()
#         self.register("Event", QueueLoggerUnit(), CONST["QUEUE_PATH"])
#         # self.register("DEFAULT", DEFAULTLoggerUnit(), CONST["DEFAULT_PATH"])
#         # self.register("Bar", BarLoggerUnit(), CONST["BAR_PATH"])
#         # self.register("Price", PriceLoggerUnit(), CONST["PRICE_PATH"])
#         self.register("Signal", SignalLoggerUnit(), CONST["SIGNAL_PATH"])
#         self.register("Order", OrderLoggerUnit(), CONST["ORDER_PATH"])
#         self.register("Cancel", CancelLoggerUnit(), CONST["CANCEL_PATH"])
#         self.register("Fill", FillLoggerUnit(), CONST["FILL_PATH"])
#
#     def log(self, event: Event.Event, log_type: str, committer: str):
#         # self.logs["Event"][0].log(event, committer)
#         if log_type in self.logs:
#             self.logs[log_type][0].log(event, committer)


# 定义EVENT_LOGGER为回测框架使用的事件记录模块，作为全局变量
EVENT_LOGGER: LoggerStringUnit = LoggerStringUnit(head_="event_datetime,event_type,info")
