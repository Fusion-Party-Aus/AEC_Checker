#!python3
from selenium import webdriver;
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException
import csv
import argparse

parser = argparse.ArgumentParser(description="automate AEC checking")
parser.add_argument('--skip', type=int, default=0, help="skip entries you've already seen")
parser.add_argument('--infile', default='input.csv')
parser.add_argument('--outfile', default='output.csv')
args = parser.parse_args()

driver= webdriver.Firefox();
driver.get('https://check.aec.gov.au/')

writer = csv.writer(open(args.outfile, 'a', newline='',))

count = 0
with open(args.infile) as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    for row in spamreader:
        count += 1
        if count <= 1 + args.skip:
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
        try:
            suburb_dropdown = Select(driver.find_element(By.ID, "ctl00_ContentPlaceHolderBody_DropdownSuburb"))
            suburb_dropdown.select_by_value(suburb_state)
        except Exception:
            row.append("Fail")
            row.append("")
            writer.writerow(row)
            continue

        elem = driver.find_element(By.ID, "ctl00_ContentPlaceHolderBody_textStreetName")
        elem.clear()
        elem.send_keys(row[5])

        captcha_entered = False

        driver.find_element(By.ID, "ctl00_ContentPlaceHolderBody_textVerificationCode").send_keys("")
        
        while captcha_entered == False:
            time.sleep(1)
            try:
                elem = driver.find_element(By.ID, "ctl00_ContentPlaceHolderBody_textVerificationCode")
            except NoSuchElementException:
                break                
            if len(elem.get_attribute("value")) == 4:
                driver.find_element(By.ID, "ctl00_ContentPlaceHolderBody_buttonVerify").click()

                try:
                    # Look for the first name tag, if it exist the captcha failed
                    driver.find_element(By.ID, "ctl00_ContentPlaceHolderBody_textGivenName")
                except Exception:
                    # Otherwise we're good. (why is a success state in an exception, brah)
                    captcha_entered = True

                if not captcha_entered:
                    driver.find_element(By.ID, "ctl00_ContentPlaceHolderBody_textVerificationCode").send_keys("")

        try:
            success = driver.find_element(By.ID, "ctl00_ContentPlaceHolderBody_panelSuccess")
            row.append("Pass")
            try:
                elem = driver.find_element(By.ID, "ctl00_ContentPlaceHolderBody_linkProfile")
                division = elem.text
                row.append(division)
            except Exception:
                row.append("")
            writer.writerow(row)
            driver.find_element(By.ID, "ctl00_ContentPlaceHolderBody_buttonBack").click()
            
        except Exception:
            row.append("Fail")
            row.append("")
            writer.writerow(row)
            driver.find_element(By.ID, "ctl00_ContentPlaceHolderBody_buttonTryAgain").click()

        

        
        
        
