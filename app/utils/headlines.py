from bs4 import BeautifulSoup
import requests

def get_mc_news():
    # Create dictionaries to store categorized headlines and URLs
    categorized_news = {
        'Stock Market News 📈': [],
        'Company News 🧑‍💻': [],
        'All News 📰': [],
    }

    # Define the URLs for each category
    urls = {
        'All News 📰': [f'https://www.moneycontrol.com/news/news-all/page-{i}' for i in range(1, 3)],
        'Stock Market News 📈': ['https://www.moneycontrol.com/news/business/stocks'],
        'Company News 🧑‍💻': ['https://www.moneycontrol.com/news/tags/companies.html']
    }

    # Function to process each URL and categorize news
    def process_url(url, category):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all h2 tags with news headlines
        sections = soup.find_all('h2')

        for section in sections:
            a_tag = section.find('a')
            if a_tag:
                headline = a_tag.get_text(strip=True)
                link = a_tag['href']
                categorized_news[category].append({'headline': headline, 'url': link})

    # Process URLs for each category
    for category, url_list in urls.items():
        for url in url_list:
            process_url(url, category)

    return categorized_news

def get_et_news():
    # Create a dictionary to store categorized headlines and URLs
    categorized_news = {
        'Latest News 📰': []
    }

    # Define the URL for the "just-in" section
    url = 'https://economictimes.indiatimes.com/markets'

    # Function to extract 'just-in' section
    def extract_latest_news(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        just_in_section = soup.find('ul', id='just_in')

        if just_in_section:
            items = just_in_section.find_all('li')
            for item in items:
                a_tag = item.find('a')
                if a_tag:
                    headline = a_tag.get_text(strip=True)
                    link = a_tag['href']
                    categorized_news['Latest News 📰'].append({'headline': headline, 'url': link})

    # Extract the latest news
    extract_latest_news(url)

    return categorized_news


def format_news_as_markdown(categorized_news):
    markdown = ""
    for category, articles in categorized_news.items():
        markdown += f"#### {category}\n\n"
        for article in articles:
            markdown += f"- [{article['headline']}]({article['url']})\n"
        markdown += "\n"
    return markdown