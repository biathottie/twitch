from selenium import webdriver
from selenium.webdriver.common.by import By
import csv
import time

with open("userList.txt", mode="a", encoding="utf-8", newline="") as file:
    writer = csv.writer(file)
    url = 'https://www.op.gg/leaderboards/tier?tier=master&page=9'
    driver = webdriver.Chrome()
    driver.get(url)

    time.sleep(10)

    table_body = driver.find_element(By.TAG_NAME, "tbody")
    table_rows = table_body.find_elements(By.TAG_NAME, "tr")

    for row in table_rows:
        table_data = row.find_elements(By.TAG_NAME, "td")
        row_data = []
        for data in table_data[1:-5]:
            row_data.append(data.text.replace("\n", ""))
        writer.writerow(row_data)
    driver.quit()