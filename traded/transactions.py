from decimal import Decimal

import sqlalchemy as sa

from . import models


def trade_stock(
    ticker: str,
    qnt: Decimal,
    value: Decimal,
    fee: Decimal,
    tax: Decimal,
    session: sa.orm.Session,
):
    """
    Buy or sell stock.

    To buy inform a positive quantity. Negative for sell.
    Value is the total value of the transaction (including fee and taxes).
    Fee and taxes are always positive.
    """

    stock_obj = models.Stock.get_from_ticker(ticker=ticker, session=session)
    if qnt > 0:
        stock_price = value - fee - tax
    else:
        stock_price = value + fee + tax

    entries = [
        models.EntryLine.new(),
    ]
    entry = models.Entry.new()
