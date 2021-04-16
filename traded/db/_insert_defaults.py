import sqlalchemy as sa

from . import models


def all(session: sa.orm.Session):
    _insert_default_coa(session)
    _insert_default_assets(session)


def _insert_default_coa(session: sa.orm.Session):  # noqa: C901
    # the testing chart of accounts
    coa = """
    root                        #  1
        Assets                  #  2
            Cash                #  3
            Receivables         #  4
            Inventory           #  5
        Liabilities             #  6
            Payables            #  7
            Shares Issued       #  8
            Retained Earnings   #  9
        Income                  # 10
            Trade               # 11
            Interest            # 12
        Expenses                # 13
            Fees                # 14
                Broker          # 15
                Administration  # 16
            Tax                 # 17
            Other               # 18
    """
    coa = [line for line in coa.splitlines() if line.strip() != ""]
    coa = [line.split("#")[0].rstrip() for line in coa]

    def _get_level(coa, line):
        line_str = coa[line]
        level = len(line_str) - len(line_str.lstrip()) - 4
        level = level // 4
        return level

    def _insert_next(coa, line, parent_id, curr_level, last_id):
        while line < len(coa) - 1:
            line += 1
            now_level = _get_level(coa, line)
            name = coa[line].strip()
            if now_level == curr_level:  # sibling account
                last_id += 1
                acc = models.Account(
                    id=last_id, name=name, parent_id=parent_id
                )
                session.add(acc)
            elif now_level == curr_level + 1:  # child
                line -= 1
                line, last_id = _insert_next(
                    coa=coa,
                    line=line,
                    parent_id=last_id,
                    curr_level=now_level,
                    last_id=last_id,
                )
            elif now_level < curr_level:  # go back one level
                return line - 1, last_id
        return line, last_id

    root = models.Account(id=1, name=coa[0].strip(), parent_id=None)
    session.add(root)
    _insert_next(coa=coa, line=0, parent_id=1, curr_level=1, last_id=1)

    session.commit()


def _insert_default_assets(session: sa.orm.Session):
    assets = [
        # currencies
        ("USD", "US Dolar", True, "currency"),
        ("EUR", "Euros", True, "currency"),
        ("JPY", "Japanese Yen", True, "currency"),
        ("CNY", "Chinese Yuan", True, "currency"),
        ("CHF", "Swiss Franc", True, "currency"),
        ("BRL", "Brazilian Real", True, "currency"),
        ("BTC", "Bitcoin", True, "currency"),
        ("ETH", "Ethereum", True, "currency"),
        ("XMR", "Monero", True, "currency"),
        ("ADA", "Cardano", True, "currency"),
        ("USDT", "Tether", True, "currency"),
    ]

    for asset_item in assets:
        if isinstance(asset_item, tuple):
            asset_item = {
                k: v
                for k, v in zip(
                    ("name", "description", "is_active", "type"), asset_item
                )
            }
        asset_db = models.Asset(**asset_item)
        session.add(asset_db)

    session.commit()
