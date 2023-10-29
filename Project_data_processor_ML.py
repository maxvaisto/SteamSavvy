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

import plotly
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

from math import isnan

import plotly.graph_objects as go


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
        datafile = "api_exploration/file_segments/game_data_" + str(index + 1) + ".csv"
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
    data = data_cutoff(data)

    # remove whitespaces
    data['genres'] = data['genres'].map(lambda x: list(map(str.strip, x)))
    data = data[['release_date', 'genres', 'owners']]

    agg_data = pd.DataFrame(columns=['genre', 'dates', 'populations'])
    # big FOR loop, for now

    agg_data = data.explode('genres')
    agg_data = agg_data.groupby("genres")
    # describe()
    agg_data = [group for _, group in agg_data]

    for x in agg_data:
        x.dropna(how='any', inplace=True)
        x.sort_values(by=['release_date'], ascending=[True], inplace=True)
        # x = x.groupby( [pd.Grouper(key='release_date', freq=str(interval)+"M"), pd.Grouper('genres')] ).agg({'owners': 'sum'})

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
    data["owners"] = data["owners"].apply(lambda name: re.findall("\d+", name))
    data["owners"] = data["owners"].apply(lambda name: [int(item) for item in name])
    data["owners"] = data["owners"].apply(lambda name: float(sum(name) / len(name)))
    return data


# Encodes time as numbers for processing
# @param: pandas dataframe with the full data
# @return: pandas dataframe with time modified
def encode_time(df):
    df['release_date'] = df['release_date'].map(dt.datetime.toordinal)
    return df

# Filters the data between year 1997 and present time, sorry Hellraid :(
# @param: pandas dataframe with the full data
# @return: pandas dataframe filtered by release_date
def data_cutoff(df):
    start_date = '1997-01-01'
    end_date = dt.datetime.now()
    
    mask = (df['release_date'] >= start_date) & (df['release_date'] <= end_date)
    filtered_df = df[mask]
    return filtered_df

def data_processing(df):
    df = clean_index(df)
    label_encoding(df)
    df = replace_owner_str_with_average_number(df)
    return df

def lin_reg(df):
    y = np.asarray(df['owners'])
    X = df[['release_date']].values
    # X_train, X_test, y_train, y_test = train_test_split(X,y,train_size=.7,random_state=42)

    model = LinearRegression()  # create linear regression object
    # model.fit(X_train, y_train) #train model on train data
    model.fit(X, y)
    # model.score(X_train, y_train) #check score
    return model

"""
# Plot the given genre data
def plot_genre_plot(dict_data: object, genre: object) -> object:
    plt.scatter(dict_data[genre]["release_date"], dict_data[genre]["owners"])
    plt.show()
    """
    
# Plot the given genre data with slope and predictions
def plot_genre_plot(dict_data: object, genre: object, models: object, predictions: object, lines: object, dates: object) -> object:
    plt.scatter(dict_data[genre]["release_date"], dict_data[genre]["owners"], color='blue', label='Actual data points')
    plt.plot(dict_data[genre]["release_date"], lines[genre], color='red', label='Regression line', linewidth=2)
    plt.scatter(dates, predictions[genre], color='green', marker='o', label='Future Predictions', s=100)
    plt.show()

# Plots the release date against owners
def get_genre_plot(dict_data: Dict[str, pd.DataFrame], genre: str, **figure_arguments) -> go.Figure:
    target_data = dict_data[genre]
    figure = go.Figure(data=go.Scatter(x=target_data["release_date"], y=target_data["owners"], mode='markers'))
    figure.update(**figure_arguments)
    return figure


# This function congregates all machine learning algorithms, returns 3 dictionaries with models, predictions and slopes, all per genre
def perform_regression_analysis_on_data(dict_data, dates):
    models = {}
    predictions = {}
    lines = {}
    
    process_data = dict_data
    for x in process_data:  
        dict_data[x] = encode_time(dict_data[x])
        
        models[x] = lin_reg(dict_data[x])
        predictions[x] = models[x].predict(dates)
        lines[x] = models[x].predict(np.asarray(dict_data[x]['release_date']).reshape(-1, 1))
        
        # ensure that slopes and predictions dont go below 0
        predictions[x] = np.maximum(predictions[x], 1)
        lines[x] = np.maximum(lines[x], 1)
        
    return models, predictions, lines

def get_data_interval(days):
    base = dt.datetime.now()

    final_date = base + dt.timedelta(days=days)

    parts = list(pd.date_range(pd.Timestamp(base), pd.Timestamp(final_date), freq='2M'))

    dates = [t.toordinal() for t in parts]
    return dates

