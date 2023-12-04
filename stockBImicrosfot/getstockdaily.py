from polygon import RESTClient
import pandas as pd
from IPython.display import display
import mysql.connector
import envVariables
import datetime
from datetime import datetime, date, timedelta
import datetime as dt
import time
from tqdm import tqdm

while (True):
    # Setting up polygon api (for apply ticker)
    client = RESTClient(envVariables.polygonKey)
    stockTicker = 'MSFT'

    # Setting up mysql cursor (write)
    connection = mysql.connector.connect(
        user     = envVariables.user,
        password = envVariables.password,
        host     = envVariables.host,
        database = 'stockanalysis'                                 
    )
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM stockEntriesDailyMSFT")
    myresult = cursor.fetchall()
    data = pd.DataFrame(myresult,columns=['Index','Open','High','Low','Close','senP','Datetime'])

    nextIndex = data.iloc[data.shape[0]-1]['Index']+1
    nextDate = data.iloc[data.shape[0]-1]['Datetime']
    date_format = '%Y-%m-%d'
    nextDate = datetime.strptime(nextDate,date_format)+timedelta(days=1)
    nextdayStr = nextDate.strftime('%Y-%m-%d')

    dataReq = client.get_aggs(ticker=stockTicker, multiplier=1,timespan='day',from_=nextdayStr,to='2100-01-01')
    priceData = pd.DataFrame(dataReq)

    if (priceData.shape[0]!=0):
        # Indexing (might be important later on)
        length = len(priceData.index)
        indexCol = list(range(nextIndex,nextIndex+length))
        priceData['index_'] = indexCol

        # Adding human friendly date value
        priceData['Date'] = priceData['timestamp'].apply(lambda x:pd.to_datetime(x*1000000))
        priceData['DateStr'] = priceData['Date'].dt.strftime('%Y/%m/%d')

        priceData = priceData[['index_','open','high','low','close','DateStr']]
        priceData.insert(5,column='senP',value=0)

        # Changing column labels for insertion
        priceData.rename(columns = {'open':'openStat'}, inplace = True)
        priceData.rename(columns = {'high':'highStat'}, inplace = True)
        priceData.rename(columns = {'low':'lowStat'}, inplace = True)
        priceData.rename(columns = {'close':'closeStat'}, inplace = True)
        priceData.rename(columns = {'DateStr':'datetime_'}, inplace = True)

        # Creating column list for insertion
        cols = ",".join([str(i) for i in priceData.columns.tolist()])

        # Inserting DataFrame records one by one. (database name changable)
        for i,row in tqdm(priceData.iterrows()):
            sql = "INSERT INTO stockEntriesDailyMSFT (" +cols + ") VALUES (" + "%s,"*(len(row)-1) + "%s)"
            cursor.execute(sql, tuple(row))
            connection.commit()
    connection.close()
    time.sleep(86400)















