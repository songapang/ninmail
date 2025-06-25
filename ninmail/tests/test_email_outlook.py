import pytest
from unittest.mock import Mock, MagicMock
from selenium.webdriver.common.keys import Keys
from ..email_providers.outlook import create_account
from ..utils.webdriver_utils import create_driver

@pytest.fixture(autouse=True)
def mock_outlook(monkeypatch):
    # Mock GeckoDriverManager and ChromeDriverManager installations
    monkeypatch.setattr('webdriver_manager.firefox.GeckoDriverManager.install', lambda *args, **kwargs: 'gecko_driver_path')
    monkeypatch.setattr('webdriver_manager.chrome.ChromeDriverManager.install', lambda *args, **kwargs: 'chrome_driver_path')

    # Mock WebDriver classes
    mock_firefox = Mock()
    mock_chrome = Mock()
    monkeypatch.setattr('selenium.webdriver.Firefox', lambda *args, **kwargs: mock_firefox)
    monkeypatch.setattr('selenium.webdriver.Chrome', lambda *args, **kwargs: mock_chrome)

    # Mock WebDriver methods
    mock_firefox.get = MagicMock()
    mock_chrome.get = MagicMock()
    mock_firefox.find_element = MagicMock(return_value=Mock())
    mock_chrome.find_element = MagicMock(return_value=Mock())
    mock_firefox.find_elements = MagicMock(return_value=[Mock()])
    mock_chrome.find_elements = MagicMock(return_value=[Mock()])
    mock_firefox.quit = MagicMock()
    mock_chrome.quit = MagicMock()

    # Mock WebDriverWait and expected_conditions
    mock_wait = MagicMock()
    monkeypatch.setattr('selenium.webdriver.support.ui.WebDriverWait', lambda *args, **kwargs: mock_wait)
    mock_wait.until = MagicMock(return_value=Mock())
    monkeypatch.setattr('selenium.webdriver.support.expected_conditions.presence_of_element_located', lambda *args, **kwargs: MagicMock())
    monkeypatch.setattr('selenium.webdriver.support.expected_conditions.element_to_be_clickable', lambda *args, **kwargs: MagicMock())
    monkeypatch.setattr('selenium.webdriver.support.expected_conditions.visibility_of_element_located', lambda *args, **kwargs: MagicMock())
    monkeypatch.setattr('selenium.webdriver.support.expected_conditions.frame_to_be_available_and_switch_to_it', lambda *args, **kwargs: MagicMock())

    # Correctly mock Select class
    def mock_select_init(self, *args, **kwargs):
        self.select_by_index = MagicMock()
        self.select_by_visible_text = MagicMock()
        self.select_by_value = MagicMock()

    monkeypatch.setattr('selenium.webdriver.support.ui.Select.__init__', mock_select_init)

    # Mock Keys
    monkeypatch.setattr('selenium.webdriver.common.keys.Keys', Keys)

    # Mock time
    monkeypatch.setattr('time.sleep', MagicMock(()))

    # Mock logging
    monkeypatch.setattr('logging.info', MagicMock())
    monkeypatch.setattr('logging.error', MagicMock())

# Mock sms services
def mock_get_phone_getsmscode(self, *args, **kwargs):
    return '111111111'

def mock_get_phone_smspool(self, *args, **kwargs):
    return 'ordeid', '111111111'

def mock_get_code(self, *arg, **kwargs):
    return '000000'

def mock_get_phone_fail(self, *args, **kwargs):
    raise Exception("Failed to get phone number")

def mock_get_code_fail(self, *args, **kwargs):
    raise Exception("Failed to retreive code")

def test_create_account_firefox():

    driver = create_driver('firefox')
    # Test data
    username = "testuser"
    password = "testpassword"
    first_name = "John"
    last_name = "Doe"
    country = "us"
    month = "1"
    day = "1"
    year = "2000"
    hotmail = False

    email, password = create_account(driver, username, password, first_name, last_name, country, month, day, year, hotmail)
    assert email == f"{username}@outlook.com"
    assert password == "testpassword"

def test_create_account_chrome():

    driver = create_driver('chrome')
    # Test data
    username = "testuser"
    password = "testpassword"
    first_name = "John"
    last_name = "Doe"
    country="us"
    month = "1"
    day = "1"
    year = "2000"
    hotmail = False

    email, password = create_account(driver, username, password, first_name, last_name, country, month, day, year, hotmail)
    assert email == f"{username}@outlook.com"
    assert password == "testpassword"

def test_create_hotmail_account():

    driver = create_driver('chrome')
    # Test data
    
    username = "testuser"
    password = "testpassword"
    first_name = "John"
    last_name = "Doe"
    country = "us"
    month = "1"
    day = "1"
    year = "2000"
    hotmail = True

    email, password = create_account(driver, username, password, first_name, last_name, country, month, day, year, hotmail)
    assert email == f"{username}@hotmail.com"
    assert password == "testpassword"

