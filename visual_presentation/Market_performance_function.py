from typing import Sequence, Optional, Any
import pandas as pd
import plotly.express as px

from dash_plot_generation.utils import get_owner_means, convert_owners_to_limits, split_companies


# The function to plot the bubble chart of market performance

def plot_market_performance(df, company_type: str, game_number_max: int, game_number_min: int, **layout_arguments):
    
    """
    This function creates a bubble chart of market performance.
    The variable company_type could only be developer or publisher.
    The bubble size is game number, which is filtered by the range [game_number_min, game_number_max].
    """

    df["owner_means"] = df["owners"].apply(lambda x: get_owner_means(convert_owners_to_limits(x)))

    # Calulate the revenue
    df["revenue"] = df["owner_means"]*df["price"]

    # Split the companies
    df["company_split"] = df[company_type].apply(lambda x: split_companies(x))
    df_split = df.assign(developer=df['company_split'].str.split(', ')).explode('company_split')

    # Calculate revenue and game number
    company_stats = df_split.groupby('company_split').agg(revenue=('revenue', 'sum'), game_number=('company_split', 'count'), owner_number=('owner_means', 'sum')).reset_index()

    # Filter the Game number
    filter_company_stats = company_stats[(company_stats['game_number'] >= game_number_min) & (company_stats['game_number'] <= game_number_max)]

    # Bubble chart
    fig = px.scatter(filter_company_stats, x='revenue', y='owner_number', size='game_number', log_y=True, log_x=True,size_max = 40,
                 hover_name='company_split', title=f'Market Performance of {company_type}')
    fig.update_layout(**layout_arguments)
    return fig



if __name__ == "__main__":
    # Read data and calulate owner means
    df = pd.read_csv("full_game_data.csv")
    game_number_min = 1
    game_number_max = 10
    fig = plot_market_performance(df, 'developer', game_number_max, game_number_min)
    fig.show()










