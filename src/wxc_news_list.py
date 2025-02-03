import os
import requests
from bs4 import BeautifulSoup

def get_wenxuecity_news():
    url = "https://www.wenxuecity.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

      # Add proxy configuration
    proxies = {
        'http': os.environ.get('HTTP_PROXY'),
        'https': os.environ.get('HTTPS_PROXY')
    } if any(os.environ.get(k) for k in ['HTTP_PROXY', 'HTTPS_PROXY']) else None
   
    articles = []
    
    try:
        response = requests.get(url, headers=headers, proxies=proxies)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Target news links in the main content area
        news_links = soup.select('div.maincontent a[href^="/news/"][href$=".html"]')
        
        for link in news_links:
            title = link.text.strip()
            url = link['href']
            
            # Handle relative URLs
            if not url.startswith('http'):
                url = f'https://www.wenxuecity.com{url}'
                
            articles.append({
                'title': title,
                'url': url
            })
            
        return articles
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return []
    except Exception as e:
        print(f"Error parsing data: {e}")
        return []

# Example usage
if __name__ == "__main__":
    news = get_wenxuecity_news()
    for idx, article in enumerate(news, 1):
        print(f"{idx}. {article['title']}")
        print(f"   {article['url']}\n")
