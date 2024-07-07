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

def streamlit_callback(step_output):
    # This function will be called after each step of the agent's execution
    st.markdown("---")
    for step in step_output:
        if isinstance(step, tuple) and len(step) == 2:
            action, observation = step
            if isinstance(action, dict) and "tool" in action and "tool_input" in action and "log" in action:
                st.markdown(f"# Action")
                st.markdown(f"**Tool:** {action['tool']}")
                st.markdown(f"**Tool Input** {action['tool_input']}")
                st.markdown(f"**Log:** {action['log']}")
                st.markdown(f"**Action:** {action['Action']}")
                st.markdown(
                    f"**Action Input:** ```json\n{action['tool_input']}\n```")
            elif isinstance(action, str):
                st.markdown(f"**Action:** {action}")
            else:
                st.markdown(f"**Action:** {str(action)}")

            st.markdown(f"**Observation**")
            if isinstance(observation, str):
                observation_lines = observation.split('\n')
                for line in observation_lines:
                    if line.startswith('Title: '):
                        st.markdown(f"**Title:** {line[7:]}")
                    elif line.startswith('Link: '):
                        st.markdown(f"**Link:** {line[6:]}")
                    elif line.startswith('Snippet: '):
                        st.markdown(f"**Snippet:** {line[9:]}")
                    elif line.startswith('-'):
                        st.markdown(line)
                    else:
                        st.markdown(line)
            else:
                st.markdown(str(observation))
        else:
            st.markdown(step)