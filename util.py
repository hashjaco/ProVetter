from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class util:

    def __init__(self, wait: WebDriverWait, driver: webdriver):
        self.wait = wait
        self.driver = driver

    def tableToArray(self, element_reference, type_of_reference):
        try:
            path = {
                "css": By.CSS_SELECTOR,
                "xpath": By.XPATH,
                "tag": By.TAG_NAME,
                "text": By.LINK_TEXT,
                "pText": By.PARTIAL_LINK_TEXT,
                "class": By.CLASS_NAME,
                "name": By.NAME,
                "id": By.ID
            }
            self.wait.until(EC.presence_of_all_elements_located((path.get(type_of_reference), element_reference)))
            return self.driver.find_elements(path.get(type_of_reference), element_reference)
        except:
            print("Error inserting table elements into array.")


    def click(self, element_reference, type_of_reference):
        def _find_xpath_js():
            return f"document.evaluate({element_reference}, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;"

        def _trigger_click():
            return f"var element = {_find_xpath_js()}; element.dispatchEvent( new Event('click', true, true) );"

        def click_script():
            _trigger_click()

        action = {
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "tag": By.TAG_NAME,
            "text": By.LINK_TEXT,
            "pText": By.PARTIAL_LINK_TEXT,
            "class": By.CLASS_NAME,
            "name": By.NAME,
            "id": By.ID
        }
        self.wait.until(EC.presence_of_element_located((action.get(type_of_reference), element_reference)))
        element = self.driver.find_element(action.get(type_of_reference), element_reference)
        self.driver.execute_script(f"{element}.scrollIntoView();")
        self.driver.execute_script(click_script())