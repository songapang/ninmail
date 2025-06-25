import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.remote.webelement import WebElement

URL = 'https://signup.live.com/signup'
WAIT = 25

def create_account(driver, 
                   username, 
                   password, 
                   first_name, 
                   last_name,
                   country,
                   month,
                   day,
                   year,
                   hotmail):
    """
    Automatically creates an outlook/hotmail account.

    Args:
        driver (WebDriver): The Selenium WebDriver instance for the configured browser.
        username (str): The desired username for the email account.
        password (str): The desired password for the email account.
        first_name (str): The first name for the account holder.
        last_name (str): The last name for the account holder.
        country (str): The country for the account holder.
        month (str): The birth month for the account holder.
        day (str): The birth day for the account holder.
        year (str): The birth year for the account holder.
        hotmail (bool): Flag indicating whether to create a Hotmail account.

    Returns:
        tuple: Email and password of the created account.

    """
    logging.info('Creating outlook account')

    driver.get(URL)

    # Select create email
    email_input = WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, 'liveSwitch')))
    email_input.click()

    driver.implicitly_wait(2)

    # Insert username
    username_input = WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, 'usernameInput')))
    username_input.send_keys(username)

    # Select hotmail if hotmail is True
    if hotmail:
        email_domain_combobox = Select(WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, 'LiveDomainBoxList'))))
        email_domain_combobox.select_by_index(1)

    # driver.find_element(By.ID, 'iSignupAction').click()
    element = driver.find_element(By.XPATH, "//button[@id='nextButton' and @type='submit']").click()
    driver.implicitly_wait(2)

    # Insert password and dismark notifications
    try:
        show_password_checkbox = WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, 'ShowHidePasswordCheckbox')))
        show_password_checkbox.click()
        time.sleep(3)
        driver.find_element(By.ID, 'iOptinEmail').click()
    except:
        pass
    driver.find_element(By.ID, 'Password').send_keys(password)
    password_next = WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.XPATH, "//button[@id='nextButton' and @type='submit']")))
    password_next.click()
    
    driver.implicitly_wait(2)

    # Insert First and Last name
    first_name_input = WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, 'firstNameInput')))
    first_name_input.send_keys(first_name)
    last_name_input = WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, 'lastNameInput')))
    last_name_input.send_keys(last_name)
    driver.find_element(By.XPATH, "//button[@id='nextButton' and @type='submit']").click()

    # Insert Country and birthdate
    country_combobox = Select(WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, 'countryRegionDropdown'))))
    country_combobox.select_by_visible_text(country)

    year_input = WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, 'BirthYear')))
    year_input.send_keys(year)

    month_combobox = Select(WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, 'BirthMonth'))))
    # month_combobox.select_by_index(int(month))
    month_combobox.select_by_visible_text(month)

    day_combobox = Select(WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, 'BirthDay'))))
    # day_combobox.select_by_index(int(day))
    day_combobox.select_by_visible_text(day)

    
    driver.find_element(By.XPATH, "//button[@id='nextButton' and @type='submit']").click()

    driver.implicitly_wait(2)

    # captcha next button
    WebDriverWait(driver, WAIT).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "enforcementFrame")))
    WebDriverWait(driver, WAIT).until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe")))
    WebDriverWait(driver, WAIT).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "game-core-frame")))
    next_button = WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div#root > div > div > button")))
    next_button.click()

    wait = WebDriverWait(driver, 60) # wait for capsolver extension to solve the captcha
    for _ in range(3):
        try:
            h2_element = wait.until(EC.visibility_of_element_located((By.XPATH, "//h2[contains(text(), 'Something went wrong. Please reload the challenge to try again.')]")))

            if h2_element and isinstance(h2_element, WebElement):
                button = driver.find_element(By.XPATH, "//button[contains(text(), 'Reload Challenge')]")
                button.click()
        except:
            break

    time.sleep(5)
    try:
        acc_created_text = wait.until(EC.visibility_of_element_located((By.XPATH, "//span[contains(text(), 'A quick note about your Microsoft account')]")))
        if acc_created_text:
            logging.info(f'{"Hotmail" if hotmail else "Outlook"} email account created successfully.')
            logging.info("Account Details:")
            logging.info(f"Email:      {username}@{'hotmail' if hotmail else 'outlook'}.com")
            logging.info(f"Password:      {password}")
            logging.info(f"First Name:    {first_name}")
            logging.info(f"Last Name:     {last_name}")
            logging.info(f"Country:       {country}")
            logging.info(f"Date of Birth: {month}/{day}/{year}")
            driver.quit()
            return f"{username}@{'hotmail' if hotmail else 'outlook'}.com", password
    except:
        logging.error(f"There was an error creating the {'Hotmail' if hotmail else 'Outlook'} account.")
        return None, None

    driver.quit()

