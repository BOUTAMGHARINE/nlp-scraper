
import feedparser


url = "https://feeds.bbci.co.uk/news/rss.xml"





def scraper_news(url):
    blog_feed =feedparser.parse(url)
    websit_title = blog_feed.feed.title
    print(websit_title)





scraper_news(url)
