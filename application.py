import sys, tweepy, schedule, time, sqlite3, os
from datetime import datetime
from pprint import pprint
from gnews import GNews


# TODO - change summery from title to a short desc of story
# TODO - Random postings when doing hourly post
# TODO - create keyword matrix, use this to ignore articles

class Twitter:
    """This class runs all functions related to twitter.
       (checks credentials, posts tweets and replies"""

    def __init__(self):
        auth = tweepy.OAuthHandler("HgrXzpH5fqfvosL6vSm9aYZqX", "yKXBs1vBUJSQWOVNMSktGkOKBFiKUPQidCVLYLemOXa3fG3Ws7")
        auth.set_access_token("3295534592-IiBIJWqSQqKMZKVCEL04RwRgWaXAnB6TMb8VHyi",
                              "M1Gn67DBn5pcK5rGcExFi1PAT8mQpTjXwj15DefXebABW")
        self.api = tweepy.API(auth)

    def check_credentials(self):
        """verify twitter credentials, api keys are wrong"""
        try:
            self.api.verify_credentials()
            print('Authentication OK')
        except KeyError:
            print('Error during authentication')
            sys.exit()

    def post(self, summery, url):
        return self.api.update_status(f"{summery} \n {url}")

    def country_info(self, codes):
        country = []
        countries = self.api.available_trends()
        for i in range(len(codes)):
            for j in range(len(countries)):
                if codes[i] == countries[j].get("countryCode"):
                    country.append({"countryAbbreviated": codes[i], "countryId": countries[j].get("woeid")})
                    break
        return country


class News:
    def __init__(self, data):
        self.data = data
        self.database = Database()
        self.twitter = Twitter()

    def trends(self, country):
        trends = self.twitter.api.get_place_trends(country)[0].get("trends")
        trends_list = []
        volume_sum = 0

        for trend in trends:
            if trend.get("tweet_volume") is not None:
                volume_sum += trend.get("tweet_volume")
                trends_list.append(trend)

        volume_mean = int(volume_sum / len(trends_list))
        trends_list = []

        for trend in trends:
            if trend.get("tweet_volume") is not None and trend.get("tweet_volume") >= volume_mean:
                trends_list.append(trend)

        return trends_list

    def article(self, country, keyword):
        google_news = GNews(country=country, max_results=1, period="6h")
        news_article = google_news.get_news(keyword)
        dt_formats = ["%Y/%m/%d %H:%M:%S", "%a, %d %b %Y %H:%M:%S GMT"]

        if len(news_article) >= 1:
            pub_date = datetime.strptime(news_article[0].get("published date"), dt_formats[1]).strftime(dt_formats[0])
            self.database.insert_article(geo_loc=country, published_date=pub_date, url=news_article[0].get("url"),
                keyword=keyword, post_time=datetime.now().strftime(dt_formats[0]))
            # self.twitter.post(news_article[0].get("title"), news_article[0].get("url"))

    def trending_article(self):
        for country in self.data:
            for trend in self.trends(country=country.get("countryId")):
                self.article(country=country.get("countryAbbreviated"), keyword=trend.get("name"))


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(os.path.abspath(os.curdir) + '/NewsDB.db')
        self.cursor = self.conn.cursor()

    def create_db(self):
        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS NewsArticle
                            (
                                NewsArticleID INTEGER PRIMARY KEY AUTOINCREMENT,
                                NewsArticleGeoLocation VARCHAR(4),
                                NewsArticlePublishedDate DATETIME,
                                NewsArticleURL TEXT,
                                NewsArticleKeyword TEXT,
                                NewsArticlePostedDate DATETIME
                            );""")
        self.conn.commit()

    def insert_article(self, geo_loc, published_date, url, keyword, post_time):
        self.cursor.execute(
            f"""INSERT INTO  NewsArticle (
                NewsArticleGeoLocation, NewsArticlePublishedDate, 
                NewsArticleURL, NewsArticleKeyword, NewsArticlePostedDate
            ) 
            VALUES (?,?,?,?,?);""", (geo_loc, published_date, url, keyword, post_time)
        )
        self.conn.commit()


def job():
    print("working")
    x = Twitter().country_info(codes=["AU", "US", "CA"])
    News(x).trending_article()
    # pprint(News(x).trends(x[0].get("countryId")))


Database().create_db()
job()

# schedule.every().hour.do(job)
# while True:
#     schedule.run_pending()
#     time.sleep(1)
