import itertools

import requests
import json
import pandas
import time
import matplotlib.pyplot as plt
from pandas.core.dtypes.common import is_numeric_dtype

sisu = "https://steamspy.com/api.php?request=all&page="


# There are 67 pages of data but for the heck of it,
# we're going try to load 100 pages
def get_all_data(iterations: int = 100):
    for i in range(iterations):
        print(i)
        url = sisu + str(i)
        try:
            response = json.loads(requests.get(url).text)
        except Exception as some_shit:
            print(some_shit)
            break
        games = [value for (key, value) in response.items()]
        if i == 0:
            df = pandas.DataFrame(games)
        else:
            df_comb = pandas.DataFrame(games)
            df = pandas.concat([df, df_comb], ignore_index=True, sort=False)
        time.sleep(0)
    return df


def add_user_rating(df):
    def user_rating_function(pos, neg):
        if pos == neg == 0:
            return 0
        return pos / (pos + neg)

    df["Review_rating"] = df.apply(lambda row: user_rating_function(row.positive, row.negative), axis=1)
    return df


def create_hist_plots(df):
    for col_name in df.columns:
        if is_numeric_dtype(df[col_name]):
            fig = plt.figure()
            plt.hist(df[col_name], log=True)
            title = " ".join([col_name, "log histogram"])
            plt.title(title)
            fig.savefig("".join(["images\\",title,".png"]))
            plt.show()


def replace_owner_number_with_symbol(df):
    def owner_strip(user_range: str):
        user_range = user_range.replace(",000,000", " M")
        user_range = user_range.replace(",000", " k")
        return user_range

    df["owners"] = df["owners"].apply(lambda name: owner_strip((name)))
    return df


def create_heat_maps(df, plot_pairs):
    for (x, y) in plot_pairs:
        plt.figure()  # Create a new figure for each heatmap
        heatmap = plt.imshow(df[[x, y]].values, cmap='hot', interpolation='nearest', aspect='auto')
        plt.colorbar(heatmap)  # Add a colorbar
        plt.xlabel(x)
        plt.ylabel(y)
        plt.title(f"Heatmap of {x} vs {y}")
        plt.show()


def price_to_dollars(convert_df):
    convert_df["price"] = convert_df["price"].apply(lambda val: int(val)/100 if int(val) != 0 else 0)
    return convert_df


if __name__ == "__main__":
    df = get_all_data(5)
    df = add_user_rating(df)
    df = replace_owner_number_with_symbol(df)
    df = price_to_dollars(df)

    h = df.describe()
    j = df.isna().sum()
    c = df["userscore"].value_counts()

    numeric_cols = [col for col in df.columns if is_numeric_dtype(df[col])]
    plot_pairs = list(itertools.combinations(numeric_cols, 2))
    print(df.columns)
    print("price", df["price"].unique())
    print("discount", df["discount"].unique())
    print("owners", df["owners"].unique())
    create_hist_plots(df)
    plt.hist(df["owners"], log=True)
    plt.xticks(rotation='vertical')
    plt.title("Histogram of game playerbase sizes with log scale")
    plt.tight_layout()
    plt.show()
    df.to_csv("game_data.csv")
    pass
