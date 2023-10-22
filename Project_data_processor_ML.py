# Introduction to Data Science, Luento-opetus, 2023
# Sergei Panarin
from typing import Dict, Any

# Data preprocessing

# IMPORTANT THINGS:
# Change the number of input files in the read_data function OR later replace with full data file
# FUNCTION replace owner with symbol is copied from the main branch, DELETE LATER and IMPORT

import pandas as pd
import numpy as np
import datetime as dt
import re
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from math import isnan
import plotly.express as go


# Reading the data from source:
# Pandas cannot read from GitLab URLs, so work is done with locally stored datasets.
# Go through partial files containing parts of the whole dataset
# @param  
# @return: full pandas dataframe, containing all the relevant columns from the csv files
def read_data():
    # full_data_df = pd.read_csv("full_data.csv")

    partial_dfs = []

    # range can be changed, reads segments of the full dataset
    for index in range(66):
        datafile="api_exploration/file_segments/game_data_"+str(index+1)+".csv"
        partial_dfs.append(pd.read_csv(datafile))
    
    # Combine partial dataframes into the full version
    full_data_df = pd.concat(partial_dfs)

    return full_data_df

# transform String columns into integer IDs.
# @param: pandas dataframe with the full data
# @return: pandas dataframe with developer, publisher, genres columns encoded with integer IDs
def label_encoding(data):
    to_be_encoded = ["publisher", "developer"]

    # remove everything but the first element in those columns and categorize everything
    for val in to_be_encoded:
        data[val] = data[val].apply(lambda x: str(x).split(",")[0])
        data[val] = data[val].astype('category')


    # select the category columns and apply label encoding
    cat_columns = data.select_dtypes(['category']).columns
    data[cat_columns] = data[cat_columns].apply(lambda x: x.cat.codes)

# Transforms full data dataframe into a dataframe with the following columns:
# - Genre
# - Amount of purchases
# - Interval of time (default chosen as 2 months for now)
# @param: pandas dataframe with the full data, interval integer meaning the number of months
# @return: list of dicts with pandas dataframes numbers of games and owners per genre per time interval

def genre_data_aggregation(data, interval):

    data["genres"] = data["genres"].apply(lambda x: str(x).split(","))

    # preprocess the release date column into the pandas datetime format
    data['release_date'] = pd.to_datetime(data['release_date'], dayfirst=True, format="mixed", errors='coerce')
    
    # remove whitespaces
    data['genres'] = data['genres'].map(lambda x: list(map(str.strip, x)))
    data = data[['release_date', 'genres', 'owners']]
    
    agg_data = pd.DataFrame(columns=['genre','dates','populations'])
    # big FOR loop, for now
    
    agg_data = data.explode('genres')
    agg_data = agg_data.groupby("genres")
    #describe()
    agg_data = [group for _, group in agg_data]
    
    for x in agg_data:
        x.dropna(how='any', inplace=True)
        x.sort_values(by=['release_date'], ascending=[True], inplace=True)
        #x = x.groupby( [pd.Grouper(key='release_date', freq=str(interval)+"M"), pd.Grouper('genres')] ).agg({'owners': 'sum'})
    
    
    # remove excessive columns and sort values
    # data = data[['release_date', 'genres', 'owners']].sort_values(['release_date','genres', 'owners'], ascending=[True, True, False])

    owner_dict_data = {}
    number_dict_data = {}
    # group by the time interval and get sum of the owners and number of games
    for i in range(0, len(agg_data)):  
        name = agg_data[i]['genres'].iloc[0]
        
        # group information on number of games per genre, keep name column name owners for plotting function
        number = agg_data[i].groupby(pd.Grouper(key='release_date', freq=str(interval)+"M"))['owners'].count()
        number = number.reset_index()
        
        # group information on owners of games per genre
        owners = agg_data[i].groupby(pd.Grouper(key='release_date', freq=str(interval)+"M")).agg({'owners': 'sum'})
        owners = owners.reset_index()
        
        owner_dict_data[name] = owners
        number_dict_data[name] = number
        
    return [owner_dict_data, number_dict_data]

# Resets Index of the merged dataframe
def clean_index(data):
    return data.reset_index(drop=True)

# Transforms owners column values from str of range of values into the average float value
# @param: pandas dataframe with the full data, interval integer meaning the number of months
# @return: pandas dataframe with owners column modified
def replace_owner_str_with_average_number(data):
    def replace_letters(entry):
        to_remove = {" M": "000000", " k": "000"}

        for char in to_remove.keys():
            entry = entry.replace(char, to_remove[char])

        return entry
        
    data["owners"] = data["owners"].apply(lambda name: replace_letters(name))
    data["owners"] = data["owners"].apply(lambda name: re.findall("\d+",name))
    data["owners"] = data["owners"].apply(lambda name: [int(item) for item in name])
    data["owners"] = data["owners"].apply(lambda name: float(sum(name)/len(name)))
    return data

# Encodes time as numbers for processing
# @param: pandas dataframe with the full data
# @return: pandas dataframe with time modified
def encode_time(df):
    df['release_date']=df['release_date'].map(dt.datetime.toordinal)
    return df

def lin_reg(df):
    
    y = np.asarray(df['owners'])
    X = df[['release_date']]
    #X_train, X_test, y_train, y_test = train_test_split(X,y,train_size=.7,random_state=42)
    
    model = LinearRegression() #create linear regression object
    #model.fit(X_train, y_train) #train model on train data
    model.fit(X, y)
    #model.score(X_train, y_train) #check score
    return model


# Plot the given genre data
def plot_genre_plot(dict_data: object, genre: object) -> object:
    plt.scatter(dict_data[genre]["release_date"], dict_data[genre]["owners"])
    plt.show()

"""
# Plots the release date against owners
def get_genre_plot(dict_data: object, genre: object, style: Dict[Any] = None) -> object:

    fig = go.scatter(x=dict_data[genre]["release_date"], y=dict_data[genre]["owners"])
    if style:
        fig.update(style=style)
    return fig
"""

def get_data_interval(days):
    base = dt.datetime.now()
    
    final_date = base + dt.timedelta(days=days)

    parts = list(pd.date_range(pd.Timestamp(base), pd.Timestamp(final_date), freq='2M')) 

    dates = [t.toordinal() for t in parts]
    return dates
    
if __name__ == "__main__":


    
    
    full_data_df = read_data()
    full_data_df = clean_index(full_data_df)

    label_encoding(full_data_df)
    data = replace_owner_str_with_average_number(full_data_df)
    owners_genre_data, number_genre_data = genre_data_aggregation(full_data_df, 2)
    
    genre = "Free to Play"
    
    plot_genre_plot(owners_genre_data, genre)
    plot_genre_plot(number_genre_data, genre)
    
    # 730 days = 2 years
    dates = np.array(get_data_interval(730))
    dates = dates.reshape(len(dates), 1)
    
    # GET ALL MODELS FOR ALL GENRES
    models = {}
    predictions = {}
    process_data = owners_genre_data
    for x in process_data:  
        owners_genre_data[x] = encode_time(owners_genre_data[x])
        models[x] = lin_reg(owners_genre_data[x])
        
    for genre in models:
        predictions[genre] = models[genre].predict(dates)
        
    # GET POINT OF REFERENCE
    
    
    
    
    
    pass

