from TwitterAutomatedNews import twitter, news, database
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
import sqlite3
import os

# TODO: CreateDB Function
# TODO: Optimize SImilarity Model

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
                                ArticlePublishedDate DATETIME,
                                ArticlePublisher TEXT
                            );""")
        self.conn.commit()

    def insert_into_timeline(self, article_id, geo_location, keyword, post_time):
        self.cursor.execute(
            """INSERT INTO  Timeline (ArticleID, TimelineGeotag, TimelineKeyword, TimelinePostedDate)
            VALUES (?,?,?,?);""", (article_id, geo_location, keyword, post_time))
        self.conn.commit()

    def insert_into_article(self, url, title, body, date, publisher):
        self.cursor.execute(
            """INSERT INTO Article(ArticleURL, ArticleTitle, ArticleBody, ArticlePublishedDate, ArticlePublisher)
            VALUES (?,?,?,?,?);""", (url, title, body, date, publisher))
        self.conn.commit()

    def check_similar_posts(self, period, article_data):
        query = self.cursor.execute(f"""SELECT * FROM Article 
                                WHERE ArticlePublishedDate BETWEEN strftime("%Y/%m/%d %H:%M:%S","NOW", "{period}") 
                                AND strftime("%Y/%m/%d %H:%M:%S","NOW");""").fetchall()

        match_percentage = -999
        query_match = None
        for i in range(len(query)):

            similarity = fuzz.partial_ratio(article_data[2], query[i][3])
            if similarity > match_percentage:
                match_percentage = similarity
                query_match = query[i]

        if match_percentage == -999 or query_match is None:
            return False

        if match_percentage >= 75 and article_data[0] == query_match[1]:
            return True
        else:
            return False
