import json
import requests
from markdownify import markdownify as md
from icecream import ic
import urllib.parse
from datetime import datetime

def check_whats_happening(stock):
    print("triggered ai!")


def fetch_and_parse_perplexity_output(query):    
    # Get the current date and time
    now = datetime.now()

    # Format the date and time
    formatted_date = now.strftime("%A, %d/%m/%Y")
    formatted_time = now.strftime("%I:%M %p")

    # Construct the date_context parameter
    date_context = f"Today is {formatted_date} and the time is {formatted_time}. Only look for Indian stocks. Else, reply 'I don't Know'. Respond with only recent results (maximum 5 days old)."


    url = f'https://unfortunate-sally-maharat-8663b4b4.koyeb.app/search_normal?query={urllib.parse.quote(query)}&pro_mode=true&date_context={urllib.parse.quote(date_context)}'
    response = requests.get(url, stream=True)
    
    response_content = response.content.decode('utf-8')
    
    sources = []
    llm_output = ""
    relevant = []
    
    for item in response_content.split('\n'):
        if item:
            output_dict = json.loads(item[5:])
            if output_dict['type'] == 'sources':
                sources.extend(output_dict['data']['organic'])
            elif output_dict['type'] == 'llm':
                llm_output += output_dict['text']
                ic(llm_output)
            elif output_dict['type'] == 'relevant':
                relevant.extend(output_dict['data']['followUp'])
            elif output_dict['type'] == 'finished':
                break
            else:
                continue
    return {'sources': sources, 'llm': md(llm_output), 'relevant': relevant}

if __name__ == "__main__":
    # check_whats_happening("RELIANCE")
    print(fetch_and_parse_perplexity_output("what is meow")['llm'])