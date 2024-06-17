import urllib.parse
import streamlit as st
import pandas as pd

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

def display_data(data):
    for key, value in data.items():
        st.write(f"###### {key}")
        if isinstance(value, list):
            if value and isinstance(value[0], dict):
                df = pd.DataFrame(value)
                st.dataframe(df, use_container_width=True)
        elif isinstance(value, dict):
            df_list = []
            for subkey, subvalue in value.items():
                sub_df = pd.DataFrame(subvalue)
                sub_df['Date'] = subkey
                df_list.append(sub_df)
            if df_list:
                df = pd.concat(df_list, ignore_index=True)
                st.dataframe(df)