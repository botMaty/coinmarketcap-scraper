import csv

def get_url_by_sym(sym: str) -> str:
    with open("all_coins.csv", newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)
        for row in reader:
            if row[1] == sym:
                return row[2]
    return None

if __name__ == "__main__":
    print(get_url_by_sym("BTC"))