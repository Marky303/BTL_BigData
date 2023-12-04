import mysql.connector
import envVariables
import pandas as pd
from hmmlearn.hmm import GaussianHMM
import numpy as np
import itertools
from tqdm import tqdm
import matplotlib.pyplot as plt
from datetime import datetime, date, timedelta
import datetime as dt
import seaborn as sns

# Setting up mysql cursor (read)
connection = mysql.connector.connect(
    user     = envVariables.user,
    password = envVariables.password,
    host     = envVariables.host,
    database = 'stockanalysis'                                 
)
cursor = connection.cursor()

# Getting data from mysql into a dataframe
cursor.execute("SELECT * FROM stockEntriesDaily")
myresult = cursor.fetchall()
data = pd.DataFrame(myresult,columns=['Index','Open','High','Low','Close','senP','Datetime'])

# Changing date format
for index, row in tqdm(data.iterrows()):
    dateStr = row['Datetime']
    date_format = '%Y-%m-%d %H:%M:%S%z'
    datetime_ = datetime.strptime(dateStr,date_format)  # Convert to date
    dateStr = datetime_.strftime('%Y-%m-%d')    # Convert to string
    data.at[index,'Datetime'] = dateStr
    
for index, row in tqdm(data.iterrows()):
    sql = "UPDATE stockentriesdaily SET datetime_ = '"+row['Datetime']+"' WHERE index_ = "+str(row['Index'])
    cursor.execute(sql)
    connection.commit()
    
# Getting data from mysql into a dataframe
cursor.execute("SELECT * FROM stockPredictionAAPL")
myresult = cursor.fetchall()
data = pd.DataFrame(myresult,columns=['Datetime','predOpen','predClose'])

# Changing date format
for index, row in tqdm(data.iterrows()):
    dateStr = row['Datetime']
    date_format = '%Y-%m-%d %H:%M:%S%z'
    datetime_ = datetime.strptime(dateStr,date_format)  # Convert to date
    dateStr = datetime_.strftime('%Y-%m-%d')    # Convert to string
    data.at[index,'Datetime'] = dateStr
    
for index, row in tqdm(data.iterrows()):
    sql = "UPDATE stockPredictionAAPL SET datetime_ = '"+row['Datetime']+"' WHERE predOpen = "+str(row['predOpen'])
    cursor.execute(sql)
    connection.commit()