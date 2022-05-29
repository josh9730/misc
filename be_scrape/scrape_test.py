import requests
from bs4 import BeautifulSoup

# URL = "https://www.brilliantearth.com/Luxe-Ballad-Diamond-Ring-(1/4-ct.-tw.)-Platinum-BE264/"
# URL = "https://www.brilliantearth.com/Delicate-Antique-Scroll-Diamond-Ring-(1/15-ct.-tw.)-White-Gold-BE241/"
URL = "https://www.brilliantearth.com/search/?q=BE241"
page = requests.get(URL)

# print(page.text)

soup = BeautifulSoup(page.content, "html.parser")
# print(soup.prettify)

with open("output_query.html", "w") as f:
    f.write(str(soup.prettify))

# results = soup.find_all(type="application/ld+json")
# print(results[1].prettify())

