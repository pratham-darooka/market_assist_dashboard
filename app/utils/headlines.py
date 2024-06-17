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

def get_finshots_news():
    # Create a dictionary to store categorized headlines and URLs
    categorized_news = {
        'Daiy Finshots 📰': []
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

def get_finshots_news():
    # Create a dictionary to store categorized headlines and URLs
    categorized_news = {
        'Daily Articles 📰': []
    }

    # Define the URL for the "archive" section
    url = 'https://finshots.in/archive/'

    # Function to extract the latest news
    def extract_latest_news(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        # Find all articles in the post feed
        articles = soup.find_all('article', class_='post-card')

        for article in articles:
            # Find the title and the link
            link_tag = article.find('a', class_='post-card-content-link')
            title_tag = article.find('h2', class_='post-card-title')
            excerpt_tag = article.find('section', class_='post-card-excerpt')
            
            if link_tag and title_tag:
                headline = title_tag.get_text(strip=True)
                link = link_tag['href']
                excerpt = excerpt_tag.get_text(strip=True) if excerpt_tag else None
                categorized_news['Daily Articles 📰'].append({'headline': headline, 'url': f'https://finshots.in{link}', 'excerpt': excerpt})

    # Extract the latest news
    extract_latest_news(url)

    return categorized_news

def format_news_as_markdown(categorized_news, include_excerpt=False, limit=5):
    markdown = ""
    for category, articles in categorized_news.items():
        markdown += f"#### {category}\n\n"
        for article in articles[:limit]:
            if include_excerpt and 'excerpt' in article:
                markdown += f"- **[{article['headline']}]({article['url']})**\n  \n  *{article['excerpt']}*\n"
            else:
                markdown += f"- [{article['headline']}]({article['url']})\n"
        markdown += "\n"
    return markdown