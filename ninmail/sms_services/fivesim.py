import logging
import re
import time
import random
import requests

PREFIXES = {
        "cameroon":"1",
        "hongkong":"2",
        "mexico":"3",
        }
COUNTRY = ["cameroon",
        "hongkong",
        "mexico"]
class APIError(Exception):
    pass

class FiveSim:
    """
    This class provides functionalities to interact with the 5Sim API to obtain phone numbers and SMS verification codes.

    Attributes:
        token (str): Your 5Sim api key.
        service (str): 5Sim service name.
        country (str, optional): The country name for the phone number. Defaults to 'lithuania'.

    Methods:
        request(kwargs): Sends a GET request to the 5Sim API with the provided arguments.
        get_phone(send_prefix=False): Purchases a phone number from the 5Sim API.
            - send_prefix (bool, optional): Specifies whether to return the phone number with or without the prefix. Defaults to False.
        get_code(phone): Retrieves the SMS verification code sent to the provided phone number.

    Exceptions:
        APIError: Raised when an error occurs while interacting with the 5Sim API.
    """

    _last_phone = None
    code_patt = re.compile(r"([0-9]{5,6})")

    def __init__(
            self,
            service,
            token,
            country=COUNTRY,
            ):
        self.token = token
        self.service = service
        self.country = random.choice(country)
        self.prefix = PREFIXES.get(self.country) or ''
        self.API_URL = "https://5sim.net/v1/user/"

    def request(self, cmd):
        """
        Sends a GET request to the 5Sim API with the provided arguments.

        Args:
            kwargs (dict): Additional arguments to be included in the request body.

        Returns:
            str: The API response text.

        Raises:
            APIError: If the API returns an error message.
        """
        headers = {
                'Authorization': 'Bearer ' + self.token,
                } 

        res = requests.get(
                self.API_URL + cmd,
                headers=headers,
                )
        try:
            res.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise APIError(str(err))

        if res.text == "no free phones":
            raise APIError('5Sim has no free phones')
        if res.text == "not enough user balance":
            raise APIError("Not enough balance")

        return res.json()

    def get_cancel(self, id, send_prefix=False):
        """
        取消订单
        
        Args:
            id: 订单ID
            send_prefix: 是否返回前缀
            
        Returns:
            str: 订单状态
        """
        logging.info("取消订单")
        cmd = 'cancel/' + id
        data = self.request(cmd=cmd)
        self._last_phone = data
        status = data['status'] 
        logging.info("订单状态: %s", status)
        return status

    def get_phone(self, send_prefix=False, max_attempts=3):
        """
        获取手机号，失败时尝试更换国家
        
        Args:
            send_prefix: 是否返回前缀
            max_attempts: 最大尝试次数
            
        Returns:
            tuple: (手机号, 订单ID)
            
        Raises:
            APIError: 获取失败时抛出异常
        """
        attempt = 0
        while attempt < max_attempts:
            try:
                logging.info(f"尝试获取手机号 (第{attempt + 1}次)")
                cmd = 'buy/activation/' + self.country + '/any/' + self.service
                data = self.request(cmd=cmd)

                self._last_phone = data
                phone_number = data['phone'] 
                phone_number = phone_number.removeprefix('+')
                order_id = data['id']

                logging.info("成功获取手机号: %s", phone_number)

                if not send_prefix:
                    phone_number = phone_number.removeprefix('1')
                return phone_number, order_id
                
            except APIError as e:
                attempt += 1
                if attempt >= max_attempts:
                    logging.error(f"获取手机号失败，已达到最大尝试次数: {str(e)}")
                    raise
                    
                logging.warning(f"获取手机号失败，尝试更换国家 (第{attempt}次)")
                # 更换国家
                self.country = random.choice([c for c in COUNTRY if c != self.country])
                self.prefix = PREFIXES.get(self.country) or ''
                time.sleep(2)  # 等待一下再重试

    def get_code(self, order_id, max_attempts=3):
        """
        获取验证码，失败时重新获取手机号
        
        Args:
            order_id: 订单ID
            max_attempts: 最大尝试次数
            
        Returns:
            str: 验证码
            
        Raises:
            APIError: 获取失败时抛出异常
        """
        attempt = 0
        while attempt < max_attempts:
            try:
                logging.info(f"尝试获取验证码 (第{attempt + 1}次)")
                cmd = '/check/' + str(order_id)
                received = False
                
                while not received:
                    res = self.request(cmd=cmd)
                    if res['sms']:
                        received = True
                    elif res['status'] in ['CANCELED', 'TIMEOUT', 'BANNED']:
                        raise APIError('获取验证码失败，订单状态: %s' % res['status'])
                    else:
                        logging.info("等待验证码...")
                        time.sleep(10)

                sms = res['sms']
                code = sms[0]['code']

                logging.info("成功获取验证码: %s", code)
                return code
                
            except APIError as e:
                attempt += 1
                if attempt >= max_attempts:
                    logging.error(f"获取验证码失败，已达到最大尝试次数: {str(e)}")
                    raise
                    
                logging.warning(f"获取验证码失败，尝试重新获取手机号 (第{attempt}次)")
                # 取消当前订单
                try:
                    self.get_cancel(str(order_id))
                except:
                    pass
                    
                # 重新获取手机号
                phone, new_order_id = self.get_phone(send_prefix=True)
                order_id = new_order_id
                time.sleep(2)  # 等待一下再重试

