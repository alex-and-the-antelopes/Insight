"""
Alex Dawkins (alexander.dawkins@gmail.com) 2021

Hello & welcome to the shit-show
"""

from urllib.request import urlopen
import pandas as pd
from bs4 import BeautifulSoup
import parlpy.bills.bill_list_fetcher as blf


def get_summary(detail_path: str) -> str:
    """
    Returns the scraped summary at the given path.
    :param detail_path: URL to scrape from
    :return: String containing the summary
    """

    # Just a wrapper to the private fetch_summary function
    return __fetch_summary(detail_path)


def append_summary(series: pd.Series) -> pd.Series:
    """
    Appends summary to the Series
    :param series: Row to append summary to
    :return: Series with summary appended
    """
    # Get path from row
    path = series['bill_detail_path']

    # Fetch summary
    summary = __fetch_summary(path)

    # Label summary
    summary_col = pd.Series(summary, ['bill_summary'])

    # Append Summary to row
    series = series.append(summary_col)

    # Return row with summary appended
    return series


def append_summaries(overview: blf.BillsOverview) -> pd.DataFrame:
    """
    Fetches and appends summaries to all rows stored in the BillsOverview object
    :param overview: BillsOverview object to add summaries to
    :return: Dataframe from BillsOverview with summaries appended
    """
    # Get all bills from BillsOverview
    df = overview.bills_overview_data

    # Generate new df with summaries from current df
    summaries = df.apply(lambda row: __fetch_summary(row['bill_detail_path']), axis=1)

    # Append to current df
    df['bill_summary'] = summaries

    return df


def __fetch_summary(detail_path: str, base_url="https://bills.parliament.uk/") -> str:
    """
    Scrapes the summary from the given page.
    :param detail_path: Path to details page
    :param base_url: URL of government website
    :return: String containing the summary text
    """

    # Build URL to scrape from
    url = base_url + detail_path

    # Get HTML from URL
    html_data = urlopen(url)
    data_bs = BeautifulSoup(html_data.read(), 'html.parser')

    # Get <div> from HTML
    summary_element = data_bs.find(class_="block block-page").find(class_="text-break")

    # Get text from <div>, and remove the leading TAB
    if summary_element is not None:
        summary_text = summary_element.text.strip()
    # if no summary could be found, use empty string
    else:
        summary_text = ""

    return summary_text
