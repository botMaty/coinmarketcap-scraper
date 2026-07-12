import csv
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "all_coins.csv"


def get_url_by_sym(sym: str) -> str:
    """Give you the url path of given coin symbol.

    Args:
        sym (str): coin symbl

    Returns:
        str: url path for given symbol
    """

    sym = sym.upper()

    with DATA_FILE.open(newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)

        for row in reader:
            if row[1] == sym:
                return row[2]

    return None


def get_all_coins_sym() -> list[str]:
    """Give you all coins symbol that exist in DATA_FILE

    Returns:
        list[str]: all coin symbol
    """

    syms = []
    with DATA_FILE.open(newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)

        for row in reader:
            syms.append(row[1])

    return syms


if __name__ == "__main__":
    print(get_url_by_sym("BTC"))
