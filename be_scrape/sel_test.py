import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import smartsheet


def test_eight_components():
    # path_to_driver = os.getcwd() + '/chromedriver'
    # driver = webdriver.Chrome(path_to_driver)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    driver.get("https://google.com")

    title = driver.title
    assert title == "Googles"

    driver.implicitly_wait(0.5)

    search_box = driver.find_element(by=By.NAME, value="q")
    search_button = driver.find_element(by=By.NAME, value="btnK")

    search_box.send_keys("Selenium")
    search_button.click()

    search_box = driver.find_element(by=By.NAME, value="q")
    value = search_box.get_attribute("value")
    assert value == "Selenium"

    driver.quit()


def test_be():

    pid = "BE26152"
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    URL = f"https://www.brilliantearth.com/search/?q={pid}"
    driver.get(URL)

    with open("sel_output.html", "w") as f:
        f.write(driver.page_source)

    links = driver.find_elements(by=By.TAG_NAME, value="a")

    words = ("6mm Aspen Wedding Ring").split()

    urls = []
    for link in links:
        link_url = link.get_attribute("href")
        try:
            if all(i in link_url for i in words):
                urls.append(link_url)
        except TypeError:
            pass

    print(urls)

    # new_url = urls[0]

    # driver.get(new_url)

    # # with open('sel_output.html', 'w') as f:
    # #     f.write(driver.page_source)

    # links = driver.find_elements(by=By.TAG_NAME, value='a')

    # words = ['top', 'image', 'BE241']

    # image_urls = []
    # for link in links:
    #     link_url = link.get_attribute('data-href')
    #     try:
    #         if all(i in link_url for i in words):
    #             image_urls.append(link_url)
    #         break
    #     except TypeError:
    #         pass

    # print(image_urls)

    driver.close()


def test_upload():
    smartsheet_client = open_smartsheet()
    smartsheet_client.Cells.add_image_to_cell(
        5040109000124292,
        4200371035891588,
        7462976634414980,
        # "https://image.brilliantearth.com/media/product_images/VZ/BE25W49_yellow_top.jpg",
        "/Users/jdickman/Desktop/be_pics/BE28615_white_top.jpeg",
        "jpeg",
    )


def sel_test():
    start_time = time.time()
    driver = open_driver()

    base_url = "https://www.brilliantearth.com/search/?q="

    for ring in rings:
        words = f"{ring[1]} White {ring[0]}"
        print(words)
        ring_link = get_links(driver, base_url + ring[0], words.split(), "href")

        if ring_link:
            image_link = get_links(
                driver, ring_link, ["top", "image", ring[0]], "data-href"
            )
        else:
            image_link = None

        print(ring[0])
        print("\tRing Link: ", ring_link)
        print("\tImage Link: ", image_link)

        time.sleep(2)

    driver.quit()
    print(time.time() - start_time)


def test_download():
    image_url = "https://image.brilliantearth.com/media/product_images/VZ/BE25W49_yellow_top.jpg"
    filename = "/Users/jdickman/Desktop/be_pics/" + image_url.split("/")[-1]

    r = requests.get(image_url, stream=True)

    # Check if the image was retrieved successfully
    if r.status_code == 200:
        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        r.raw.decode_content = True

        # Open a local file with wb ( write binary ) permission.
        with open(filename, "wb") as f:
            shutil.copyfileobj(r.raw, f)

        print("Image sucessfully Downloaded: ", filename)
    else:
        print("Image Couldn't be retreived")


def test_ss():
    access_token = "FF8W4twmkyxslTkWRqLabgnI0odHKPhUk5V7S"
    smartsheet_client = smartsheet.Smartsheet(access_token)
    smartsheet_client.errors_as_exceptions(True)

    # response = smartsheet_client.Sheets.list_sheets(
    #     include="attachments,source", include_all=True
    # )
    # sheets = response.data

    # for i in sheets:
    #     print(i)



    """
    columnId:
        1: 5507729016022916
        2: 1516703133788036
        3: 3255929202337668
    """

    # sheet_id = "5040109000124292"
    # sheet = smartsheet_client.Sheets.get_sheet(sheet_id)
    # a = sheet.rows[200]

    # print(dir(a))
    # print(a)
    # print(a.get_column(1516703133788036).value)

    # for row in sheet.rows:
    #     print(row)
    #     break

    # sheet_dict = {}
    # for counter, row in enumerate(sheet.rows):
    #     sheet_dict.update(
    #         {
    #             counter: row.id
    #         }
    #     )



