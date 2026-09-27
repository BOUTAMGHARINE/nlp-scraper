import feedparser
import requests
from bs4 import BeautifulSoup
import sqlite3
import datetime



urls = [
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://feeds.bbci.co.uk/news/uk/rss.xml",
    "https://feeds.bbci.co.uk/news/business/rss.xml",
    "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
    "https://feeds.bbci.co.uk/news/health/rss.xml",
    "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
    "https://feeds.bbci.co.uk/news/politics/rss.xml",
    "https://feeds.bbci.co.uk/news/education/rss.xml",
    "https://feeds.bbci.co.uk/news/world/africa/rss.xml",
    "https://feeds.bbci.co.uk/news/world/asia/rss.xml",
    "https://feeds.bbci.co.uk/news/world/europe/rss.xml",
    "https://feeds.bbci.co.uk/news/world/latin_america/rss.xml",
    "https://feeds.bbci.co.uk/news/world/middle_east/rss.xml",
     "https://feeds.bbci.co.uk/news/topics/c8nq32jw5r5t/rss.xml",
    "https://feeds.bbci.co.uk/news/topics/c302m85q5jjt/rss.xml",
    "https://feeds.bbci.co.uk/news/topics/cx1m7zg05wpt/rss.xml",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://rss.dw.com/rdf/rss-en-all",
    "https://www.euronews.com/rss",
    "https://www.theguardian.com/world/rss",
    "https://www.theguardian.com/business/rss",
    "https://www.theguardian.com/technology/rss",
    "https://www.theguardian.com/science/rss",
    "https://feeds.npr.org/1001/rss.xml",
    "https://feeds.npr.org/1004/rss.xml",
    "https://feeds.npr.org/1006/rss.xml",
    "https://feeds.npr.org/1007/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Science.xml",
    "https://techcrunch.com/feed/",
    "https://feeds.arstechnica.com/arstechnica/index",
    "https://www.nature.com/nature.rss",
    "https://www.sciencedaily.com/rss/all.xml",
    "https://www.sciencedaily.com/rss/top/science.xml",
    "https://www.sciencedaily.com/rss/top/technology.xml",
    "https://www.sciencedaily.com/rss/top/environment.xml",
    "https://www.sciencedaily.com/rss/top/health.xml",
    "https://www.wired.com/feed/rss",

]

time_now = datetime.datetime.now()
articls  =  0

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
    global articls
    blog_feed = feedparser.parse(url)
    content = blog_feed.entries

    for entry in content:
        print("articl :",articls)
        if articls >= 400 :
            break
        
        
        
        if not hasattr(entry, "published_parsed"):
            continue

    

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
            articls+=1
           
         
            
                        

        else:
            print("Article body not found")
            continue


    conn.commit()


for url in urls:
    print("articl :",articls)
    if articls >= 400 :
        break
    scraper_news(url)

conn.close()