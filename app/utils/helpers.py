import urllib.parse


def get_unique_dicts(input_list):
    # Convert list of dicts to a set of tuples to remove duplicates
    unique_tuples = set(tuple(sorted(d.items())) for d in input_list)

    # Convert back to a list of dictionaries
    unique_dicts = [dict(t) for t in unique_tuples]

    return unique_dicts


def purify_symbol(symbol):
    return urllib.parse.quote(symbol)


def purify_prices(price):
    price = price.replace(',', '')
    return float(price)
