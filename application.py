import sys
import tweepy
import sqlite3
import os
from datetime import datetime
from pprint import pprint
from gnews import GNews
from pysummarization.nlpbase.auto_abstractor import AutoAbstractor
from pysummarization.tokenizabledoc.simple_tokenizer import SimpleTokenizer
from pysummarization.abstractabledoc.top_n_rank_abstractor import TopNRankAbstractor
from fuzzywuzzy import fuzz
from fuzzywuzzy import process









db = Database()
db.create_article_table()
db.create_timeline_table()
print(f"Fetching news article {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}")
x = Twitter().country_info(codes=["US", "CA"])
News(x).trending_article()
