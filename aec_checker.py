from selenium import webdriver;
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import csv

driver= webdriver.Firefox();
driver.get('https://check.aec.gov.au/')

writer = csv.writer(open('output.csv', 'w', newline='',))

count = 0
with open('input.csv') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in spamreader:
        count += 1
        if count == 1:
            continue

        time.sleep(.1)

        elem = driver.find_element(By.ID, "ctl00_ContentPlaceHolderBody_textGivenName")
        elem.clear()
        elem.send_keys(row[0])

        elem = driver.find_element(By.ID, "ctl00_ContentPlaceHolderBody_textSurname")
        elem.clear()
        elem.send_keys(row[1])

        
        elem = driver.find_element(By.ID, "ctl00_ContentPlaceHolderBody_textPostcode")
        elem.clear()
        elem.send_keys(row[2])

        time.sleep(.1)

        suburb_state = f"{str.upper(row[3])} ({row[4]})"
        suburb_dropdown = Select(driver.find_element(By.ID, "ctl00_ContentPlaceHolderBody_DropdownSuburb"))
        suburb_dropdown.select_by_value(suburb_state)

        elem = driver.find_element(By.ID, "ctl00_ContentPlaceHolderBody_textStreetName")
        elem.clear()
        elem.send_keys(row[5])

        captcha_entered = False

        driver.find_element(By.ID, "ctl00_ContentPlaceHolderBody_textVerificationCode").send_keys("")
        
        while captcha_entered == False:
            time.sleep(1)
            elem = driver.find_element(By.ID, "ctl00_ContentPlaceHolderBody_textVerificationCode")
            if len(elem.get_attribute("value")) == 4:
                captcha_entered = True

        elem = driver.find_element(By.ID, "ctl00_ContentPlaceHolderBody_buttonVerify")
        elem.click()

        try:
            elem = driver.find_element(By.ID, "ctl00_ContentPlaceHolderBody_linkProfile")
            division = elem.text
            row.append("Pass")
            row.append(division)
            writer.writerow(row)
            driver.find_element(By.ID, "ctl00_ContentPlaceHolderBody_buttonBack").click()
            
        except Exception:
            row.append("Fail")
            row.append("")
            writer.writerow(row)
            driver.find_element(By.ID, "ctl00_ContentPlaceHolderBody_buttonTryAgain").click()

        

        
        
        