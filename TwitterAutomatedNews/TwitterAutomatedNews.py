from pysummarization.abstractabledoc.top_n_rank_abstractor import TopNRankAbstractor
from pysummarization.tokenizabledoc.simple_tokenizer import SimpleTokenizer
from pysummarization.nlpbase.auto_abstractor import AutoAbstractor
from pytrends.request import TrendReq
from operator import itemgetter
from newspaper import Article
from datetime import datetime
from gnews import GNews
import sqlite3
import tweepy
import time
import os


class TAN:
    def __init__(self):
        self.twitter = Twitter()
        self.news = News()
        self.database = Database()
        self.dt_formats = ["%a, %d %b %Y %H:%M:%S GMT", "%Y-%m-%d %H:%M:%S"]

    def retrieve_articles(self):
        self.database.create_database()
        trends = self.news.trends()
        last_row = self.database.cursor.lastrowid

        for index, row in trends.iterrows():
            article = self.news.article(row.values[0])
            complete_article = self.news.full_article(link_url=article[0]["url"])

            self.database.insert_into_article(
                url=article[0]["url"], title=article[0]["title"],
                publisher=article[0]["publisher"]["title"], body=complete_article.text,
                date=datetime.strptime(article[0]["published date"], self.dt_formats[0]).strftime(self.dt_formats[1]),
                keyword=row.values[0])

        return last_row

    def add_to_twitter(self):
        article_db = self.database.select_articles(self.retrieve_articles(), self.database.cursor.lastrowid)
        for article in article_db:
            self.database.check_similarity()
            # self.twitter.post(description=self.news.summarize(article[3]), url=article[1])
            self.database.insert_into_timeline(article[0], post_time=datetime.now())
            time.sleep(10)


class Twitter:
    def __init__(self):
        auth = tweepy.OAuthHandler("HgrXzpH5fqfvosL6vSm9aYZqX", "yKXBs1vBUJSQWOVNMSktGkOKBFiKUPQidCVLYLemOXa3fG3Ws7")
        auth.set_access_token("3295534592-IiBIJWqSQqKMZKVCEL04RwRgWaXAnB6TMb8VHyi",
                              "M1Gn67DBn5pcK5rGcExFi1PAT8mQpTjXwj15DefXebABW")
        self.api = tweepy.API(auth)

    def check_credentials(self):
        """
            Checks the user credentials
            prints out the result,
            if the function finds an error it quits the program
        """
        try:
            self.api.verify_credentials()
            print('Authentication OK')
        except KeyError:
            print('Error during authentication')
            sys.exit()

    def post(self, description, url):
        """
        posts a status with the inputted strings
        the summery gives a brief overview of the article, the url link to the article
        Args:
            description (str): description of article
            url (str): external link to article
        Returns: None
        """
        return self.api.update_status(f"{description} \n {url}")


class News:
    def __init__(self):
        self.gtrends = TrendReq(hl='en-US', geo='GLOBAL')
        self.news = GNews()
        self.auto_abstractor = AutoAbstractor()

    def trends(self):
        return self.gtrends.trending_searches()

    def article(self, keyword):
        return self.news.get_news(keyword)

    def full_article(self, link_url):
        full_article = Article(url=link_url, language='en')
        full_article.download()
        full_article.parse()
        return full_article

    def summarize(self, description):
        self.auto_abstractor.tokenizable_doc = SimpleTokenizer()
        self.auto_abstractor.delimiter_list = [".", "\n"]
        result_dict = self.auto_abstractor.summarize(description, TopNRankAbstractor())

        max_score = max(result_dict["scoring_data"], key=itemgetter(1))[0]
        return str(result_dict["summarize_result"][max_score])


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(os.path.abspath(os.curdir) + '/NewsDB.db')
        self.cursor = self.conn.cursor()

    def create_timeline_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Timeline
                            (
                                TimelineID INTEGER PRIMARY KEY AUTOINCREMENT,
                                ArticleID INTEGER,
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
                                ArticleKeyword TEXT,
                                ArticlePublishedDate DATETIME,
                                ArticlePublisher TEXT
                            );""")
        self.conn.commit()

    def create_database(self):
        """
        Creates the database and all tables
        """
        self.create_article_table()
        self.create_timeline_table()

    def select_articles(self, start, end):
        sql_string = "select * from Article where ArticleID >= {0} and ArticleID <= {1}".format(start, end)
        return self.cursor.execute(sql_string, ()).fetchall()

    def check_similarity(self):
        pass

    def insert_into_timeline(self, article_id, post_time):
        self.cursor.execute(
            """INSERT INTO  Timeline (ArticleID, TimelinePostedDate)
            VALUES (?,?);""", (article_id, post_time))
        self.conn.commit()

    def insert_into_article(self, url, title, body, keyword, date, publisher):
        self.cursor.execute(
            """INSERT INTO Article(ArticleURL, ArticleTitle, ArticleBody, ArticleKeyword, ArticlePublishedDate, ArticlePublisher)
            VALUES (?,?,?,?,?,?);""", (url, title, body, keyword, date, publisher))
        self.conn.commit()
