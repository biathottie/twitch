from selenium import webdriver
from selenium.webdriver.common.by import By
import csv
import time

patches = ["14.1","14.2","14.3","14.4","14.5","14.6","14.7","14.8","14.9","14.10","14.11","14.12","14.13","14.14","14.15","14.16","14.17","14.18","14.19","14.20","14.21","14.22","14.23"]
ranks = ["iron","bronze","silver","gold","platinum","emerald","diamond","diamond,master,grandmaster,challenger"]
ranksTwo = ["Iron","Bronze","Silver","Gold","Platinum","Emerald","Diamond","Diamond+"]

for patch in patches:
    count = 0
    with open(f"season14test{patch}.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        for rank in ranks:
            url = f'https://www.metasrc.com/lol/{patch}/stats?ranks={rank}'
            driver = webdriver.Chrome()
            driver.get(url)

            time.sleep(10)

            table_body = driver.find_element(By.TAG_NAME, "tbody")
            table_rows = table_body.find_elements(By.TAG_NAME, "tr")

            for row in table_rows:
                table_data = row.find_elements(By.TAG_NAME, "td")
                row_data = []
                for data in table_data:
                    row_data.append(data.text)
                row_data.append(patch)
                row_data.append(ranksTwo[count])
                writer.writerow(row_data)
            driver.quit()
            count += 1 