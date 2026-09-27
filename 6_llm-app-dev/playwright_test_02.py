import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # 1. 브라우저 열기
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # 2. 페이지 이동
    url = "http://quotes.toscrape.com"
    page.goto(url=url)

    # 3. 페이지 가져오기
    # print(page.content())
    html = page.content()

    # 4. 브라우저 닫기
    browser.close()

    # 5. 파싱
    soup = BeautifulSoup(html, "html.parser")
    quotes = soup.find_all("div", class_="quote")
    print(len(quotes))

    # first = quotes[0]
    # for i in range(10):
    #     print(quotes[i].find("span", class_="text").text)
    #     print(quotes[i].find("small", class_="author").text)
    #     print("=" * 80 + "\n")

    all_quote = []
    for div in quotes:
        all_quote.append(
            {
                "명언": div.find("span", class_="text").text.strip("'"),
                "작가": div.find("small", class_="author").text,
                "태그": ", ".join([t.text for t in div.find_all("a", class_="tag")]),
            }
        )

    print(pd.DataFrame(all_quote))

    pd.DataFrame(all_quote).to_csv("quotes.csv", index=False, encoding="utf-8")
