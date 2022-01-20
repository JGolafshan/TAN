import sys, tweepy, schedule, time, sqlite3, os
from datetime import datetime
from pprint import pprint
from gnews import GNews
from pysummarization.nlpbase.auto_abstractor import AutoAbstractor
from pysummarization.tokenizabledoc.simple_tokenizer import SimpleTokenizer
from pysummarization.abstractabledoc.top_n_rank_abstractor import TopNRankAbstractor
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

class Twitter:
    def __init__(self):
        auth = tweepy.OAuthHandler("HgrXzpH5fqfvosL6vSm9aYZqX", "yKXBs1vBUJSQWOVNMSktGkOKBFiKUPQidCVLYLemOXa3fG3Ws7")
        auth.set_access_token("3295534592-IiBIJWqSQqKMZKVCEL04RwRgWaXAnB6TMb8VHyi",
                              "M1Gn67DBn5pcK5rGcExFi1PAT8mQpTjXwj15DefXebABW")
        self.api = tweepy.API(auth)

    def check_credentials(self):
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
        self.auto_abstractor = AutoAbstractor()

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
        news_article = google_news.get_news(keyword)[0]
        dt_formats = ["%Y/%m/%d %H:%M:%S", "%a, %d %b %Y %H:%M:%S GMT"]

        if len(news_article) >= 1:
            full_article = google_news.get_full_article(url=news_article["url"])
            summarise = ""

            if full_article.is_valid_body() is True:
                summarise = self.summarise(full_article.text)
            pub_date = datetime.strptime(news_article["published date"], dt_formats[1]).strftime(dt_formats[0])
            self.database.insert_into_article(url=full_article.url, title=full_article.title, body=full_article.text,
                                              summery=summarise, date=pub_date,
                                              publisher=news_article["publisher"]["title"])

    def summarise(self, document):
        self.auto_abstractor.tokenizable_doc = SimpleTokenizer()
        self.auto_abstractor.delimiter_list = [".", "\n"]
        result_dict = self.auto_abstractor.summarize(document, TopNRankAbstractor())
        print(result_dict)
        max_score = (0, 0)
        for sentence in result_dict["scoring_data"]:
            if max_score[1] < sentence[1]:
                max_score = sentence
        return result_dict["summarize_result"][max_score[0]]

    def trending_article(self):
        for country in self.data:
            for trend in self.trends(country=country.get("countryId")):
                try:
                    self.article(country=country.get("countryAbbreviated"), keyword=trend.get("name"))
                except tweepy.errors.Forbidden:
                    break


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(os.path.abspath(os.curdir) + '/NewsDB.db')
        self.cursor = self.conn.cursor()

    def create_timeline_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Timeline
                            (
                                TimelineID INTEGER PRIMARY KEY AUTOINCREMENT,
                                ArticleID INTEGER,
                                TimelineGeotag VARCHAR(4),
                                TimelineKeyword TEXT,
                                TimelinePostedDate DATETIME,
                                FOREIGN KEY(ArticleID) REFERENCES Article(ArticleID)
                            );""")
        self.conn.commit()

    def create_article_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Article
                            (
                                ArticleID INTEGER PRIMARY KEY AUTOINCREMENT,
                                ArticleURL TEXT,
                                ArticleTitle TEXT,
                                ArticleBody TEXT,
                                ArticleSummery TEXT,
                                ArticlePublishedDate DATETIME,
                                ArticlePublisher TEXT
                            );""")
        self.conn.commit()

    def insert_into_timeline(self, article_id, geo_location, keyword, post_time):
        self.cursor.execute(
            """INSERT INTO  Timeline (ArticleID, TimelineGeotag, TimelineKeyword, TimelinePostedDate)
            VALUES (?,?,?,?);""", (article_id, geo_location, keyword, post_time)
        )
        self.conn.commit()

    def insert_into_article(self, url, title, body, summery, date, publisher):
        self.cursor.execute(
            """INSERT INTO Article(ArticleURL, ArticleTitle, ArticleBody, ArticleSummery, ArticlePublishedDate, ArticlePublisher)
            VALUES (?,?,?,?,?,?);""", (url, title, body, summery, date, publisher)
        )
        self.conn.commit()

    def check_similar_posts(self, period, post_object):
        self.cursor.executemany("""SELECT * FROM Article WHERE""")
        self.conn.commit()


db = Database()
db.create_article_table()
db.create_timeline_table()
print(f"Fetching news article {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}")
x = Twitter().country_info(codes=["AU", "US", "CA"])
News(x).trending_article()
