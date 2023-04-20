#!python3
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException
import csv
import argparse
import typing
import collections
from enum import Enum
import sys


class AECResult(Enum):
    PASS = "Pass"
    PARTIAL = "Partial"
    FAIL = "Fail"
    FAIL_STREET = "Fail_Street"
    FAIL_SUBURB = "Fail_Suburb"


AECStatus = collections.namedtuple(
    "AECStatus", ["result", "federal", "state", "local_gov", "local_ward"]
)


def getAECStatus(
    driver: webdriver,
    givenNames: str,
    surname: str,
    postcode: str,
    suburb: str,
    state: str,
    streetName: str,
) -> AECStatus:

    elem = driver.find_element(By.ID, "ctl00_ContentPlaceHolderBody_textGivenName")
    elem.clear()
    elem.send_keys(givenNames)

    elem = driver.find_element(By.ID, "ctl00_ContentPlaceHolderBody_textSurname")
    elem.clear()
    elem.send_keys(surname)

    elem = driver.find_element(By.ID, "ctl00_ContentPlaceHolderBody_textPostcode")
    elem.clear()
    elem.send_keys(postcode)

    time.sleep(0.1)

    suburb_state = f"{str.upper(suburb)} ({state})"
    try:
        suburb_dropdown = Select(
            driver.find_element(By.ID, "ctl00_ContentPlaceHolderBody_DropdownSuburb")
        )
        suburb_dropdown.select_by_value(suburb_state)
    except Exception as e:
        print(e, suburb_state, file=sys.stderr)
        return AECStatus(AECResult.FAIL_SUBURB, "", "", "", "")

    elem = driver.find_element(By.ID, "ctl00_ContentPlaceHolderBody_textStreetName")
    elem.clear()
    elem.send_keys(streetName)

    captcha_entered = False

    driver.find_element(
        By.ID, "ctl00_ContentPlaceHolderBody_textVerificationCode"
    ).send_keys("")

    while not captcha_entered:
        time.sleep(1)
        try:
            elem = driver.find_element(
                By.ID, "ctl00_ContentPlaceHolderBody_textVerificationCode"
            )
        except NoSuchElementException:
            break

        if len(elem.get_attribute("value")) == 4:
            driver.find_element(
                By.ID, "ctl00_ContentPlaceHolderBody_buttonVerify"
            ).click()

            try:
                # Look for the first name tag, if it exist the captcha failed
                driver.find_element(By.ID, "ctl00_ContentPlaceHolderBody_textGivenName")
            except Exception:
                # Otherwise we're good. (why is a success state in an exception, brah)
                captcha_entered = True

            if not captcha_entered:
                driver.find_element(
                    By.ID, "ctl00_ContentPlaceHolderBody_textVerificationCode"
                ).send_keys("")

    try:
        driver.find_element(By.ID, "ctl00_ContentPlaceHolderBody_panelSuccess")

        federal_division = ""
        state_district = ""
        local_gov = ""
        local_ward = ""

        try:
            federal_division = driver.find_element(
                By.ID, "ctl00_ContentPlaceHolderBody_linkProfile"
            ).text
            state_district = driver.find_element(
                By.ID, "ctl00_ContentPlaceHolderBody_labelStateDistrict2"
            ).text
            local_gov = driver.find_element(
                By.ID, "ctl00_ContentPlaceHolderBody_labelLGA2"
            ).text
            local_ward = driver.find_element(
                By.ID, "ctl00_ContentPlaceHolderBody_labelLGAWard2"
            ).text
        except Exception:
            pass

        driver.find_element(By.ID, "ctl00_ContentPlaceHolderBody_buttonBack").click()
        return AECStatus(
            AECResult.PASS, federal_division, state_district, local_gov, local_ward
        )

    except Exception:
        out = AECStatus(AECResult.FAIL, "", "", "", "")
        try:
            reason = driver.find_element(
                By.ID, "ctl00_ContentPlaceHolderBody_labelFailedReason"
            )
            if "partial" in reason.text:
                out = AECStatus(AECResult.PARTIAL, "", "", "", "")
            elif "street" in reason.text:
                out = AECStatus(AECResult.FAIL_STREET, "", "", "", "")
        except Exception:
            pass
        driver.find_element(
            By.ID, "ctl00_ContentPlaceHolderBody_buttonTryAgain"
        ).click()
        return out


def main():
    parser = argparse.ArgumentParser(description="automate AEC checking")
    parser.add_argument(
        "--skip", type=int, default=0, help="skip entries you've already seen"
    )
    parser.add_argument("--infile", default="input.csv")
    parser.add_argument("--outfile", default="output.csv")
    args = parser.parse_args()

    driver = webdriver.Firefox()
    driver.get("https://check.aec.gov.au/")

    writer = csv.writer(
        open(
            args.outfile,
            "a",
            newline="",
        )
    )
    count = 0
    with open(args.infile) as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for row in reader:
            count += 1
            if count <= 1 + args.skip:
                writer.writerow(row)
                continue
            time.sleep(0.5)
            status = getAECStatus(driver, *row[:6])
            writer.writerow(row + [i for i in status])
    writer.close()
    driver.close()


if __name__ == "__main__":
    main()
