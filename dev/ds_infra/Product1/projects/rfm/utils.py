import pandas as pd
import numpy as np

import ds_infra.api.rest.common.utils as utils
import logging


def read_from_db(sql, con, columns):
    """
    Runs a DML SQL query for a given sql, connection object, and columns, using cx_Oracle, and
    stores output in a Pandas dataframe.

    Parameters
    ----------
        sql (str) : SELECT statement used to query to the database
        con (cx_oracle.Connection) : connection object created by db.py (ds_infra framework output)
        columns (list of str) : column names supplied to the pandas DataFrame columns attribute.

    Returns
    -------
        df (pandas.DataFrame) : SQL result set in Pandas Dataframe object format.
    """
    cur = con.cursor()

    cur.execute(sql)
    rows = cur.fetchall()

    if len(rows) > 0:
        df = pd.DataFrame(rows, columns=columns)
    else:
        df = pd.DataFrame(columns=columns)
    return df


def write_to_db(sql, con, df):
    """
    Writes pandas dataframe into the table specified by the sql query.

    Parameters
    ----------
        sql (str) : SELECT statement used to query to the database
        con (cx_oracle.Connection) : connection object created by db.py (ds_infra framework output)
        df (pandas.DataFrame) : pandas DataFrame table to write to database.
    Returns
    -------
        No return
    """
    cur = con.cursor()
    df_array = df.values.tolist()
    cur.executemany(sql, df_array)
    con.commit()


def local_global_mean(beh_data, local_window_length=3):
    """
    Compute local global average matrix for all recipients across time.

    The local-global average, or LGM, is a metric that is used to detect the
    rate of change of a behavioral event of a recipient in time.

    We define the LGM at time t as the ratio:

    LGM(t) = local_mean(t)/global_mean(t), where

    - local_mean(t) = mean from t - w, ..., t (w = window). Typically we choose w = 3 as a configurable.
    - global_mean(t) = mean from start, 1,..., t

    The LGM at time t then describes the ratio of relatively new behavior to long-running behavior
    as a changepoint detection metric.

    Example: find the open rate LGM of recipient 123 at week t=5, whose  weekly open rates are

    t = 1  2    3     4   5
    [0.0, 0.0, 0.1, 0.2, 0.3]

    with window w = 3. Then

    local_mean(t= 5) = (0.1 + 0.2 + 0.3)/3 = 0.2
    global_mean(t= 5) = (0.0 + 0.0 + 0.1 + 0.2 + 0.3)/5 = 0.12

    lgm(t= 5) = 0.2 / 0.12 = 1.666. Since lgm > 1, then the engagement of recipient 123 increased.

    Below, we repeat the example for calculating the LGM for every time t.

    Parameters
    ----------
        beh_data (pandas.DataFrame or pandas.Series) : dataframe composing of indexes as RIIDs,
            columns as weekly behavioral counts (or rates) (see example).

        local_window_length (int) : determines how large of a window we want for computing the local mean.
    Returns
    -------
        lgm_matrix (pandas.DataFrame) : LGM matrix for all recipients, for each time point.
    """
    # if input is Series call recipient_local_global_mean method
    if isinstance(beh_data, pd.Series):
        return recipient_local_global_mean(beh_data, local_window_length=local_window_length)
    else:

        local_mean_matrix = beh_data.rolling(window=local_window_length, min_periods=1, axis=1).mean()
        global_mean_matrix = beh_data.expanding(min_periods=1, axis=1).mean()

        # temporarily zeros with 1 so when local mean and global mean matrices are divided, zero division error is avoided
        global_mean_matrix_masked = global_mean_matrix.mask(cond=(global_mean_matrix == 0), other=1)

        # the quotient of local and global mean matrices represent the LGM matrix (local-global mean matrix)
        lgm_matrix = (local_mean_matrix / global_mean_matrix_masked)

        # Fill first window values with the running mean of the first window.
        # Without those, values at columns (lgm day 1, ..., lgm day local_window_length) will be NaN
        lgm_matrix.iloc[:, :local_window_length] = global_mean_matrix.iloc[:, :local_window_length]

        # since we temporarily masked global mean zeros with -1, we will reset those back to zero
        lgm_matrix = lgm_matrix.mask(cond=(global_mean_matrix == 0), other=0)

        # since pandas.rolling does not skipna, we will mask also any index that originally had NaN to be NaN again
        lgm_matrix[beh_data.isnull()] = np.nan

        # # if input is Series, then convert output to Series
        # if isinstance(beh_data, pd.Series):
        #     lgm_matrix = pd.Series(lgm_matrix.values[0])

        return lgm_matrix


