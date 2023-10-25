# Annual released game number (by selecting publisher/developer)
import os

import pandas
import pandas as pd
import re
import plotly.express as px
import plotly.graph_objs

from dash_plot_generation.data_store import FULL_DATA


# Extract the year
def get_game_release_figure(df: pd.DataFrame, company_name: str, show_column: str = "developer", **layout_arguments):
    def extract_year(row):
        match = re.search(r'\d{4}', str(row))
        if match:
            return match.group()
        return None

    def add_missing_years(df):
        df_copy = df.copy()

        df_copy['year'] = pd.to_numeric(df_copy['year'])

        # Get all years
        all_years = list(range(int(df_copy['year'].min()), 2024))

        # Create dud df
        all_years_df = pd.DataFrame({show_column: company_name, 'year': all_years, 'game_number': 0})

        # Join dfs
        result_df = pd.concat([df_copy, all_years_df], ignore_index=True)

        # Sort
        result_df.sort_values('year', inplace=True)

        # Convert back to str
        result_df["year"] = result_df["year"].map(str)

        return result_df

    copy_df = df[["release_date", show_column]]
    copy_df['year'] = copy_df['release_date'].apply(extract_year)
    copy_df['year'].replace('', None, inplace=True)

    company_games = copy_df[copy_df[show_column] == company_name]
    games_grouped_by_year = company_games.groupby([show_column, 'year']).size().reset_index(name='game_number')
    try:

        games_grouped_by_year_full = add_missing_years(games_grouped_by_year)

        if show_column == "publisher":
            title = f'Games Published by Year - {company_name}'
        elif show_column == "developer":
            title = f'Games Developer by Year - {company_name}'
        else:
            raise KeyError(f"Invalid column argument: {show_column}")

        fig = px.bar(games_grouped_by_year_full, x='year', y='game_number',
                     title=title,
                     labels={'year': 'Year', 'game_number': 'Game Number'})
    except Exception as ex:
        fig = plotly.graph_objs.Figure()

    fig.update_layout(showlegend=False)
    fig.update_layout(**layout_arguments)
    return fig


if __name__ == "__main__":
    fig = get_game_release_figure(FULL_DATA, "Valve", "developer")
    fig.show()
