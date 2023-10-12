import math
import re
from typing import Sequence, Optional, Any
import pandas

DEFAULT_ILLEGAL_CONTINUATIONS = {"INC.", "LLC", "CO.", "LTD.", "S.R.O."}


def get_owner_means(owner_limits: Sequence[Any]):
    if not isinstance(owner_limits, list):
        return owner_limits
    else:
        return (owner_limits[0] + owner_limits[1]) / 2


def convert_owners_to_limits(owner_limit):
    if not isinstance(owner_limit, str):
        return owner_limit
    owners_raw = [rev.replace(" ", "") for rev in owner_limit.split(" .. ")]
    owners_clean = []
    for owner_limit in owners_raw:
        owner_limit = owner_limit.replace("M", "0" * 6)
        owner_limit = owner_limit.replace("k", "0" * 3)
        owners_clean.append(int(owner_limit))
    return owners_clean


def split_companies(arr, illegal_continuations: Optional[Sequence[str]] = None):
    """
    Splits the given string at comma sign as long as following the comma none of the illegal
    continuations happen. In such a case, the string split does not happen that said comma.
    :param arr: Array containing the developers/publishers for a single game
    :param illegal_continuations: A list of illegal continuations. Must be uppercase.
    :return: Returns the given split input string as a list.
    :note: If the arr is numpy.NaN, this value is returned instead of a list.
    """
    if illegal_continuations is None:
        illegal_continuations = DEFAULT_ILLEGAL_CONTINUATIONS
    if pandas.isna(arr):
        return arr

    results_list = []
    start_index = 0
    split_char = ", "

    for index in range(len(arr)):
        if index < len(arr) - 1:
            txt = arr[index:index + 2]
            if txt == split_char:
                found_illegal = False
                min_continuation = min([len(continuation) for continuation in illegal_continuations])
                max_continuation = max([len(continuation) for continuation in illegal_continuations])
                next_chars = arr[index + min_continuation:index + min_continuation + max_continuation]
                for i in range(index + min_continuation, index + len(next_chars) + 2):
                    comp_txt = arr[index + 2:i + 2].upper()
                    if comp_txt in illegal_continuations:
                        found_illegal = True
                        break
                if not found_illegal:
                    results_list.append(arr[start_index:index].strip())
                    start_index = index + 1
        elif index == len(arr) - 1:
            results_list.append(arr[start_index:index + 1].strip())

    return results_list


def extract_unique_companies(nested_companies):
    full_company_list = [dev for company_list in nested_companies
                         if isinstance(company_list, list) for dev in company_list]
    unique_companies = []
    for company in full_company_list:
        if company not in unique_companies:
            unique_companies.append(company)
    return unique_companies


def replace_owner_number_with_symbol(df):
    def owner_strip(user_range: str):
        if isinstance(user_range, str):
            user_range = user_range.replace(",000,000", " M")
            user_range = user_range.replace(",000", " k")
        return user_range

    df["owners"] = df["owners"].apply(lambda name: owner_strip((name)))
    return df


def replace_owner_number_with_symbol_real_numeric(value):
    value_str = str(value)
    value_str = re.sub("0" * 9 + "$", " billion", value_str)
    value_str = re.sub("0" * 6 + "$", " million", value_str)
    # value_str = re.sub("0" * 3 + "$", " thousand", value_str)
    return value_str


def update_dots(n):
    num_dots = (n % 10) + 1
    dots = "." * num_dots
    return [dots]


def convert_to_numeric_str(value, **kwargs):
    return replace_owner_number_with_symbol_real_numeric(round_to_three_largest_digits(value, **kwargs))


def label_with_rev(label, rev, space, char=".", currency_symbol=""):
    processed_rev = convert_to_numeric_str(int(rev))
    return_val = label_with_text(label, "".join([currency_symbol, processed_rev]), space, char)
    return return_val


def label_with_text(first_str, second_str, space, char="."):
    white_space_filler = char * (space - (len(first_str) + len(second_str)) - 2)
    return_val = " ".join([first_str, white_space_filler, second_str])
    return return_val


def round_to_three_largest_digits(number, accuracy=2):
    round_val = -(len(str(round(number))) - accuracy)
    return_val = round(round(number), min(round_val, 0))
    return return_val
