from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from user import User
import time
from element import *


class JefeScreener:

    def __init__(self, pros: [], user: User, browser: str):
        if pros is None:
            pros = []
        self.user = user
        self.pros = pros
        self.driver, self.wait, self.actions = self.getDriver(browser)

    # user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15.2; rv:71.0) Gecko/20100101 Firefox/71.0'
    # options = webdriver.ChromeOptions()
    # options = webdriver.FirefoxOptions()
    # options.headless = True
    # options.add_argument('--ignore-certificate-errors')
    # options.add_argument(f'user-agent={user_agent}')
    # options.add_argument('--headless')
    # options.binary_location = '/Applications/Google Chrome 2.app/Contents/MacOS/Google Chrome'
    # driver = webdriver.Chrome(options=options, executable_path='drivers/chromedriver76')
    # driver = webdriver.Firefox(options=options, executable_path='drivers/geckodriver')
    # wait = WebDriverWait(driver, 10, poll_frequency=1,
    #                      ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException])
    # actions = ActionChains(driver)
    keep_running = True

    def getDriver(self, browser):
        try:
            driver, wait, actions = None, None, None
            if browser == "firefox":
                user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15.2; rv:71.0) Gecko/20100101 Firefox/71.0'
                options = webdriver.FirefoxOptions()
                options.add_argument('--ignore-certificate-errors')
                # options.add_argument(f'--user-agent={user_agent}')
                # options.add_argument('--headless')
                driver = webdriver.Firefox(options=options, executable_path='drivers/geckodriver')

            elif browser == "chrome":
                        user_agent = 'Google/5.0 (Macintosh; Intel Mac OS X 10.15.2; rv:76.0) Chrome/20100101 Chrome/76.0'
                        options = webdriver.ChromeOptions()
                        options.add_argument('--ignore-certificate-errors')
                        options.add_argument(f'user-agent={user_agent}')
                        # options.add_argument('--headless')
                        driver = webdriver.Chrome(options=options, executable_path='drivers/chromedriver76')

            wait = WebDriverWait(driver, 10, poll_frequency=1,
                                 ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException])
            actions = ActionChains(driver)

            return driver, wait, actions
        except:
            print("Error thrown while getting driver.")
            pass

    # Types of references: css, xpath, name, id, class, tag, text, pText (partial text)
    def click(self, element_reference, type_of_reference):
        find_xpath = f"document.evaluate('{element_reference}', document, null, XPathResult.ANY_TYPE, null).singleNodeValue"
        trigger_click = f"var element = {find_xpath};\nvar evt = document.createEvent('MouseEvents');\nevt.initEvent('click', true, true);\nelement.dispatchEvent(evt);"
        print(trigger_click)

        try:
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
            self.driver.execute_script("arguments[0].scrollIntoView();", element)
            self.driver.execute_script(trigger_click)
            # element.click()

        except:
            print("Error during click script")
            pass


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

    def login(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.NAME, usernameField)))
            print("\nLogging into Jefe...\n")
            field = self.driver.find_element_by_name(usernameField)
            field.send_keys(self.user.getUsername())
            field = self.driver.find_element_by_name(passwordField)
            field.send_keys(self.user.getPassword())
            self.click(loginButton, "xpath")
            print("\nSuccessfully logged into Jefe!\n")
        finally:
            pass

    def goToProfile(self, pro_id):
        try:
            print(f"Navigating to profile page of pro #{pro_id}")
            self.driver.get(f"{jefeBaseUrl}workers/{pro_id}")
            print(f"On pro #{pro_id} profile page.\n")
        except SessionNotCreatedException:
            pass

    def getWorkHistory(self):
        try:
            print("Getting table elements...\n")
            web_table = self.tableToArray(workHistoryTableColumns, "xpath")
            work_history_details = []
            qualified_roles = {}

            number_of_rows = len(self.tableToArray(workHistoryTableRows, "xpath"))
            number_of_columns = int(len(web_table) / number_of_rows)

            label = {
                0: "name",
                1: "position",
                2: "start",
                3: "duration"
            }

            for row in range(number_of_rows):
                column = 0
                details = {}
                cell_array = list()

                while column < number_of_columns - 1:
                    cell = web_table[row * number_of_columns + column].text

                    if column == 3:
                        print("Modifying duration of history...\n")
                        if "years" in cell or "year" in cell:
                            cell_array = cell.split(" ")
                            print(str(cell_array))

                            if cell_array[0] == "[CURRENT]":
                                print("Attempting to remove the first element from new list.\n")
                                cell_array.pop(0)
                                print("Removal successful. Tis now ", str(cell_array))

                            position = details.get("position")
                            duration = int(cell_array[0])

                            if position in qualified_roles.keys():
                                qualified_roles[position] += duration
                            else:
                                qualified_roles.update({position: duration})

                    details.update({label.get(column): cell.replace("[CURRENT] ", "")})
                    column += 1
                work_history_details.append(details)
            print("\nGot work history!\n")
            return self._getRoles(work_history_details)
        except:
            print("Error while getting work history. 126")
            pass

    def getQualifiedRoles(self):
        michelin_pro = False
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, workHistoryTab)))
            self.click(workHistoryTab, "xpath")

            print("Reviewing work history...\n")
            work_history = self.getWorkHistory()
            qualified_roles = self._getRoles(work_history)
            print("\nPro's qualified roles and duration of experience are as follows: " + str(qualified_roles))
            print("\nWork history reviewed.")
            return qualified_roles
        except:
            print("Error while getting qualified roles. 175-189")
            pass

    def _getRoles(self, table):
        if table is None:
            print("Work history is empty...")
            return
        roles = {}
        size = len(table)
        row = 0
        try:
            while row < size:
                data = table[row]
                print("\nName of Establishment: " + data.get("name") +
                      "\nPosition: " + data.get("position") +
                      "\nStart Date: " + data.get("start") +
                      "\nDuration of Employment: " + data.get("duration"))
                row += 1

                duration = data.get("duration")
                print("\n\nDuration = " + duration)
                cell_array = duration.split(" ")
                print(cell_array)

                if cell_array[1] == "years" or cell_array[1] == "year":
                    position = data.get("position")
                    number_of_years = int(cell_array[0])
                    if position in roles.keys():
                        roles[position] += number_of_years
                    else:
                        roles.update({position: number_of_years})
            return roles
        except:
            print("Error while getting roles. 191")
            pass

    def getReferences(self):
        try:
            print("Getting references...")
            cells = self.tableToArray(referenceTableColumns, "xpath")
            if len(cells) < 1:
                return

            references = {}

            label = {
                0: "name",
                1: "relationship",
                2: "is-good",
                3: "phone",
                4: "viewable",
                5: "attempts",
                6: "last-sent",
                7: "status"
            }

            table = self.tableToArray(referenceTableRows, "xpath")
            for element in table:
                print(element.text)
            number_of_rows = len(self.tableToArray(referenceTableRows, "xpath"))
            number_of_columns = int(len(cells) / number_of_rows)
            print("Number of rows: " + str(number_of_rows))
            print("Number of columns: " + str(number_of_columns))

            for row in range(number_of_rows):
                print("Reviewing row #" + str(row + 1))
                column = 0
                details = {}

                while column < number_of_columns:
                    details.update({label.get(column): cells[(row * number_of_columns) + column].text})
                    column += 1

                if details.get("status") == "Completed!" and details.get("is-good") == "-":
                    references.update({row: details})
            print("Size of references table: ", len(references))
            return references
        except:
            print("Error while getting references.")
            pass

    def reviewReferences(self):
        try:
            print("Reviewing pro's references...\n")
            self.wait.until(EC.presence_of_element_located((By.XPATH, referencesTab)))
            self.click(referencesTab, "xpath")
            references = self.getReferences()
            if len(references) < 1:
                print("There are no references to review. Throwing pro out.")
                return
            self._printReferences(references)
            status = self.reviewRefResponses(references)
            print("Reference review complete!\n")
            if status > 1:
                return True
            return False
        except:
            print("Error while reviewing references")
            pass

    def _printReferences(self, table):
        if table is None:
            print("Table is empty!")
            return
        print("Printing references...")
        for position, reference in table.items():
            print("\nName of Reference: ", reference.get("name"),
                  "\nRelationship: ", reference.get("relationship"),
                  "\nAccepted: ", reference.get("accepted"),
                  "\nPhone Number: ", reference.get("phone"),
                  "\nViewable: ", reference.get("viewable"),
                  "\nAttempts ", reference.get("attempts"),
                  "\nLast Sent: ", reference.get("last-sent"),
                  "\nStatus: ", reference.get("status")
                  )


    def reviewRefResponses(self, references):
        is_good = 1
        pro_approval_score = 0

        print("\nReviewing reference responses...\n")
        try:
            for row, reference in references:
                print("Checking reference row #", row)

                action_bronson = "/html/body/div/div/div[2]/div[2]/div/section/section/div/div[2]/div[1]/div[3]/div[3]/div/div/div[2]/div/div[2]/table/tbody/tr[" + str(
                    row + 1) + "]/td[9]/span/button/div/span"

                self.wait.until(EC.presence_of_element_located((By.XPATH, action_bronson)))
                self.driver.execute_script("arguments[0].scrollIntoView();",
                                           self.driver.find_element_by_xpath(action_bronson))
                self.actions.move_to_element(self.driver.find_element_by_xpath(action_bronson))
                self.click(action_bronson, "xpath")

                print("Looking for reference rating...")

                self.wait.until(EC.presence_of_element_located(
                    (By.XPATH, "/html/body/div[2]/div/div[1]/div/div/div/div[3]/div[1]/div[2]/div[2]/div[1]")))
                elements = self.driver.find_elements_by_xpath(referenceRatings)

                if len(elements) > 0:
                    for element in elements:
                        print(element.text)
                    print("Xpath found! Converting table to array...")
                    index = 0
                    for rating in elements:
                        print(rating.text, end=" "),
                        if int(rating.text) < 4 and index != 2:
                            is_good = 0
                            break
                        index += 1
                print("\nReviewing reference survey responses...\n")
                survey_elements = self.driver.find_elements_by_xpath(referenceSurvey)
                for element in survey_elements:
                    print(element.text)

                if survey_elements[0].text == "No" or survey_elements[1].text == "No":
                    is_good = 0

                def set_bad():
                    self.click(referenceBad, "xpath")

                def set_good(score):
                    if reference.get("relationship") == "Supervisor":
                        score += 1
                    self.click(referenceGood, "xpath")

                approved = {
                    0: set_bad(),
                    1: set_good(pro_approval_score)
                }
                pro_approval_score += is_good
                approved.get(is_good)

            print("\nInspection complete!\n")
            return pro_approval_score
        except:
            print("Error while assessing pro eligibility")
            pass

    def server_template(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, eventServer)))
            self.actions.move_to_element(eventServer)
            self.click(eventServer, "xpath")
        except:
            pass

    def busser_template(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, busser)))
            self.actions.move_to_element(busser)
            self.click(busser, "xpath")
        except:
            pass

    def line_cook_template(self, duration):
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, lineCookMed)))

            if duration < 2:
                self.actions.move_to_element(lineCookLow)
                self.click(lineCookLow, "xpath")
            elif duration < 3:
                self.actions.move_to_element(lineCookMed)
                self.click(lineCookMed, "xpath")
            else:
                self.actions.move_to_element(lineCookHigh)
                self.click(lineCookHigh, "xpath")
        except:
            pass

    def prep_cook_template(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, prepCook)))
            self.actions.move_to_element(prepCook)
            self.click(prepCook, "xpath")
        except:
            pass

    def dishwasher_template(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, dishwasher)))
            self.actions.move_to_element(dishwasher)
            self.click(dishwasher, "xpath")
        except:
            pass

    def pastry_cook_template(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, pastryCook)))
            self.actions.move_to_element(pastryCook)
            self.click(pastryCook, "xpath")
        except:
            pass

    def foh_template(self, duration):
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, fohHigh)))
            time.sleep(2)

            if duration < 2:
                self.actions.move_to_element(fohLow)
                self.click(fohLow, "xpath")
                print("clicked low foh template...\n")
            if duration < 3:
                self.wait.until(EC.presence_of_element_located((By.XPATH, fohMed)))
                self.click(fohMed, "xpath")
                print("clicked medium foh template...\n")
            else:
                self.actions.move_to_element(fohHigh)
                self.click(fohHigh, "xpath")
        except:
            pass

    def cashier_template(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, cashier)))
            self.actions.move_to_element(cashier)
            self.click(cashier, "xpath")
        except:
            pass

    def barback_template(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, barback)))
            self.actions.move_to_element(barback)
            self.click(barback, "xpath")
        except:
            pass

    def bartender_template(self, duration):
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, bartenderHigh)))

            if duration >= 3:
                self.actions.move_to_element(bartenderHigh)
                self.click(bartenderHigh, "xpath")
            elif duration >= 2:
                self.actions.move_to_element(bartenderMed)
                self.click(bartenderMed, "xpath")
            else:
                self.actions.move_to_element(bartenderLow)
                self.click(bartenderLow, "xpath")
        except:
            pass

    def barista_template(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, baristaTemplate)))
            self.actions.move_to_element(baristaTemplate)
            self.click(baristaTemplate, "xpath")
        except:
            pass

    def get_action(self, position, duration=None):
        action = {
            "Server": self.server_template(),
            "Busser": self.busser_template(),
            "Foodrunner": self.busser_template(),
            "Line Cook": self.line_cook_template(duration),
            "Sous Chef": self.line_cook_template(duration),
            "Executive Chef": self.line_cook_template(duration),
            "Prep Cook": self.prep_cook_template(),
            "Chef de Cuisine": self.prep_cook_template(),
            "Dishwasher": self.dishwasher_template(),
            "Pasty Cook": self.pastry_cook_template(),
            "General Manager": self.foh_template(duration),
            "Cashier": self.cashier_template(),
            "Barback": self.barback_template(),
            "Bartender": self.bartender_template(duration),
            "Barista": self.barista_template()
        }
        return action.get(position)

    def addAttributes(self, qualified_roles):
        try:
            if qualified_roles is None:
                print("Pro is not qualified for any roles.")
                return
            self.wait.until(EC.presence_of_element_located((By.XPATH, matchAttributesTab)))
            self.click(matchAttributesTab, "xpath")

            print("Matching attributes to qualified roles...\n")
            for position, duration in qualified_roles.items():
                self.wait.until(EC.presence_of_element_located((By.XPATH, matchAttributesTemplate)))
                self.click(matchAttributesTemplate, "xpath")
                self.wait.until(EC.presence_of_element_located((By.XPATH, attributeTemplates)))
                self.click(attributeTemplates, "xpath")
                self.get_action(position, duration)
                self.wait.until(EC.presence_of_element_located((By.XPATH, submitAttribute)))
                self.click(submitAttribute, "xpath")
        except:
            print("Error while adding attributes.")
            pass

    def approveForFth(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, editProfile)))
            self.click(editProfile, "xpath")
            self.wait.until(EC.presence_of_element_located((By.NAME, pxApprove)))
            self.click(pxApprove, "name")
            self.click(editorSubmit, "xpath")
        except:
            print("Error while approving for fth.")
            pass

    def archivePro(self, archive_reason=None):
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, optionsDropDown)))
            self.click(optionsDropDown, "xpath")
            self.wait.until(EC.presence_of_element_located((By.XPATH, archivePro)))
            self.click(archivePro, "xpath")
            self.wait.until(EC.presence_of_element_located((By.XPATH, submitArchive)))
        except:
            print("Error while finalizing pro")

    def finalizePro(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, optionsDropDown)))
            self.click(optionsDropDown, "xpath")
            self.wait.until(EC.presence_of_element_located((By.XPATH, matchToShifts)))
            self.click(matchToShifts, "xpath")
        except:
            pass

    def killDriver(self):
        try:
            self.driver.close()
            self.keep_running = False
        except:
            pass

    def screenThem(self):
        while len(self.pros) > 0 and self.keep_running is True:
            next_pro = self.pros.pop()
            try:
                self.goToProfile(next_pro)
                self.driver.fullscreen_window()
                self.login()
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                qualified_roles = self.getQualifiedRoles()
                result = self.reviewReferences()
                if result is False:
                    print("Pro not approved")
                    self.archivePro()
                    return
                print("Pro has been approved. Adding new attributes...")
                self.addAttributes(qualified_roles)
                self.approveForFth()
                self.finalizePro()
            except:
                print("Ran into an error while screening pro #", next_pro)
            finally:
                pass
        self.killDriver()

    def test(self):
        self.goToProfile("3855")
        self.driver.maximize_window()
        self.login()
        self.getQualifiedRoles()
        self.reviewReferences()

        self.killDriver()

    def run(self):
        self.screenThem()
