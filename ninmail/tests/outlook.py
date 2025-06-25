from ..ninjemail_manager import Ninjemail
import pytest

@pytest.fixture(autouse=True)
def test_create_outlook_account():
    # Replace "YOUR_API_KEY", "USERNAME" and "TOKEN" with your actual keys
    ninja = Ninjemail(
        		browser="undetected-chrome",
        		captcha_keys={"capsolver": "CAP-909B35A72505BB24D8EADAD5DDFA3234"},
        		sms_keys={"5sim": {"token": "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzQyODI3MzIsImlhdCI6MTc0Mjc0NjczMiwicmF5IjoiZmE5ZTE5NjhhZjBkYWIzMzMyNWU1NDEwNzUwYWQ4OGYiLCJzdWIiOjMxMDkwODN9.DjPMLsqvAR4RoW0e-DyC9eKJjENt4wwhC7FCItzk7e-tyCOVGxZ-oKyDzrFEUDFHomjcSM2Uy9G53_AlAg8XTYsCYZ3PvoX_Kewol494i-47Z2MMFf9kG6fdXzRP3IVTW7AjOBMryU96FtYph4cdQTmCq4dheu9rcyR-B7AWrRHauta0ub1IBSOi8-kKIWmYXCi9kOLZYGy-R0mN05txtQa-KccCVekzjGzUGJsIXOhhN_it7_z3NByNeafYOB8nCnKT2WLWJ5sTLkx7ppS4myQvd3XNG2Vn9lxpJT_tmHiDVNHGzlSp53zVCbyG2deuQ9v6Yjl8Llv4NH5tH9QzOA"}},
    			auto_proxy=True)
    email, password = ninja.create_outlook_account(
        					username="qonep001", 
        					password="12a34b5678c", 
        					first_name="John", 
        					last_name="Doe", 
        					country="USA", 
        					birthdate="01-01-2020"
    )

    print(f"Email: {email}")
    print(f"Password: {password}")
