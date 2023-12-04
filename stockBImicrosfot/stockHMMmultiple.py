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
import pandas_market_calendars as mcal

# Setting up mysql cursor (read)
connection = mysql.connector.connect(
    user     = envVariables.user,
    password = envVariables.password,
    host     = envVariables.host,
    database = 'stockanalysis'                                 
)
cursor = connection.cursor()


# Getting data from mysql into a dataframe
cursor.execute("SELECT * FROM stockEntriesDailyMSFT")
myresult = cursor.fetchall()
data_Original = pd.DataFrame(myresult,columns=['Index','Open','High','Low','Close','senP','Datetime'])


# Dataframe to save predicted values
predictions = pd.DataFrame(columns=['datetime_','predOpen','predClose'])

# Loopable
daysToPredict = 30
for i in tqdm(range(daysToPredict)):
    # Getting daily version of mysql data
    data = data_Original[0:data_Original.shape[0]-(daysToPredict-1-i)]
    
    # Splitting data
    train_size = int(0.8*data.shape[0])
    train_data = data.iloc[0:train_size]
    test_data = data.iloc[train_size+1:]
    
    # Predicting next day open price__________________________________________________________________________________
    # Define function to extract features from dataframe
    def augment_features(dataframe):
        count = dataframe.shape[0]
        new_dataframe = pd.DataFrame(columns=['closeopen','closehigh','closelow','closeOpen','senP']) 
        for i in range(count-1):
            # Calculations
            closeopenStat    = (dataframe.iloc[i]['Open']-dataframe.iloc[i]['Close'])/dataframe.iloc[i]['Close']
            closehighStat    = (dataframe.iloc[i]['High']-dataframe.iloc[i]['Close'])/dataframe.iloc[i]['Close']
            closelowStat     = (dataframe.iloc[i]['Low']-dataframe.iloc[i]['Close'])/dataframe.iloc[i]['Close']
            closeOpenStat    = (dataframe.iloc[i+1]['Open']-dataframe.iloc[i]['Close'])/dataframe.iloc[i]['Close']
            senPStat = dataframe.iloc[i]['senP']
            
            # Appendage
            new_dataframe.loc[len(new_dataframe)] = [closeopenStat, closehighStat, closelowStat, closeOpenStat, senPStat]    
        return new_dataframe

    def extract_features(dataframe):
        return np.column_stack((dataframe['closeopen'], dataframe['closehigh'], dataframe['closelow'], dataframe['closeOpen'], dataframe['senP']))

    # Extracting features
    feature_train_data = augment_features(train_data)
    features_train = extract_features(feature_train_data)
    model = GaussianHMM(n_components=10)
    model.fit(features_train)

    test_augmented  = augment_features(test_data)
    closeopenStat    = test_augmented['closeopen']
    closehighStat    = test_augmented['closehigh']
    closelowStat     = test_augmented['closehigh']
    closeOpenStat   = test_augmented['closeOpen']
    senPStat        = test_augmented['senP']

    sample_space_closeopenStat   = np.linspace(closeopenStat.min() , closeopenStat.max() , 10)
    sample_space_closehighStat   = np.linspace(closehighStat.min() , closehighStat.max() , 10)
    sample_space_closelowStat    = np.linspace(closelowStat.min()  , closelowStat.max()  , 10)
    sample_space_closeOpenStat   = np.linspace(closeOpenStat.min() , closeOpenStat.max(), 50)
    sample_space_senPStat        = np.linspace(senPStat.min()      , senPStat.max()     , 10)
    
    possible_outcomes = np.array(list(itertools.product(sample_space_closeopenStat, sample_space_closehighStat, sample_space_closelowStat, sample_space_closeOpenStat, sample_space_senPStat)))

    # Extract feature from test data
    previous_data = extract_features(augment_features(test_data))
    outcome_scores = []
    for outcome in tqdm(possible_outcomes): # tqdmable
        # Append each outcome one by one with replacement to see which sequence generates the highest score
        total_data = np.row_stack((previous_data, outcome))
        outcome_scores.append(model.score(total_data))
        
    # Take the most probable outcome as the one with the highest score
    most_probable_outcome = possible_outcomes[np.argmax(outcome_scores)]
    predicted_open_price = test_data.iloc[test_data.shape[0]-1]['Close'] * (1 + most_probable_outcome[3])

    # Predicting next day close price__________________________________________________________________________________
    def augment_features(dataframe):
        fracocp = (dataframe['Close']-dataframe['Open'])/dataframe['Open']
        frachp = (dataframe['High']-dataframe['Open'])/dataframe['Open']
        fraclp = (dataframe['Open']-dataframe['Low'])/dataframe['Open']
        senPStat = dataframe['senP']
        new_dataframe = pd.DataFrame({'delOpenClose': fracocp,
                                    'delHighOpen': frachp,
                                    'delLowOpen': fraclp,
                                    'senP': senPStat})
        new_dataframe.set_index(dataframe.index)
        
        return new_dataframe

    def extract_features(dataframe):
        return np.column_stack((dataframe['delOpenClose'], dataframe['delHighOpen'], dataframe['delLowOpen'], dataframe['senP']))
    features = extract_features(augment_features(train_data))

    # Extracting features
    feature_train_data = augment_features(train_data)
    features_train = extract_features(feature_train_data)
    model = GaussianHMM(n_components=10)
    model.fit(features_train)

    test_augmented = augment_features(test_data)
    fracocp = test_augmented['delOpenClose']
    frachp = test_augmented['delHighOpen']
    fraclp = test_augmented['delLowOpen'] 
    senPStat = test_augmented['senP'] 

    sample_space_fracocp = np.linspace(fracocp.min(), fracocp.max(), 50)
    sample_space_fraclp = np.linspace(fraclp.min(), frachp.max(), 10)
    sample_space_frachp = np.linspace(frachp.min(), frachp.max(), 10)
    sample_space_senP = np.linspace(senPStat.min(), senPStat.max(), 10)

    possible_outcomes = np.array(list(itertools.product(sample_space_fracocp, sample_space_frachp, sample_space_fraclp, sample_space_senP)))

    # Extract feature from test data
    previous_data = extract_features(augment_features(test_data))
    outcome_scores = []
    for outcome in tqdm(possible_outcomes): # tqdmable
        # Append each outcome one by one with replacement to see which sequence generates the highest score
        total_data = np.row_stack((previous_data, outcome))
        outcome_scores.append(model.score(total_data))
        
    # Take the most probable outcome as the one with the highest score
    most_probable_outcome = possible_outcomes[np.argmax(outcome_scores)]
    predicted_close_price = predicted_open_price * (1 + most_probable_outcome[0])

    # Get next day str
    curDay = test_data.iloc[test_data.shape[0]-1]['Datetime']
    date_format = '%Y-%m-%d'
    curDay = datetime.strptime(curDay,date_format)
    nyse = mcal.get_calendar('NYSE')
    validDays = nyse.valid_days(start_date=curDay.strftime('%Y-%m-%d'),end_date=(curDay+timedelta(days=7)))
    validDay = validDays[0]
    nextdayStr = validDay.strftime('%Y-%m-%d')

    # Adding prediction into database
    predictions.loc[len(predictions.index)] = [nextdayStr, predicted_close_price, predicted_open_price]

    # End of predictions________________________________________________________


# Creating column list for insertion
cols = ",".join([str(i) for i in predictions.columns.tolist()])

# Inserting DataFrame records one by one. (database name changable)
for i,row in predictions.iterrows():
    sql = "INSERT INTO stockPredictionMSFT (" +cols + ") VALUES (" + "%s,"*(len(row)-1) + "%s)"
    cursor.execute(sql, tuple(row))
    connection.commit()
    
print("Done!")



