from datetime import datetime
from TwitterAutomatedNews import twitter, news, database

db = database.Database()
db.create_article_table()
db.create_timeline_table()
print(f"Fetching news article {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}")
x = twitter.Twitter().country_info(codes=["US", "CA"])
news.News(x).trending_article()
