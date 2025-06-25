from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import os
from urllib.parse import urlparse
import re
import time

def add_capsolver_api_key(file_path, api_key):
    with open(file_path, 'r') as file:
        content = file.read()

    updated_content = re.sub(r'apiKey:\s*\'[^\']*\'', f'apiKey: \'{api_key}\'', content)

    with open(file_path, 'w', encoding='utf-8',newline='\n') as file:
        file.write(updated_content)

def create_backgroundjs(host, port, username, password):
    return """
        var config = {
                mode: "fixed_servers",
                rules: {
                singleProxy: {
                    scheme: "http",
                    host: "%s",
                    port: parseInt(%s)
                },
                bypassList: ["localhost"]
                }
            };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """ % (host, port, username, password)

def create_background_file(background_js):
    folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'proxy_auth_ext')
    file_path = os.path.join(folder_path, 'background.js')

    os.makedirs(folder_path, exist_ok=True)

    with open(file_path, 'w') as file:
        file.write(background_js)

    return folder_path

def create_driver(browser, captcha_extension=False, proxy=None, captcha_key={}):
    """
    Create a WebDriver instance for the specified browser with optional configurations.

    Parameters:
        browser (str): The name of the browser to use. Currently supports 'firefox' and 'chrome'.
        captcha_extension (bool, optional): Whether to enable a captcha solving extension (default is False).
        proxy (str, optional): Proxy server address in the format 'http://<ip_address>:<port>' or 'socks5://<ip_address>:<port>'.
        captcha_key (dict, optional): Dict containing the name and api key for the captcha solving service to use.
    
    Returns:
        WebDriver: An instance of WebDriver configured based on the provided parameters.

    Raises:
        ValueError: If an unsupported browser is specified.

    Example:
        To create a headless Firefox driver:
        >>> driver = create_driver('firefox')

        To create a headless Chrome driver with a proxy and captcha solving extension:
        >>> driver = create_driver('chrome', captcha_extension=True, proxy='http://127.0.0.1:8080')
    """
    if proxy:
        parsed_url = urlparse(proxy)

        ip_address = parsed_url.hostname
        port = parsed_url.port
        username = parsed_url.username
        password = parsed_url.password

    if browser == 'firefox':
        custom_profile = FirefoxProfile()
        custom_profile.set_preference("extensions.ui.developer_mode", True)

        options = FirefoxOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--headless')
        custom_profile.set_preference("intl.accept_languages", "en-us")

        # proxy
        if proxy:
            options.set_preference("network.proxy.type", 1)
            options.set_preference("network.proxy.http", ip_address)
            options.set_preference("network.proxy.http_port", port)
            options.set_preference('network.proxy.socks', ip_address)
            options.set_preference('network.proxy.socks_port', port)
            options.set_preference('network.proxy.socks_remote_dns', False)
            options.set_preference("network.proxy.ssl", ip_address)
            options.set_preference("network.proxy.ssl_port", port)

        options.profile = custom_profile

        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)

        if captcha_extension:
            if captcha_key.get('name', None) == 'capsolver':
                driver.install_addon(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'captcha_solvers/capsolver_captcha_solver-1.10.4.xpi'))
                driver.get('https://www.google.com')
                capsolver_src = driver.find_element(By.XPATH, '/html/script[2]')
                capsolver_src = capsolver_src.get_attribute('src')
                capsolver_ext_id = capsolver_src.split('/')[2]
                driver.get(f'moz-extension://{capsolver_ext_id}/www/index.html#/popup')
                time.sleep(5)
                
                api_key_input = driver.find_element(By.XPATH, '//input[@placeholder="Please input your API key"]')
                api_key_input.send_keys(captcha_key.get('key', None))
                driver.find_element(By.ID, 'q-app').click()
            elif captcha_key.get('name', None) == 'nopecha':
                driver.install_addon(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'captcha_solvers/noptcha-0.4.9.xpi'))
                driver.get(f"https://nopecha.com/setup#{captcha_key.get('key', None)}")

    elif browser == 'chrome':
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')
        
        if captcha_extension:
            captcha_extension_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'captcha_solver_ext')
            options.add_argument(f'--load-extension={captcha_extension_path}')
            
        driver = uc.Chrome(options=options)
        
        # 执行 JavaScript 来修改 navigator.webdriver
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        if captcha_key.get('name', None) == 'nopecha':
            driver.get(f"https://nopecha.com/setup#{captcha_key.get('key', None)}")

    elif browser == 'undetected-chrome':
        # 使用 undetected_chromedriver 的默认配置
        driver = uc.Chrome(
            driver_executable_path="C:\Program Files\Google\Chrome\Application\chromedriver.exe",
            browser_executable_path="C:\Program Files\Google\Chrome\Application\chrome.exe"
        )

        # 添加必要的选项
        driver.options.add_argument('--no-sandbox')
        driver.options.add_argument('--disable-dev-shm-usage')
        driver.options.add_argument('--disable-gpu')
        driver.options.add_argument('--disable-infobars')
        driver.options.add_argument('--disable-notifications')
        driver.options.add_argument('--disable-popup-blocking')
        driver.options.add_argument('--disable-blink-features=AutomationControlled')
        driver.options.add_experimental_option('excludeSwitches', ['enable-automation'])
        driver.options.add_experimental_option('useAutomationExtension', False)
        driver.options.add_experimental_option('prefs', {
            'intl.accept_languages': 'en-us',
            'profile.default_content_setting_values.notifications': 2,
            'profile.default_content_setting_values.geolocation': 2,
            'profile.default_content_setting_values.media_stream_mic': 2,
            'profile.default_content_setting_values.media_stream_camera': 2,
            'profile.default_content_setting_values.automatic_downloads': 1,
            'profile.default_content_setting_values.midi_sysex': 2,
            'profile.default_content_setting_values.push_messaging': 2,
            'profile.default_content_setting_values.ssl_cert_decisions': 2,
            'profile.default_content_setting_values.metro_switch_to_desktop': 2,
            'profile.default_content_setting_values.protected_media_identifier': 2,
            'profile.default_content_setting_values.site_engagement': 2,
            'profile.default_content_setting_values.durable_storage': 2
        })

        if proxy:
            if username and password:
                background_js = create_backgroundjs(ip_address, port, username, password)
                proxy_ext = create_background_file(background_js)
                if not captcha_extension:
                    driver.options.add_argument(f'--load-extension={proxy_ext}')
            else:
                driver.options.add_argument(f'--proxy-server={proxy}')

        if captcha_extension:
            if captcha_key.get('name', None) == 'capsolver':
                add_capsolver_api_key(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'captcha_solvers/capsolver-chrome-extension/assets/config.js'), captcha_key.get('key', None))
                ext_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'captcha_solvers/capsolver-chrome-extension/')
            elif captcha_key.get('name', None) == 'nopecha':
                ext_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'captcha_solvers/NopeCHA-CAPTCHA-Solver/')
            if proxy_ext:
                driver.options.add_argument(f'--load-extension={ext_path},{proxy_ext}')
            else:
                driver.options.add_argument(f'--load-extension={ext_path}')

        # 执行 JavaScript 来修改 navigator.webdriver 和其他属性
        driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
            Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
            Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});
            Object.defineProperty(navigator, 'maxTouchPoints', {get: () => 0});
            Object.defineProperty(navigator, 'userAgent', {get: () => 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'});
        """)

        # 添加更多的反检测措施
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                window.chrome = {runtime: {}};
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            '''
        })

        if captcha_key.get('name', None) == 'nopecha':
            driver.get(f"https://nopecha.com/setup#{captcha_key.get('key', None)}")
    else:
        raise ValueError('Unsupported browser')
    return driver
