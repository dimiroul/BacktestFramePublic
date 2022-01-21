from Logger.Logger import (LoggerStringUnit)

# 定义EVENT_LOGGER为回测框架使用的事件记录模块，作为全局变量
EVENT_LOGGER: LoggerStringUnit = LoggerStringUnit(head_="event_datetime,event_type,info")
