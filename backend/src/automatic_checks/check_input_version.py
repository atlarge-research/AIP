import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from django.db import connection


# from pyppeteer import launch
# import asyncio

dblp_url = "https://dblp.uni-trier.de/xml/"
aminer_and_mag_url = "https://www.aminer.org/open-academic-graph"
semantic_scholar_url = \
    "http://s2-public-api.prod.s2.allenai.org/corpus/download/"


def extract_dblp_date(url=dblp_url):
    reqs = requests.get(url)
    soup = BeautifulSoup(reqs.text, "html.parser")

    for tr in soup.find_all("tr"):
        f = tr.find("a")
        if f is not None:
            if f.get("href") == "dblp.xml.gz":
                date = re.search(r"(\d{4}(-)\d{2}(-)\d{2})", tr.text)
                date_string = date.group()
                date_version = datetime.strptime(
                    date_string,
                    "%Y-%m-%d",
                ).date()
                print("DBLP date of latest version:", date_version)
                return date_version


def extract_semantic_scholar_date(url=semantic_scholar_url):
    reqs = requests.get(url)
    soup = BeautifulSoup(reqs.text, "html.parser")

    text1 = soup.find("h2", text="Most Recent Release")

    # Sometimes throws a timeout error..
    text2 = text1.find_next_sibling("table")

    date_string = text2.find("b").text
    date_version = datetime.strptime(date_string, "%Y-%m-%d").date()
    print("Semantic Scholar date of latest version:", date_version)
    return date_version

    # Unfortunately does not work when running through Docker,
    # has something to do with opening other processes and
    # singles working only in the main thread
# async def extract_aminer_and_mag_date(url=aminer_and_mag_url):
#     # Code from:
#     # https://scrapingant.com/blog/scrape-dynamic-website-with-python
#
#     # Launch the browser
#     browser = await launch(executablePath='/usr/bin/google-chrome-stable')
#     # Open a new browser page
#     page = await browser.newPage()
#     # Create a URI for our test file
#     page_path = url
#     # Open our test file in the opened page
#     await page.goto(page_path)
#     page_content = await page.content()
#     # Process extracted content with BeautifulSoup
#     soup = BeautifulSoup(page_content, 'html.parser')
#
#     # Sometimes throws an
#     # "AttributeError: 'NoneType' object has no attribute 'find_next'",
#     # probably something to do with timeouts as well
#     text1 = soup.find(id="#content0").find_next()
#     text1 = text1.find_next_sibling('p')
#     date_string = None
#     while text1 is not None:
#         date = re.search(r'([a-zA-Z]{3}( )\d{4})', text1.text)
#         if date is not None:
#             date_string = date.group()
#         text1 = text1.find_next_sibling('p')
#
#     if date_string is None:
#         raise LookupError(
#             "No date was extracted from the Aminer/MAG website")
#
#     date_version = datetime.strptime(date_string, '%b %Y').date()
#
#     print("Aminer/MAG date of latest version:", date_version)
#
#     # Close browser
#     await browser.close()
#     return date_version


def is_fresh(new_version, source_name):
    with connection.cursor() as cursor:
        if source_name == "DBLP":
            q = "SELECT dblp_version FROM properties;"
        elif source_name == "Aminer/MAG":
            q = "SELECT aminer_mag_version FROM properties;"
        elif source_name == "Semantic Scholar":
            q = "SELECT semantic_scholar_version FROM properties;"
        else:
            raise LookupError("No such source exists, check the name")
        cursor.execute(q)
        curr_version = cursor.fetchone()
        if curr_version is None:
            return False
        else:
            return curr_version[0] >= new_version


def check_if_fresh(data_source, date_version):
    fresh = is_fresh(new_version=date_version, source_name=data_source)
    if fresh:
        return "Current version of " + data_source + " is up to date"
    else:
        return "A new version of " + data_source + " is available"


def check_all():
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # To get dynamic websites to work try this:
    # https://github.com/miyakogi/pyppeteer/issues/14
    input_names = [
        ("DBLP", extract_dblp_date()),
        # ("Aminer/MAG", loop.run_until_complete(
        #     extract_aminer_and_mag_date())),
        ("Semantic Scholar", extract_semantic_scholar_date()),
    ]
    # loop.stop()
    res = []
    for source in input_names:
        res.append(
            check_if_fresh(
                data_source=source[0],
                date_version=source[1],
            ),
        )
    return res
