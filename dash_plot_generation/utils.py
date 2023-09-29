import math
from typing import List, Sequence, Optional

import numpy
import pandas

DEFAULT_ILLEGAL_CONTINUATIONS = {"INC.", "LLC", "CO.", "LTD.", "S.R.O."}


def split_developers(arr, illegal_continuations: Optional[Sequence[str]] = None):
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
                    results_list.append(arr[start_index:index])
                    start_index = index + 1
        elif index == len(arr) - 1:
            results_list.append(arr[start_index:index + 1])

    return results_list
