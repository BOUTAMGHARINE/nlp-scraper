import feedparser
import requests
from bs4 import BeautifulSoup
import sqlite3
import datetime





url1 = "https://feeds.bbci.co.uk/news/rss.xml"
url2 = "https://feeds.bbci.co.uk/news/world/rss.xml"
url3="https://feeds.bbci.co.uk/news/uk/rss.xml"
url4="https://feeds.bbci.co.uk/news/business/rss.xml"
url5="https://feeds.bbci.co.uk/news/technology/rss.xml"
url6="https://feeds.bbci.co.uk/news/science_and_environment/rss.xml"
url7="https://feeds.bbci.co.uk/news/health/rss.xml"
url8="https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml"
url9="https://feeds.bbci.co.uk/news/politics/rss.xml"

time_now = datetime.datetime.now()

def create_database() :
    conn = sqlite3.connect("news.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            link TEXT UNIQUE,
            date TEXT,
            summary TEXT,
            body TEXT
        )
    """)
    return cursor,conn
cursor,conn = create_database()


def scraper_news(url):
    blog_feed = feedparser.parse(url)
    content = blog_feed.entries

    for entry in content:

    

        response = requests.get(entry.link)

        if response.status_code != 200 :
            print("Failed to fetch:",response.status_code)
            continue

        soup = BeautifulSoup(response.content, "html.parser")

        article = soup.find("article")
        article_date = datetime.datetime(*entry.published_parsed[:6])


        if article and time_now - article_date <= datetime.timedelta(days=7):
            paragraphs = article.find_all("p")

            body = " ".join(
                p.get_text(strip=True)
                for p in paragraphs
            )
            cursor.execute("""
                INSERT OR IGNORE INTO articles
                (title, link, date, summary, body)
                VALUES(?,?,?,?,?)

            """,(
                entry.title,
                entry.link,
                entry.published,
                entry.summary,
                body
            ))
            

        else:
            print("Article body not found")
            continue


        print("-" * 70)
    conn.commit()


scraper_news(url1)
scraper_news(url2)
scraper_news(url3)
scraper_news(url4)
scraper_news(url5)
scraper_news(url6)
scraper_news(url7)
scraper_news(url8)
scraper_news(url9)
conn.close()
