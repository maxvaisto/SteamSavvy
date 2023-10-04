# Introduction to Data Science, Luento-opetus, 2023
# Sergei Panarin


# Data preprocessing

# IMPORTANT THINGS:
# Change the number of input files in the read_data function OR later replace with full data file
# FUNCTION replace owner with symbol is copied from the main branch, DELETE LATER and IMPORT

# Reading the data from source:
# Pandas cannot read from GitLab URLs, so work is done with locally stored datasets.
# Go through partial files containing parts of the whole dataset
# @param  
# @return: full pandas dataframe, containing all the relevant columns from the csv files
def read_data():
    # full_data_df = pd.read_csv("full_data.csv")

    partial_dfs = []

    # range can be changed, reads segments of the full dataset
    for index in range(10):
        datafile="file_segments/game_data_"+str(index+1)+".csv"
        partial_dfs.append(pd.read_csv(datafile))
    
    # Combine partial dataframes into the full version
    full_data_df = pd.concat(partial_dfs)

    return full_data_df

# transform String columns into integer IDs.
# @param: pandas dataframe with the full data
# @return: pandas dataframe with developer, publisher, genres columns encoded with integer IDs
def label_encoding(data):
    to_be_encoded = ["publisher", "developer", "genres"]

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
# @return: pandas dataframe with genre, # of purchases, time interval columns

def genre_data_aggregation(data, interval):
    # preprocess the release date column into the pandas datetime format
    data['release_date'] = pd.to_datetime(data['release_date'], dayfirst=True, format="mixed")

    # remove excessive columns and sort values
    data = data[['release_date', 'genres', 'owners']].sort_values(['release_date','genres', 'owners'], ascending=[True, True, False])

    # group by the time interval and get sum of the owners
    data = data.groupby( [pd.Grouper(key='release_date', freq=str(interval)+"M"), pd.Grouper('genres')] ).agg({'owners': 'sum'})
    return data

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


if __name__ == "__main__":

    import pandas as pd
    import numpy as np
    import datetime as dt
    import re

    full_data_df = read_data()
    full_data_df = clean_index(full_data_df)

    label_encoding(full_data_df)

    data = replace_owner_str_with_average_number(full_data_df)

    genre_data = genre_data_aggregation(full_data_df, 2)

    
    pass

