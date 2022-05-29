import shutil
import time

import keyring
import requests
import selenium.common.exceptions
import smartsheet
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def open_driver():
    """Open Selenium using the Chrome Driver."""
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()))


def open_smartsheet():
    """Initialize Smartsheets object."""
    access_token = keyring.get_password("rings_smartsheets", "api")
    smartsheet_client = smartsheet.Smartsheet(access_token)
    smartsheet_client.errors_as_exceptions(True)
    return smartsheet_client


def get_list_of_rows(smartsheet_client):
    """Return a list of Row objects from Smartsheets.

    Col 1 is the PIDs, Col 2 is the Image, and Col 3 is the Description.
    """
    sheet_id = "5040109000124292"
    return smartsheet_client.Sheets.get_sheet(sheet_id).rows[210:]


def get_links(driver, url: str, words: list, attribute: str):
    """Runs Selenium and returns a URL string.

    Args:
        words [list]: A list of words, from the Description field from Smartsheets, that is
        used to filter the list of anchor elements. This is very inefficient and can likely
        be improved.

        attribute [str]: HTML tag to filter on. Expect href or data-href
    """
    driver.get(url)
    while driver.title == "ERROR: The request could not be satisfied":
        print(driver.title)
        time.sleep(300)  # handle blocked requests
        driver.get(url)
    links = driver.find_elements(by=By.TAG_NAME, value="a")

    with open("output.html", "w") as f:
        f.write(driver.page_source)

    for link in links:
        try:
            link_url = link.get_attribute(attribute)
        except selenium.common.exceptions.StaleElementReferenceException:
            pass

        try:
            if all(i in link_url for i in words):
                if link_url.startswith("//"):  # handle '//image..'
                    link_url = "https:" + link_url
                return link_url
        except TypeError:
            pass
    return None


def get_image_url(driver, row) -> str:
    """Use Selenium to query for the ring.

    Uses the get_links() function to actually query. First time is for the search,
    which is expected to contain the appropriate URLs. Note that there is a marketing popup, but this
    does not seem to have an effect on the output.

    Second time is using the URL retrieved early to navigate to the product page and find the image.

    Returns image or None.
    """
    query_url = "https://www.brilliantearth.com/search/?q="

    pid = row.get_column(6452170849576836).value
    description = row.get_column(8703970663262084).value
    words = description.split("(")[0] + f" {pid}"  # remove inconsistent size notes

    ring_link = get_links(driver, query_url + pid, words.split(), "href")

    if ring_link:
        image_link = get_links(driver, ring_link, ["top", "image", pid], "data-href")
        return image_link

    return None


def download_image(image_url: str):
    """Cannot upload the image directly to Smartsheets, so this downloads the image first."""
    filename = "/Users/jdickman/Desktop/be_pics/" + image_url.split("/")[-1]
    r = requests.get(image_url, stream=True)

    if r.status_code == 200:
        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        r.raw.decode_content = True

        # Open a local file with wb ( write binary ) permission.
        with open(filename, "wb") as f:
            shutil.copyfileobj(r.raw, f)
    return filename


def upload_image(smartsheet_client, row_id: int, filename: str):
    """Upload image from the same directort that was used to store the image,
    and push to Smartsheets.
    """
    smartsheet_client.Cells.add_image_to_cell(
        5040109000124292,  # sheet id
        row_id,
        4200371035891588,  # column id
        filename,
        filename.split(".")[-1],
        alt_text=filename.split("/")[-1],
    )


def main():
    """Program to upload images of Brilliant Earth Rings given a list of PIDs/Descriptions.
    PIDs and Description fields are in Smartsheets, and the images are uploaded to the same
    sheet.

    Functions:
        - Initalize Selenium
        - Initialize Smartsheets
        - Use Smartsheets API to return list of rows with PIDs
            Manually sliced for where to begin
        - Pass the rows to Selenium:
            - Use the PID to search the website
            - Find product URL directly on this results page
            - Use this URL to navigate to the product
            - Find the appropriate image on this page
        - Save the image locally, using the requests library
        - Upload the image to the appropriate Smartsheets column/row
    """
    driver = open_driver()
    smartsheet_client = open_smartsheet()

    # Get list of rows and filter out rows with an image already uploaded
    rows_all = get_list_of_rows(smartsheet_client)
    rows = [row for row in rows_all if not row.get_column(4200371035891588).value]
    for row in rows:
        pid = row.get_column(6452170849576836).value
        image_url = get_image_url(driver, row)

        if image_url:
            filename = download_image(image_url)
            upload_image(smartsheet_client, row.id, filename)
            print(f"Uploaded image for {pid}.")

        else:
            print(f"No image found for {pid}.")

        time.sleep(3)
    driver.quit()


if __name__ == "__main__":
    main()
