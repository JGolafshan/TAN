from pysummarization.abstractabledoc.top_n_rank_abstractor import TopNRankAbstractor
from pysummarization.tokenizabledoc.simple_tokenizer import SimpleTokenizer
from pysummarization.nlpbase.auto_abstractor import AutoAbstractor
from TwitterAutomatedNews import twitter, news, database
from datetime import datetime
from gnews import GNews
import tweepy


class News:
    def __init__(self, data):
        self.data = data
        self.database = database.Database()
        self.twitter = twitter.Twitter()
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
        news_article = google_news.get_news(keyword)
        dt_formats = ["%Y/%m/%d %H:%M:%S", "%a, %d %b %Y %H:%M:%S GMT"]

        if len(news_article) >= 1:
            full_article = google_news.get_full_article(url=news_article[0]["url"])
            pub_date = datetime.strptime(news_article[0]["published date"], dt_formats[1]).strftime(dt_formats[0])
            try:
                news = (full_article.url, full_article.title, full_article.text, pub_date,
                        news_article[0]["publisher"]["title"])
            except AttributeError:
                return None
            if full_article.is_valid_body() is True:
                summarise = self.summarise(full_article.text)
                if self.database.check_similar_posts("-12 hours", news) is False:
                    self.database.insert_into_article(url=full_article.url, title=full_article.title,
                                                      body=full_article.text, date=pub_date,
                                                      publisher=news_article[0]["publisher"]["title"])
                    self.database.insert_into_timeline(self.database.cursor.lastrowid, country, keyword, datetime.now())
                    self.twitter.post(summarise, full_article.url)

    def summarise(self, document):
        self.auto_abstractor.tokenizable_doc = SimpleTokenizer()
        self.auto_abstractor.delimiter_list = [".", "\n"]
        result_dict = self.auto_abstractor.summarize(document, TopNRankAbstractor())
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
