import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pandas_datareader as web
import datetime as dt
from gnews import GNews
from IPython.display import display
import pandas as pd
import datetime
from datetime import datetime
from newspaper import Article
import nltk
from textblob import TextBlob
nltk.download('punkt')

# Getting article and link
start = datetime(2015, 1, 15, 17, 0, 0)
end = datetime(2015, 1, 16, 17, 0, 0)
google_news = GNews(language='english',country='US',start_date=start,end_date=end)
rsp = google_news.get_news("Apple")
display(rsp)

data = pd.DataFrame(rsp)
display(data)

# Choosing link
linkList = data['url']
url = linkList[1]
article = Article(url)
article.download()
article.parse()
article.nlp()

text = article.summary

blob = TextBlob(text)
senP = blob.sentiment.polarity

