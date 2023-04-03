from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import ini_reader

s = Service(ChromeDriverManager().install())


options = Options()
options.add_argument("--headless")
options.add_argument("--log-level=3")

driver = webdriver.Chrome(service=s, chrome_options=options)
driver.maximize_window()


def signals():
    try:
        driver.get("https://www.investing.com/technical/technical-summary")

        technical_summary_table = driver.find_element(By.XPATH, value='//*[@id="technical_summary_container"]/table')
        technical_summary_rows = technical_summary_table.find_elements(By.TAG_NAME, value="tr")

        technical_summary_rows = technical_summary_rows[1:]

        currency_pairs_dic = {}
        pair_index = 0
        summary_index = 2
        for index in range(0, len(technical_summary_rows) // 3):
            found = False
            if "Moving Averages:" in technical_summary_rows[pair_index].text:
                currency_pair = technical_summary_rows[pair_index].text.split('\n')[0].replace('/', '')
                current_price = technical_summary_rows[pair_index].text.split('\n')[1]
                found = True

            if "Summary:" in technical_summary_rows[summary_index].text and found:
                strong_buy_count = technical_summary_rows[summary_index].text.count("Strong Buy")
                strong_sell_count = technical_summary_rows[summary_index].text.count("Strong Sell")
                if strong_buy_count == 4:
                    buy_or_sell = "SELL"
                elif strong_sell_count == 4:
                    buy_or_sell = "BUY"
                else:
                    buy_or_sell = "Neutral"
                pair_index = pair_index + 3
                summary_index = summary_index + 3
                if buy_or_sell != "Neutral":
                    currency_suggestion_list = {"price": current_price, "BuyOrSell": buy_or_sell}
                    currency_pairs_dic[currency_pair] = currency_suggestion_list

        if ini_reader.props["commodity_trade"] == 'true':

            driver.get("https://www.investing.com/technical/commodities-technical-summary")
            technical_summary_table = driver.find_element(By.XPATH, value='//*[@id="technical_summary_container"]/table')
            technical_summary_rows = technical_summary_table.find_elements(By.TAG_NAME, value="tr")
            technical_summary_rows = technical_summary_rows[1:]
            pair_index = 0
            summary_index = 2
            for index in range(0, len(technical_summary_rows) // 3):
                found = False
                if "Moving Averages:" in technical_summary_rows[pair_index].text:
                    commodity = technical_summary_rows[pair_index].text.split('\n')[0]
                    if commodity == "Gold":
                        commodity = "XAUUSD"
                    if commodity == "Silver":
                        commodity = "XAGUSD"
                    if commodity == "Copper":
                        commodity = "XCUUSD"
                    current_price = technical_summary_rows[pair_index].text.split('\n')[1]
                    found = True

                if "Summary:" in technical_summary_rows[summary_index].text and found:
                    strong_buy_count = technical_summary_rows[summary_index].text.count("Strong Buy")
                    strong_sell_count = technical_summary_rows[summary_index].text.count("Strong Sell")
                    if strong_buy_count == 4:
                        buy_or_sell = "SELL"
                    elif strong_sell_count == 4:
                        buy_or_sell = "BUY"
                    else:
                        buy_or_sell = "Neutral"
                    pair_index = pair_index + 3
                    summary_index = summary_index + 3
                    if buy_or_sell != "Neutral":
                        currency_suggestion_list = {"price": current_price, "BuyOrSell": buy_or_sell}
                        currency_pairs_dic[commodity] = currency_suggestion_list
    except:
        return {}

    return currency_pairs_dic
