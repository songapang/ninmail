import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from sms_services import get_sms_instance

URL = 'https://accounts.google.com/signup'
WAIT = 5
NEXT_BUTTON_XPATH = [
        "//span[contains(text(), 'Next')]",
        "//span[contains(text(),'I agree')]",
        "//div[contains(text(),'I agree')]"
        "//button[@class='VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-k8QpJ VfPpkd-LgbsSe-OWXEXe-dgl2Hf nCP5yc AjY5Oe DuMIQc LQeN7 qIypjc TrZEUc lw1w4b']",
        "//button[contains(text(),'Next')]",
        "//button[contains(text(),'I agree')]",
        "//div[@class='VfPpkd-RLmnJb']",
        ]

def next_button(driver):
    for selector in NEXT_BUTTON_XPATH:
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, selector))).click()
            break
        except:
            pass

def create_account(driver, 
                   sms_key,
                   username, 
                   password, 
                   first_name, 
                   last_name,
                   month,
                   day,
                   year):
    """
    Automatically creates a Gmail  account.

    Args:
        driver (WebDriver): The Selenium WebDriver instance for the configured browser.
        sms_key(dict): The data of the SMS service.
        username (str): The desired username for the email account.
        password (str): The desired password for the email account.
        first_name (str): The first name for the account holder.
        last_name (str): The last name for the account holder.
        month (str): The birth month for the account holder.
        day (str): The birth day for the account holder.
        year (str): The birth year for the account holder.

    Returns:
        tuple: Email and password of the created account.

    """
    SMS_SERVICE = sms_key['name']
    sms_provider = get_sms_instance(sms_key, 'google')

    logging.info('Creating Gmail account')

    driver.get(URL)
    driver.implicitly_wait(2)

    # insert first and last name
    name_input = WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, 'firstName')))
    name_input.send_keys(first_name)
    time.sleep(1)
    lastname_input = WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, 'lastName')))
    lastname_input.send_keys(last_name)
    time.sleep(1)
    next_button(driver)

    # select birthdate
    time.sleep(10)
    month_combobox = Select(WebDriverWait(driver, WAIT).until(EC.element_to_be_clickable((By.ID, 'month'))))
    # month_combobox.select_by_index(int(month))
    month_combobox.select_by_visible_text(month)
    # driver.find_element(By.XPATH, f'//*[@id="month"]/option[{month}]').click() alternative

    day_input = WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.XPATH, '//input[@name="day"]')))
    driver.execute_script("arguments[0].scrollIntoView();", day_input)
    driver.execute_script("arguments[0].setAttribute('value', arguments[1]);", day_input, int(day))

    year_input = WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, 'year')))
    driver.execute_script("arguments[0].scrollIntoView();", year_input)
    driver.execute_script("arguments[0].setAttribute('value', arguments[1]);", year_input, year)

    # gender
    gender_combobox = Select(WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, 'gender'))))
    gender_combobox.select_by_index(3)
    next_button(driver)

    # select how to define username
    try:
        create_input = WebDriverWait(driver, WAIT).until(EC.element_to_be_clickable((By.ID, 'selectionc4')))
        create_input.click()
    except:
        pass

    # insert username
    
    # WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.XPATH, "//span[text()='Create your own Gmail address']"))).click()
    try:
        exist = WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, 'selectionc3')))
        exist.click()
        print("true")
    except:
        print("false")
    time.sleep(5)
    username_input = WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.NAME, 'Username')))
    username_input.send_keys(username)
    next_button(driver)

    # insert Password
    password_input = WebDriverWait(driver, WAIT).until(EC.element_to_be_clickable((By.NAME, 'Passwd')))
    password_input.send_keys(password)
    time.sleep(3)
    password_confirm_input = WebDriverWait(driver, WAIT).until(EC.element_to_be_clickable((By.NAME, 'PasswdAgain')))
    password_confirm_input.send_keys(password)
    time.sleep(3)
    next_button(driver)

    try:
        element = WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Sorry, we could not create your Google Account.')]")))
        if element and isinstance(element, WebElement):
            logging.error("Error from Google, message: 'Sorry, we could not create your Google Account.'.")
            driver.quit()
            return None, None
    except:
        pass

    def wait_for_element(driver, by, value, timeout=WAIT, condition=EC.presence_of_element_located):
        """
        等待元素出现并返回
        
        Args:
            driver: WebDriver实例
            by: 定位方式
            value: 定位值
            timeout: 超时时间
            condition: 等待条件
            
        Returns:
            WebElement: 找到的元素
        """
        try:
            element = WebDriverWait(driver, timeout).until(
                condition((by, value))
            )
            return element
        except Exception as e:
            logging.error(f"等待元素失败: {by}={value}, 错误: {str(e)}")
            return None

    def safe_click(driver, element):
        """
        安全点击元素
        
        Args:
            driver: WebDriver实例
            element: 要点击的元素
            
        Returns:
            bool: 是否点击成功
        """
        try:
            # 确保元素可见和可点击
            WebDriverWait(driver, WAIT).until(
                EC.element_to_be_clickable((By.ID, element.get_attribute("id")))
            )
            # 使用JavaScript点击
            driver.execute_script("arguments[0].click();", element)
            return True
        except Exception as e:
            logging.error(f"点击元素失败: {str(e)}")
            return False

    def handle_phone_verification(driver, sms_provider, SMS_SERVICE):
        """
        处理手机号验证流程
        """
        try:
            # 获取手机号
            if SMS_SERVICE == 'getsmscode':
                phone = sms_provider.get_phone(send_prefix=True)
                order_id = None
            elif SMS_SERVICE in ['smspool', '5sim']:
                phone, order_id = sms_provider.get_phone(send_prefix=True)
            else:
                logging.error(f"不支持的SMS服务: {SMS_SERVICE}")
                return None

            # 等待页面加载完成
            time.sleep(5)
            
            # 确保页面已完全加载
            driver.execute_script("return document.readyState") == "complete"
            
            # 输入手机号
            phone_input = wait_for_element(driver, By.ID, "phoneNumberId", condition=EC.element_to_be_clickable)
            if not phone_input:
                raise Exception("无法找到手机号输入框")
                
            # 清除输入框
            phone_input.clear()
            time.sleep(1)
            
            # 输入手机号
            phone_input.send_keys('+' + str(phone))
            time.sleep(1)
            
            # 点击next按钮
            if not safe_next_button(driver):
                raise Exception("点击next按钮失败")
            
            # 等待页面响应
            time.sleep(5)
            
            return phone, order_id
            
        except Exception as e:
            logging.error('输入手机号失败: %s', str(e))
            raise

    def handle_phone_rejection(driver, sms_provider, order_id):
        """
        处理手机号被拒绝的情况
        """
        try:
            # 取消当前订单
            status = sms_provider.get_cancel(str(order_id))
            logging.info(f"取消订单状态: {status}")
            
            # 获取新手机号
            phone, new_order_id = sms_provider.get_phone(send_prefix=True)
            
            # 等待页面加载
            time.sleep(3)
            
            # 清除并重新输入手机号
            phone_input = wait_for_element(driver, By.ID, "phoneNumberId", condition=EC.element_to_be_clickable)
            if not phone_input:
                raise Exception("无法找到手机号输入框")
                
            # 清除输入框
            phone_input.clear()
            time.sleep(1)
            
            # 输入新手机号
            phone_input.send_keys('+' + str(phone))
            time.sleep(1)
            
            # 点击next按钮
            if not safe_next_button(driver):
                raise Exception("点击next按钮失败")
            
            # 等待页面响应
            time.sleep(5)
            
            logging.warning("手机号被拒绝，已尝试新号码")
            return phone, new_order_id
            
        except Exception as e:
            logging.error('处理手机号拒绝失败: %s', str(e))
            return None

    def check_page_state(driver):
        """
        检查页面状态
        
        Returns:
            bool: 页面是否正常
        """
        try:
            # 检查页面是否完全加载
            if driver.execute_script("return document.readyState") != "complete":
                return False
                
            # 检查是否有错误页面
            if "error" in driver.current_url.lower():
                return False
                
            # 检查页面标题
            if "google" not in driver.title.lower():
                return False
                
            return True
        except Exception as e:
            logging.error(f"检查页面状态失败: {str(e)}")
            return False

    def check_google_error(driver):
        """
        检查Google返回的错误信息
        
        Args:
            driver: WebDriver实例
            
        Returns:
            bool: 是否存在错误
        """
        try:
            # 检查通用错误消息
            error_element = WebDriverWait(driver, WAIT).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Sorry, we could not create your Google Account.')]"))
            )
            if error_element and isinstance(error_element, WebElement):
                logging.error("Google返回错误: 'Sorry, we could not create your Google Account.'")
                return True
                
            # 检查特定错误消息
            specific_error = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[1]/div[2]/div/div/div[2]/div/div/div[1]/form/span/section/div/div/div[2]/div/div[2]/div[2]/div'))
            )
            if specific_error and isinstance(specific_error, WebElement):
                logging.error(f"Google返回特定错误: {specific_error.text}")
                return True
                
            return False
            
        except:
            return False

    def check_phone_warnings(driver):
        """
        检查手机号相关的警告信息
        
        Args:
            driver: WebDriver实例
            
        Returns:
            str: 警告类型，如果没有警告则返回None
        """
        try:
            # 检查各种可能的警告信息
            warning_messages = {
                'verification': "//div[text()='This phone number cannot be used for verification.']",
                'too_many_times': "//div[text()='This phone number has been used too many times']",
                'invalid': "//div[contains(text(), 'This phone number is invalid')]",
                'unavailable': "//div[contains(text(), 'This phone number is unavailable')]"
            }
            
            for warning_type, xpath in warning_messages.items():
                try:
                    WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    logging.warning(f"检测到手机号警告: {warning_type}")
                    return warning_type
                except:
                    continue
                    
            return None
            
        except Exception as e:
            logging.error(f"检查手机号警告时发生错误: {str(e)}")
            return None

    def safe_input_password(driver, password):
        """
        安全输入密码
        
        Args:
            driver: WebDriver实例
            password: 密码字符串
            
        Returns:
            bool: 是否输入成功
        """
        try:
            # 等待密码输入框出现
            password_input = wait_for_element(driver, By.NAME, 'Passwd', condition=EC.element_to_be_clickable)
            if not password_input:
                raise Exception("无法找到密码输入框")
            
            # 清除输入框
            password_input.clear()
            time.sleep(1)
            
            # 输入密码
            password_input.send_keys(password)
            time.sleep(2)
            
            # 等待确认密码输入框
            password_confirm = wait_for_element(driver, By.NAME, 'PasswdAgain', condition=EC.element_to_be_clickable)
            if not password_confirm:
                raise Exception("无法找到确认密码输入框")
            
            # 清除确认密码输入框
            password_confirm.clear()
            time.sleep(1)
            
            # 输入确认密码
            password_confirm.send_keys(password)
            time.sleep(2)
            
            return True
            
        except Exception as e:
            logging.error(f"输入密码失败: {str(e)}")
            return False

    def safe_next_button(driver):
        """
        安全点击next按钮
        
        Args:
            driver: WebDriver实例
            
        Returns:
            bool: 是否点击成功
        """
        try:
            # 等待页面加载完成
            time.sleep(3)
            
            # 检查页面状态
            if not check_page_state(driver):
                logging.error("点击next按钮前页面状态异常")
                return False
            
            # 尝试多种方式点击next按钮
            next_button_selectors = [
                "//span[contains(text(), 'Next')]",
                "//span[contains(text(),'I agree')]",
                "//span[contains(text(),'Skip')]",
                "//div[contains(text(),'I agree')]",
                "//button[@class='VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-k8QpJ VfPpkd-LgbsSe-OWXEXe-dgl2Hf nCP5yc AjY5Oe DuMIQc LQeN7 qIypjc TrZEUc lw1w4b']",
                "//button[contains(text(),'Next')]",
                "//button[contains(text(),'I agree')]",
                "//div[contains(text(),'Skip')]",
                "//div[@class='VfPpkd-RLmnJb']"
            ]
            
            for selector in next_button_selectors:
                try:
                    # 等待按钮可点击
                    button = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    
                    # 确保按钮在视图中
                    driver.execute_script("arguments[0].scrollIntoView(true);", button)
                    time.sleep(1)
                    
                    # 使用JavaScript点击
                    driver.execute_script("arguments[0].click();", button)
                    
                    # 等待页面响应
                    time.sleep(3)
                    
                    # 检查是否点击成功
                    if check_page_state(driver):
                        logging.info("成功点击next按钮")
                        return True
                        
                except Exception as e:
                    logging.debug(f"尝试点击按钮 {selector} 失败: {str(e)}")
                    continue
            
            logging.error("所有next按钮点击尝试都失败")
            return False
            
        except Exception as e:
            logging.error(f"点击next按钮时发生错误: {str(e)}")
            return False

    def check_password_error(driver):
        """
        检查密码相关错误
        
        Args:
            driver: WebDriver实例
            
        Returns:
            bool: 是否存在错误
        """
        try:
            error_messages = [
                "//div[contains(text(), 'Password is too short')]",
                "//div[contains(text(), 'Password is too common')]",
                "//div[contains(text(), 'Passwords do not match')]",
                "//div[contains(text(), 'Password cannot be your email')]"
            ]
            
            for xpath in error_messages:
                try:
                    error_element = WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    if error_element:
                        logging.error(f"密码错误: {error_element.text}")
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            logging.error(f"检查密码错误时发生错误: {str(e)}")
            return False

    # 执行手机号验证流程
    try:
        # 检查页面状态
        if not check_page_state(driver):
            logging.error("页面状态异常")
            driver.quit()
            return None, None

        # 获取并输入手机号
        phone, order_id = handle_phone_verification(driver, sms_provider, SMS_SERVICE)
        if not phone:
            driver.quit()
            return None, None

        # 处理手机号被拒绝的情况
        max_attempts = 3
        attempt = 0
        while attempt < max_attempts:
            try:
                # 等待页面加载
                time.sleep(5)
                
                # 检查页面状态
                if not check_page_state(driver):
                    logging.error("页面状态异常")
                    break
                
                # 检查警告信息
                warning_type = check_phone_warnings(driver)
                
                if warning_type:
                    logging.info(f"尝试处理警告类型: {warning_type}")
                    result = handle_phone_rejection(driver, sms_provider, order_id)
                    if not result:
                        logging.error("处理手机号拒绝失败")
                        driver.quit()
                        return None, None
                    phone, order_id = result
                    attempt += 1
                    logging.info(f"第 {attempt} 次尝试新手机号")
                else:
                    logging.info("未检测到警告，继续验证流程")
                    break
                    
            except Exception as e:
                logging.error(f"处理手机号验证时发生错误: {str(e)}")
                break

        if attempt >= max_attempts:
            logging.error(f"达到最大尝试次数 ({max_attempts})，验证失败")
            driver.quit()
            return None, None

        # 检查Google错误
        if check_google_error(driver):
            driver.quit()
            return None, None

    except Exception as e:
        logging.error('手机号验证过程失败: %s', str(e))
        driver.quit()
        return None, None

    # sms verification
    try:
        max_sms_attempts = 3
        sms_attempt = 0
        while sms_attempt < max_sms_attempts:
            try:
                logging.info(f"尝试获取短信验证码 (第{sms_attempt + 1}次)")
                if SMS_SERVICE == 'getsmscode':
                    code = sms_provider.get_code(phone)
                elif SMS_SERVICE == 'smspool' or SMS_SERVICE == '5sim':
                    code = sms_provider.get_code(order_id)
                
                # 输入验证码
                code_input = wait_for_element(driver, By.ID, "code", condition=EC.element_to_be_clickable)
                if not code_input:
                    raise Exception("无法找到验证码输入框")
                    
                code_input.clear()
                time.sleep(1)
                code_input.send_keys(str(code))
                time.sleep(1)
                
                # 点击验证按钮
                # 点击next按钮
                if not safe_next_button(driver):
                    raise Exception("点击next按钮失败")
                time.sleep(3)
                
                # 检查验证是否成功
                try:
                    if not safe_next_button(driver):
                        raise Exception("点击Skip按钮失败")
                        break
                except:
                    logging.warning("验证码验证可能失败，继续尝试")
                    sms_attempt += 1
                    if sms_attempt >= max_sms_attempts:
                        raise Exception("验证码验证失败，已达到最大尝试次数")
                    time.sleep(2)
                    
            except Exception as e:
                logging.error(f"获取或输入验证码失败: {str(e)}")
                sms_attempt += 1
                if sms_attempt >= max_sms_attempts:
                    raise
                time.sleep(2)
                
    except Exception as e:
        logging.error('短信验证失败: %s', str(e))
        driver.quit()
        return None, None

    time.sleep(5)
    driver.find_elements(By.TAG_NAME, "button")[-1].click()
    # phone recovery (skip)
    next_button(driver)
    time.sleep(5)

    # final step
    next_button(driver)
    time.sleep(5)
    next_button(driver)
    time.sleep(5)
    next_button(driver)

    # log and return results
    logging.info("Verification complete.")
    logging.info("IF YOU ACCESS THIS ACCOUNT IMMEDIATELY FROM A DIFFERENT IP IT WILL BE BANNED")

    logging.info('Gmail email account created successfully.')
    logging.info("Account Details:")
    logging.info(f"Email:      {username}@gmail.com")
    logging.info(f"Password:      {password}")
    logging.info(f"First Name:    {first_name}")
    logging.info(f"Last Name:     {last_name}")
    logging.info(f"Date of Birth: {month}/{day}/{year}")
    driver.quit()
    return f"{username}@gmail.com", password