def recipient_local_global_mean(beh_data, local_window_length=3):
    """
    Compute local global average matrix for a single recipient.

    Parameters
    ----------
        beh_data (pandas.Series) : Series composing of indexes as RIIDs,
            columns as weekly behavioral counts (or rates) (see example).

        local_window_length (int) : determines how large of a window we want for computing the local mean.

    Returns
    -------
        lgm_series (pandas.Series) : LGM matrix for all recipients, for each time point.
    """
    local_mean_series = beh_data.rolling(window=local_window_length, min_periods=1).mean()
    global_mean_series = beh_data.expanding(min_periods=1).mean()

    # temporarily zeros with 1 so when local mean and global mean matrices are divided, zero division error is avoided
    global_mean_series_masked = global_mean_series.mask(cond=(global_mean_series == 0), other=1)

    # the quotient of local and global mean matrices represent the LGM matrix (local-global mean matrix)
    lgm_series = (local_mean_series / global_mean_series_masked)

    # Fill first window values with the running mean of the first window.
    # Without those, values at columns (lgm day 1, ..., lgm day local_window_length) will be NaN
    lgm_series[:local_window_length] = global_mean_series[:local_window_length]

    # since we temporarily masked global mean zeros with -1, we will reset those back to zero
    lgm_series = lgm_series.mask(cond=(global_mean_series == 0), other=0)

    # since pandas.rolling does not skipna, we will mask also any index that originally had NaN to be NaN again
    lgm_series[beh_data.isnull()] = np.nan

    return lgm_series


def set_resampled_matrix(event_frequency_matrix, bin_size):
    """
    Aggregates frequency matrix of a particular event in the aggregation level specified.

    Parameters
    ----------
      event_frequency_matrix (pandas.DataFrame) : dataframe with (ideally) daily counts for each recipient for the given event
      bin_size (int) : denotes the size of the bin we will aggregate with

    Returns
    -------
      agg_matrix (pandas.DataFrame) : aggregated dataframe

    """
    idx = event_frequency_matrix.T.index.astype(int)
    agg_matrix = event_frequency_matrix.T.groupby(idx // bin_size).sum().T
    return agg_matrix


def set_rate_matrix(send_count_matrix, response_count_matrix):
    """
    Creates a rate matrix (= response counts / send counts). 

    Example: open rate matrix is a matrix with each column being the open rates of one week (or day or month, depending on cadence)

    RIID | LIST_ID | Week 1 | Week 2 | ... | Week 24

    123 | 1 | 0.2 | 0.0 | ... | 0.4 
    ...
    345 | 1 | 0.0 | 0.3 | ... | 0.2


    Parameters
    ---------
      send_count_matrix (pandas.DataFrame) : matrix of send counts
      response_count_matrix (pandas.DataFrame) : matrix of open counts
    Returns
    -------
      rate_matrix (pandas.DataFrame) : matrix of open rates across time and across recipients
    """

    rate_matrix = (response_count_matrix / send_count_matrix)

    rate_matrix[send_count_matrix == 0] = np.nan

    if (np.sum(send_count_matrix.index != response_count_matrix.index) == 0):  # if RIIDs in each matrix are the same
        rate_matrix[send_count_matrix == 0] = np.nan
    else:
        log('RIIDs in OR matrix are not equal to RIIDs in send matrix, so original OR matrix is returned.')
    return rate_matrix


def log(msg):
    return utils.log(msg=msg, level=logging.INFO)
