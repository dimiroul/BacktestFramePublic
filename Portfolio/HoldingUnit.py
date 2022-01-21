from BaseType.Subject import Subject
import Event.Event as Event
from Event.EventHandler import (PriceHandler, SignalHandler, FillHandler, ENDHandler)
from Event.EventQueue import EVENT_QUEUE
from BaseType.Const import CONST


class HoldingUnit(Subject, PriceHandler, SignalHandler, FillHandler, ENDHandler):
    _name = "HoldingUnit"

    def __init__(self, symbol_: str = CONST["SYMBOL"], exchange_: str = CONST["EXCHANGE"],
                 last_datetime_=CONST["START_TIME"],
                 per_hand_: int = CONST["PER_HAND"], per_price_: float = CONST["PER_PRICE"],
                 bid_commission_: float = CONST["BID_COMMISSION"],
                 bid_commission_rate_: float = CONST["BID_COMMISSION_RATE"],
                 ask_commission_: float = CONST["ASK_COMMISSION"],
                 ask_commission_rate_: float = CONST["ASK_COMMISSION_RATE"],
                 bid_tax_: float = CONST["BID_TAX"], bid_tax_rate_: float = CONST["BID_TAX_RATE"],
                 ask_tax_: float = CONST["ASK_TAX"], ask_tax_rate_: float = CONST["ASK_TAX_RATE"],
                 crt_price_: float = CONST["CRT_PRICE"], net_price_: float = CONST["NET_PRICE"],
                 book_value_: float = CONST["BOOK_VALUE"], volume_: float = CONST["VOLUME"],
                 multiplier_: int = CONST["MULTIPLIER"], margin_rate_: float = CONST["MARGIN_RATE"],
                 currency_: str = CONST["CURRENCY"]):
        super().__init__(symbol_=symbol_, exchange_=exchange_, last_datetime_=last_datetime_, per_hand_=per_hand_,
                         per_price_=per_price_, bid_commission_=bid_commission_,
                         bid_commission_rate_=bid_commission_rate_, ask_commission_=ask_commission_,
                         ask_commission_rate_=ask_commission_rate_, bid_tax_=bid_tax_, bid_tax_rate_=bid_tax_rate_,
                         ask_tax_=ask_tax_, ask_tax_rate_=ask_tax_rate_, crt_price_=crt_price_, net_price_=net_price_,
                         book_value_=book_value_, volume_=volume_, multiplier_=multiplier_, margin_rate_=margin_rate_,
                         currency_=currency_)
        EVENT_QUEUE.register("Price", self.on_price)
        EVENT_QUEUE.register("Signal", self.on_signal)
        EVENT_QUEUE.register("Fill", self.on_fill)
        EVENT_QUEUE.register("END", self.on_end)
