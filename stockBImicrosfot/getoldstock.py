import yfinance as yahooFinance
import pandas as pd
import datetime as dt
import pandas as pd
from IPython.display import display
import mysql.connector
import envVariables
import datetime
from datetime import date
import time 
 
# Setting up mysql cursor (write)
connection = mysql.connector.connect(
    user     = envVariables.user,
    password = envVariables.password,
    host     = envVariables.host,
    database = 'stockanalysis'                                 
)
cursor = connection.cursor()
 
# in order to specify start date and 
# end date we need datetime package
import datetime
 
# startDate , as per our convenience we can modify
startDate = datetime.datetime(2020, 1, 1)
 
# endDate , as per our convenience we can modify
endDate = date.today()
getAppleInfo = yahooFinance.Ticker("MSFT")
 
# pass the parameters as the taken dates for start and end
print(getAppleInfo.history(start=startDate, end=endDate))

# Extracting dataframe
priceData = pd.DataFrame(getAppleInfo.history(start=startDate, end=endDate))

# Indexing (might be important later on)
length = len(priceData.index)
indexCount = 0
indexCol = list(range(indexCount,indexCount+length))
priceData['index_'] = indexCol
indexCount = indexCount + length

# Adding senP column
priceData.insert(5,column='senP',value=0)
priceData['DateStr'] = priceData.index.get_level_values('Date').strftime('%Y-%m-%d')

priceData = priceData[['index_','Open','High','Low','Close','senP','DateStr']]

# Changing column labels for insertion
priceData.rename(columns = {'Open':'openStat'}, inplace = True)
priceData.rename(columns = {'High':'highStat'}, inplace = True)
priceData.rename(columns = {'Low':'lowStat'}, inplace = True)
priceData.rename(columns = {'Close':'closeStat'}, inplace = True)
priceData.rename(columns = {'DateStr':'datetime_'}, inplace = True)
display(priceData)

# Creating column list for insertion
cols = ",".join([str(i) for i in priceData.columns.tolist()])

# Inserting DataFrame records one by one. (database name changable)
for i,row in priceData.iterrows():
    sql = "INSERT INTO stockEntriesDailyMSFT (" +cols + ") VALUES (" + "%s,"*(len(row)-1) + "%s)"
    cursor.execute(sql, tuple(row))
    connection.commit()