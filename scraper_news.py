import feedparser
import requests
from bs4 import BeautifulSoup
import sqlite3




url = "https://feeds.bbci.co.uk/news/rss.xml"


def creat_database() :
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


def scraper_news(url):
    blog_feed = feedparser.parse(url)
    content = blog_feed.entries
    cursor,conn = creat_database()

    for entry in content:

    

        response = requests.get(entry.link)

        if response.status_code != 200 :
            print("Failed to fetch:",response.status_code)
            continue

        soup = BeautifulSoup(response.content, "html.parser")

        article = soup.find("article")

        if article:
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
    conn.close()


scraper_news(url)