import csv
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "all_coins.csv"


def get_url_by_symbol(sym: str) -> str | None:
    """Give you the url path of given coin symbol.

    Args:
        sym (str): coin symbol

    Returns:
        str: url path for given symbol
    """

    if not isinstance(sym, str):
        raise TypeError("sym must be a string")

    sym = sym.strip().upper()

    with DATA_FILE.open(newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)

        for row in reader:
            if row[1] == sym:
                return row[2]

    return None


def get_all_coins_symbol() -> list[str]:
    """Give you all coins symbol that exist in DATA_FILE

    Returns:
        list[str]: all coin symbol
    """

    with DATA_FILE.open(newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)

        return [row[1] for row in reader]


if __name__ == "__main__":
    print(get_url_by_symbol(""))
