import base64
import undetected_chromedriver as uc
import capsolver
import time
import os
from io import BytesIO
import csv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

pages_to_scrape = 3  # Default number of pages to scrape
contact_message = "Hi, I'm interested in your property"
name = "John Alex"
phone = "+16084631153"
email = "john.alex@gmail.com"
capsolver.api_key = "CAP-557EDBC2B5095D762F685AAB094269D3"

driver = uc.Chrome()

def js_click(driver, element):
    driver.execute_script("arguments[0].click();", element)

def process_property(driver, property):
    try:
        driver.get(property)
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.summary-left h1"))
        )
        title = driver.find_element(By.CSS_SELECTOR, "div.summary-left h1").text
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span[itemprop='price']"))
        )
        price = driver.find_element(By.CSS_SELECTOR, "span[itemprop='price']").text
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "js-ver-mapa-zona"))
        )
        county = driver.find_element(By.ID, "js-ver-mapa-zona")
        x = driver.find_element(By.ID, "js-ver-mapa-zona")
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "js-ver-mapa-zona"))
        )
        address = driver.execute_script(
            """
            var element = arguments[0];
            var textNode = element.nextSibling;
            while (textNode.nodeType !== Node.TEXT_NODE) {
                textNode = textNode.nextSibling;
            }
            var textContent = textNode.textContent.trim();
            return textContent.replace(/^-+\s*/, '');
        """,
            x,
        )
        complete_address = county.text + address
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "js-contact-top-text"))
        )
        contact_textarea = driver.find_element(By.ID, "js-contact-top-text")
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.feature-container"))
        )
        features = driver.find_element(By.CSS_SELECTOR, "ul.feature-container")
        WebDriverWait(features, 3).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li"))
        )
        lis = features.find_elements(By.CSS_SELECTOR, "li")
        area = (
            lis[0]
            .find_element(By.XPATH, '//*[@id="js-feature-container"]/ul/li[1]/strong')
            .text
            + " m²"
        )
        rooms = (
            lis[1]
            .find_element(By.XPATH, '//*[@id="js-feature-container"]/ul/li[2]/strong')
            .text
            + " hab."
        )
        toilets = (
            lis[2]
            .find_element(By.XPATH, '//*[@id="js-feature-container"]/ul/li[3]/strong')
            .text
            + " baños"
        )
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "js-cont-superior"))
        )
        contact_textarea.send_keys("\b" * len(contact_textarea.get_attribute("value")))
        contact_textarea.send_keys(contact_message)
        js_click(driver, driver.find_element(By.ID, "js-cont-superior"))
        time.sleep(1)
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "Nombre"))
        )
        name_input = driver.find_element(By.ID, "Nombre")
        name_input.send_keys("\b" * len(contact_textarea.get_attribute("value")))
        name_input.send_keys(name)
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "Telefono"))
        )
        phone_input = driver.find_element(By.ID, "Telefono")
        phone_input.send_keys("\b" * len(contact_textarea.get_attribute("value")))
        phone_input.send_keys(phone)
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, "Email")))
        email_input = driver.find_element(By.ID, "Email")
        email_input.send_keys("\b" * len(contact_textarea.get_attribute("value")))
        email_input.send_keys(email)
        try:
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "span.tiny-span.required")
                )
            )
            parent_element = driver.find_element(
                By.CSS_SELECTOR, "span.tiny-span.required"
            )

            driver.execute_script(
                """
                var parent = arguments[0];
                var text = arguments[1];
                var nodes = Array.from(parent.childNodes);
                var textNode = nodes.find(node => node.nodeType === Node.TEXT_NODE && node.textContent.includes(text));
                textNode.parentElement.click();
            """,
                parent_element,
                "Acepto el ",
            )

        except Exception as e:
            pass

        time.sleep(3)

        isCaptcha = True
        while(isCaptcha):
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.ID, "CaptchaImage"))
            )
            captcha_image = driver.find_element(By.ID, "CaptchaImage")
            screenshot = captcha_image.screenshot_as_png
            buffered = BytesIO(screenshot)
            buffered.seek(0)
            base64_image = base64.b64encode(buffered.read()).decode("utf-8")

            captcha_solution = solve_captcha(base64_image)
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.ID, "CaptchaInputText"))
            )
            captcha_input = driver.find_element(By.ID, "CaptchaInputText")
            captcha_input.send_keys(captcha_solution["text"])
            if len(captcha_solution["text"]) == 5:
                time.sleep(0.5)
                js_click(driver, driver.find_element(By.ID, "submitSolicitudes"))
                try:
                    time.sleep(0.5)
                    WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.ID, "captchaError"))
                    )
                    captchaError = driver.find_element(By.ID, "captchaError").text
                    if captchaError == "":
                        isCaptcha = False
                    else:
                        isCaptcha = True
                        print("Retrying Captcha...")
                except (TimeoutException, NoSuchElementException):
                    isCaptcha = False
                    pass
                except Exception as e:
                    isCaptcha = False
                    pass
            else:
                js_click(driver, driver.find_element(By.ID, "reloadCaptcha"))
                time.sleep(1)

        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.tel-llamar"))
        )
        owner_phone = driver.find_element(By.CSS_SELECTOR, "span.tel-llamar")
        phone_num = owner_phone.text
        while phone_num == "":
            # try getting phone number again
            owner_phone = driver.find_element(By.CSS_SELECTOR, "span.tel-llamar")
            phone_num = owner_phone.text

        return {
            "title": title,
            "price": price,
            "address": complete_address,
            "area": area,
            "rooms": rooms,
            "toilets": toilets,
            "phone": phone_num,
        }

    except Exception as e:
        return False

