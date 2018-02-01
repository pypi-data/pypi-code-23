from bs4 import BeautifulSoup
import requests
import re
import time
import json


def scrape_single_advertisement(url=None, content=None):
    """
    Scrapes single web page based on url

    :param content: content to scrape
    :param url: url to scrape
    :return: {} or dictionary with elements "title", "expiration_date", "city", "company_name", "salary", "watched",
    "candidates", "responsibilities_text", "qualifications_text", "benefits_text", "salary_text", "company_description"
    """

    if url:
        response = requests.get(url)

        if response.status_code != 200:
            return {}

        content = response.content

    data = dict.fromkeys(["title", "expiration_date", "city", "company_name", "salary", "watched",
                          "candidates", "responsibilities_text", "qualifications_text", "benefits_text",
                          "salary_text", "company_description"],
                         None)

    soup = BeautifulSoup(content, "html.parser")

    data["title"] = soup.find("h1", {"class": "heading1",
                                     "id": "jobad_heading1"}
                              ).get_text()

    data["city"] = soup.find("div", {"id": "jobad_location"}).a.text

    salary_element = soup.find("strong", {"class": "salary_emphasised"})
    if salary_element:
        data["salary"] = salary_element.text

    stats_elements = soup.find_all("strong", {"class": "jobad_stat_value"})

    for idx, value in enumerate(stats_elements):
        if idx == 0:
            data["watched"] = stats_elements[idx].text
        elif idx == 1:
            data["candidates"] = stats_elements[idx].text

    for element in ["responsibilities", "qualifications", "benefits"]:
        tmp_element = soup.find("div", {"class": "jobad_txt",
                                        "itemprop": element})
        if tmp_element:
            data[element + "_text"] = tmp_element.text

    jobadd_elements = soup.find_all("div", {"class": "jobad_txt"})

    for element in jobadd_elements:
        if "itemprop" not in element.attrs:
            data["salary_text"] = element.text
            break

    data["company_description"] = soup.find("div", {"id": "jobad_company_description"}).text
    data["companay_name"] = soup.find("h2", {"id": "jobad_company_title"}).text

    data["expiration_date"] = soup.find("div", {"id": "jobad_expiration"}).attrs["title"]

    data = {key: None if not value else re.sub(" +", " ", value.replace("\r\n", " ").replace("\n\n", " ").replace("\n", " ").strip())
            for key, value in data.items()}

    data["url"] = url

    return data


def scrape_multiple_advertisements(url=None, content=None, timeout=1, verbose=False):
    """
    Scrapes multiple web pages based on url

    :param url: url to scrape
    :param content: content to scrape
    :param timeout: time out between requests, default=1
    :param verbose: show extended information, default=False
    :return: list with advertisement dictiotary
    """

    data = []

    if url:
        response = requests.get(url)

        if response.status_code != 200:
            return {}

        content = response.content

    soup = BeautifulSoup(content, "html.parser")

    advertisements = soup.find_all("article")

    for advertisement in advertisements:
        if verbose:
            print(advertisement.a.attrs["href"])

        data.append(scrape_single_advertisement(advertisement.a.attrs["href"]))

        time.sleep(timeout)

    return data


def next_url_exists(url):
    """
    Checks if url contains next page to scrape url

    :param url: url to check for next url to scrape
    :return: None or next url
    """
    response = requests.get(url)

    if response.status_code != 200:
        return None

    content = response.content

    soup = BeautifulSoup(content, "html.parser")

    navigation = soup.find("ul", {"class": "pages_ul mt30 mb30"})
    navigations = navigation.find_all("li")
    next_page_element = navigations[-1].find("a", {"class": "prev_next"})

    if next_page_element:
        return next_page_element.attrs["href"]

    return None


def scrape_multiple_pages(url, timeout=1, file_path=None, verbose=False):
    """
    Iterate and scrape all next pages

    :param file_path: json file path to export scraped data
    :param verbose: show extended information, default=False
    :param url: url of first page to scrape
    :param timeout: time out between requests, default=1
    :return: list with advertisement dictiotary
    """

    data = []
    data.extend(scrape_multiple_advertisements(url=url,
                                               timeout=timeout,
                                               verbose=verbose))

    next_url = next_url_exists(url)
    while next_url:
        data.extend(scrape_multiple_advertisements(url=next_url,
                                                   timeout=timeout,
                                                   verbose=verbose))
        next_url = next_url_exists(next_url)

    if file_path:
        with open(file_path, "w", encoding="utf8") as file_obj:
            json.dump(data, file_obj, ensure_ascii=False, indent=4)
    else:
        print(json.dumps(data, indent=4))