if __name__ == "__main__":
    # test_eight_components()
    test_ss()



{
    "cells": [
        {"columnId": 5507729016022916, "displayValue": "BE201", "value": "BE201"},
        {
            "columnId": 1516703133788036,
            "displayValue": "https://image.brilliantearth.com/media/product_images/46/BE201_white_top.jpg",
            "formula": '=SYS_CELLIMAGE("https://image.brilliantearth.com/media/product_images/46/BE201_white_top.jpg","cXjtFca3gPeXUkiTUPzCLV",850,850,"BE201_white_top[1].jpg")',
            "image": {
                "altText": "https://image.brilliantearth.com/media/product_images/46/BE201_white_top.jpg",
                "height": 850,
                "id": "cXjtFca3gPeXUkiTUPzCLV",
                "imageId": "cXjtFca3gPeXUkiTUPzCLV",
                "width": 850,
            },
            "value": "https://image.brilliantearth.com/media/product_images/46/BE201_white_top.jpg",
        },
        {
            "columnId": 3255929202337668,
            "displayValue": "2mm Comfort Fit Wedding Ring",
            "value": "2mm Comfort Fit Wedding Ring",
        },
        {"columnId": 7759528829708164, "displayValue": "Active", "value": "Active"},
        {"columnId": 2130029295495044, "value": "2008-01-01"},
        {"columnId": 6633628922865540, "displayValue": "Complete", "value": "Complete"},
        {
            "columnId": 4381829109180292,
            "displayValue": "Uploaded to Web",
            "value": "Uploaded to Web",
        },
        {"columnId": 8885428736550788, "displayValue": "Yes", "value": "Yes"},
        {"columnId": 89335714342788, "displayValue": "Unisex", "value": "Unisex"},
        {"columnId": 4592935341713284, "displayValue": "None", "value": "None"},
        {
            "columnId": 2341135528028036,
            "displayValue": "High polish",
            "value": "High polish",
        },
        {"columnId": 6844735155398532},
    ],
    "createdAt": "2022-05-28T02:43:18+00:00Z",
    "expanded": true,
    "id": 27881707333508,
    "modifiedAt": "2022-05-28T02:54:56+00:00Z",
    "rowNumber": 1,
}

{
    "cells": [
        {"columnId": 6452170849576836, "displayValue": "BE28615", "value": "BE28615"},
        {"columnId": 4200371035891588},
        {
            "columnId": 8703970663262084,
            "displayValue": "Zephyr Wedding Ring",
            "value": "Zephyr Wedding Ring",
        },
        {"columnId": 541196338653060, "displayValue": "Active", "value": "Active"},
        {"columnId": 5044795966023556, "value": "2022-02-18"},
        {"columnId": 2792996152338308},
        {"columnId": 7296595779708804},
        {"columnId": 1667096245495684, "displayValue": "No", "value": "No"},
        {"columnId": 6170695872866180, "displayValue": "Male", "value": "Male"},
        {"columnId": 3918896059180932, "displayValue": "None", "value": "None"},
        {
            "columnId": 8422495686551428,
            "displayValue": "High polish",
            "value": "High polish",
        },
        {"columnId": 1104146292074372},
        {"columnId": 3448137578768260},
        {"columnId": 5699937392453508},
        {"columnId": 1196337765083012},
        {"columnId": 6825837299296132},
        {"columnId": 2322237671925636},
        {"columnId": 7388787252717444},
        {"columnId": 2885187625346948},
        {"columnId": 5136987439032196},
        {"columnId": 633387811661700},
        {"columnId": 7951737206138756},
    ],
    "createdAt": "2022-05-28T22:05:13+00:00Z",
    "expanded": true,
    "id": 2959377007044484,
    "modifiedAt": "2022-05-28T22:15:03+00:00Z",
    "rowNumber": 159,
    "siblingId": 5211176820729732,
}
