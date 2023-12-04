import mysql.connector
import envVariables
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display
import datetime as dt
from datetime import datetime
from newspaper import Article
from newspaper import Config
from gnews import GNews
import nltk
from textblob import TextBlob
import time
from tqdm import tqdm
nltk.download('punkt')

# Setting up user agent
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
config = Config()
config.browser_user_agent = user_agent

# Setting up mysql cursor (read)
connection = mysql.connector.connect(
    user     = envVariables.user,
    password = envVariables.password,
    host     = envVariables.host,
    database = 'stockanalysis'                                 
)
cursor = connection.cursor()

# Getting data from mysql into a dataframe
cursor.execute("SELECT * FROM stockentriesdailyMSFT")
myresult = cursor.fetchall()
data = pd.DataFrame(myresult,columns=['Index','Open','High','Low','Close','senP','Datetime'])


date_format = '%Y-%m-%d'
# Looping through and updating senP
for index, row in tqdm(data.iterrows()):
    rowDate = datetime.strptime(row['Datetime'],date_format)
    # Get gnews
    google_news = GNews(language='english',country='US',start_date=rowDate-dt.timedelta(days=1),end_date=rowDate,exclude_websites=['forbes.com'])
    rsp = google_news.get_news("Microsoft")
    newsdata = pd.DataFrame(rsp)
    dailySenP = 0
    for indexi, rowi in newsdata.iterrows():
        url = rowi['url']
        article = Article(url)
        try:
            article.download()
            article.parse()
            article.nlp()
            text = article.summary 
            blob = TextBlob(text)
            dailySenP += blob.sentiment.polarity
        except Exception:
            pass
    data.at[index,'senP'] = dailySenP

# Dealing with outliers
percentile25 = data['senP'].quantile(0.25)
percentile75 = data['senP'].quantile(0.75)
iqr = percentile75 = percentile25
upper_limit = percentile75 + 1.5 * iqr
lower_limit = percentile25 - 1.5 * iqr

new_df_cap = data.copy()
new_df_cap['senP'] = np.where(new_df_cap['senP'] > upper_limit,upper_limit,np.where(new_df_cap['senP'] < lower_limit,lower_limit,new_df_cap['senP']))


# sns.distplot(data['senP'])
# plt.show()

# sns.distplot(new_df_cap['senP'])
# plt.show()

# Updating mysql
for index, row in tqdm(new_df_cap.iterrows()):
    sql = "UPDATE stockentriesdailyMSFT SET senP = "+str(round(row['senP'],4))+ " WHERE index_ = "+str(row['Index'])
    cursor.execute(sql)
    connection.commit()
    
display(data)   
        
    