def get_properties(driver):
    try:
        properties = driver.find_elements(By.CSS_SELECTOR, "h3.list-item-title")
        if not properties:
            return []
        property_links = [
            property.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            for property in properties
        ]
        return property_links
    except Exception as e:
        return []

def change_page(driver, new_page):
    try:
        new_url = f"{url}-{new_page}.htm"
        driver.get(new_url)
        while driver.execute_script("return document.readyState") != "complete":
            pass
        while get_properties(driver) == []:
            pass
    except Exception as e:
        return False

def solve_captcha(base64_image):
    print("Solving captcha...")
    solution = capsolver.solve(
        {
            "type": "ImageToTextTask",
            "module": "common",
            "body": base64_image,
        }
    )
    print(solution)
    return solution

def main():
    url_parts = input("Please enter the URL: ").split(".")[:-1]
    global url
    url = '.'.join(url_parts)
    driver.get(f"{url}.htm")
    
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "didomi-notice-agree-button"))
        )
        js_click(driver, driver.find_element(By.ID, "didomi-notice-agree-button"))
    except Exception as e:
        pass
    
    while driver.execute_script("return document.readyState") != "complete":
        pass

    while get_properties(driver) == []:
        pass

    pagination_alert_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "next"))
    )
    time.sleep(1)
    previous_li_element = pagination_alert_element.find_element(By.XPATH, "./preceding-sibling::li[1]")
    try:
        pages_to_scrape = int(previous_li_element.text.strip())
    except ValueError:
        pages_to_scrape = 0
    print(f"Number of pages: {pages_to_scrape}")

    if not os.path.exists("./results.csv"):
        with open("./results.csv", "w", newline="") as csvfile:
            fieldnames = [
                "Title",
                "Price",
                "Address",
                "Area",
                "Rooms",
                "Toilets",
                "Phone",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

    for i in range(pages_to_scrape-1):
        properties = get_properties(driver)
        if properties == []:
            print("No properties found")
            break
        for property in properties:
            result = process_property(driver, property)
            if result and result["phone"] and result != {}:
                print(result)
                with open("./results.csv", "a", newline="") as csvfile:
                    csvfile.write(
                        f"{result['title']},{result['price']},{result['address']},{result['area']},{result['rooms']},{result['toilets']},{result['phone']}\n"
                    )

            else:
                print("Failed to process")
                print(result)
            time.sleep(3)

        time.sleep(10)
        change_page(driver, i+1 )

    print("Completed Scraping data successfully!")

if __name__ == "__main__":
    main()
