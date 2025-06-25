import logging
import json
import argparse
from ninjemail_manager import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sms_services.fivesim import *
import undetected_chromedriver as uc

def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def load_config(config_path='config.json'):
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"配置文件 {config_path} 未找到")
        return None
    
def main():
    # Replace "YOUR_API_KEY", "USERNAME" and "TOKEN" with your actual keys
    ninja = Ninjemail(
        		browser="undetected-chrome",
        		captcha_keys={"nopecha": "I-H7AG500SGFEN"},
        		sms_keys={"5sim": {"token": "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzQyODI3MzIsImlhdCI6MTc0Mjc0NjczMiwicmF5IjoiZmE5ZTE5NjhhZjBkYWIzMzMyNWU1NDEwNzUwYWQ4OGYiLCJzdWIiOjMxMDkwODN9.DjPMLsqvAR4RoW0e-DyC9eKJjENt4wwhC7FCItzk7e-tyCOVGxZ-oKyDzrFEUDFHomjcSM2Uy9G53_AlAg8XTYsCYZ3PvoX_Kewol494i-47Z2MMFf9kG6fdXzRP3IVTW7AjOBMryU96FtYph4cdQTmCq4dheu9rcyR-B7AWrRHauta0ub1IBSOi8-kKIWmYXCi9kOLZYGy-R0mN05txtQa-KccCVekzjGzUGJsIXOhhN_it7_z3NByNeafYOB8nCnKT2WLWJ5sTLkx7ppS4myQvd3XNG2Vn9lxpJT_tmHiDVNHGzlSp53zVCbyG2deuQ9v6Yjl8Llv4NH5tH9QzOA"}},
    			auto_proxy=True)
    email, password = ninja.create_outlook_account(
    		username="qonep0002", 
    		password="12a34b5678c", 
    		first_name="Joe", 
    		last_name="Sean", 
    		country="United States", 
            # country="China", 
    		birthdate="October-1-1996", 
    		hotmail=False,
    		use_proxy=True
    )
    # email, password = ninja.create_gmail_account(
    #         username="qonep006", 
    #     	password="12a34b5678c", 
    #     	first_name="Johns", 
    #     	last_name="Does", 
    #     	birthdate="October-1-2000",
    # 		use_proxy=False
    # )

    print(f"Email: {email}")
    print(f"Password: {password}")
    
if __name__ == "__main__":
    main()