# Function to check if the slope ratio of owners vs number of games is higher than average
# If yes, then it is an opportunity with many owners and few games
def get_opportunities(owner_models, number_models, genre):
    ratios = []
    for key in owner_models:
        slope1 = owner_models[key].coef_[0]
        slope2 = number_models[key].coef_[0]
        if (slope2 != 0):
            ratios.append(slope1 / slope2)
        else: 
            ratios.append(0)

    #average = sum(ratios) / len(ratios)
    opportunity = owner_models[genre].coef_[0]/number_models[genre].coef_[0]
    
    return opportunity
    #return (opportunity > average)

# Sort the python dictionary and get average value
def opportunity_transfrom(opportunities):
    # Calculate the average of the values
    #average_value = np.mean(list(opportunities.values()))
    non_nan_values = [value for value in opportunities.values() if not isnan(value)]
    average_value = sum(non_nan_values) / len(non_nan_values)
    print("Average: ", average_value)

    # Order the dictionary by values in ascending order
    sorted_data = dict(sorted(opportunities.items(), key=lambda item: item[1]))
    if 'nan' in opportunities:
        del opportunities['nan']
    sorted_data = {key: value for key, value in sorted_data.items() if not isnan(value)}
    return average_value, sorted_data

# Get colors for the final histogram
def compute_interpolated_color(value, average, opportunities):
    # Normalize the value based on the range of data
    normalized_value = (value - min(opportunities.values())) / (max(opportunities.values()) - min(opportunities.values()))
    
    print("normalized: ", normalized_value)
    print("average: ", average)
    
    if value > average:
        # Interpolate between yellow (1, 1, 0) and green (0, 1, 0)
        red = max(0, min(1, 1 - normalized_value))
        green = 1
        blue = 0
    elif value < average:
        # Interpolate between yellow (1, 1, 0) and red (1, 0, 0)
        red = 1
        green = max(0, min(1, normalized_value))
        blue = 0
    else:
        # Return yellow color for values equal to average
        red, green, blue = (1, 1, 0)
    
    return (red, green, blue)

def plot_opportunity(opportunities, average, colors):
    fig, ax = plt.subplots(figsize=(15, 8))
    bar_positions = np.arange(len(opportunities))
    bars = ax.bar(bar_positions, opportunities.values(), width=0.5, color=colors, align='center')
    
    # Set x-ticks and labels
    ax.set_xticks(bar_positions)
    ax.set_xticklabels(opportunities.keys(), rotation=90)
    
    # s y-ticks
    ax.set_yticks([min(opportunities.values()), max(opportunities.values())])
    ax.set_yticklabels(["Low ", "High"])
    
    # Set title and labels
    ax.set_title('Colored Histogram of Opportunity scores')
    ax.set_xlabel('Genres')
    ax.set_ylabel('Score')
    
    # Display the plot
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":

    full_data_df = read_data()
    full_data_df = data_processing(full_data_df)
    
    owners_genre_data, number_genre_data = genre_data_aggregation(full_data_df, 2)

    genre = "Violent"
    
    # 730 days = 2 years
    dates = np.array(get_data_interval(730))
    dates = dates.reshape(len(dates), 1)

    # GET ALL MODELS, PREDICTIONS AND SLOPE LINES FOR ALL GENRES
    # Owner = owner count per period of time
    # Number = number of games per period of time
    owner_models, owner_predictions, owner_lines = perform_regression_analysis_on_data(owners_genre_data, dates)
    number_models, number_predictions, number_lines = perform_regression_analysis_on_data(number_genre_data, dates)
    
    opportunities = {}
    for x in owners_genre_data:
        opportunities[x] = get_opportunities(owner_models, number_models, x)
        
    # plot opportunities
    average_value, opportunities = opportunity_transfrom(opportunities)
    interpolated_colors = [compute_interpolated_color(value, average_value, opportunities) for value in opportunities.values()]
    plot_opportunity(opportunities, average_value, interpolated_colors)
    
    # return data to datetime for plots
    owners_genre_data[genre]["release_date"] = owners_genre_data[genre]["release_date"].apply(lambda x: dt.datetime.fromordinal(x))
    number_genre_data[genre]["release_date"] = number_genre_data[genre]["release_date"].apply(lambda x: dt.datetime.fromordinal(x))
    vectorized_fromordinal = np.vectorize(dt.datetime.fromordinal)
    dates = vectorized_fromordinal(dates)
    
    plot_genre_plot(owners_genre_data, genre, owner_models, owner_predictions, owner_lines, dates)
    plot_genre_plot(number_genre_data, genre, number_models, number_predictions, number_lines, dates)
    
    # GET POINT OF REFERENCE

    pass
