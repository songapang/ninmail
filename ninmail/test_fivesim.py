import logging
from sms_services.fivesim import FiveSim

# 配置日志
logging.basicConfig(level=logging.INFO)

def test_get_phone():
    # 请替换为您的实际API token
    token = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzQyODI3MzIsImlhdCI6MTc0Mjc0NjczMiwicmF5IjoiZmE5ZTE5NjhhZjBkYWIzMzMyNWU1NDEwNzUwYWQ4OGYiLCJzdWIiOjMxMDkwODN9.DjPMLsqvAR4RoW0e-DyC9eKJjENt4wwhC7FCItzk7e-tyCOVGxZ-oKyDzrFEUDFHomjcSM2Uy9G53_AlAg8XTYsCYZ3PvoX_Kewol494i-47Z2MMFf9kG6fdXzRP3IVTW7AjOBMryU96FtYph4cdQTmCq4dheu9rcyR-B7AWrRHauta0ub1IBSOi8-kKIWmYXCi9kOLZYGy-R0mN05txtQa-KccCVekzjGzUGJsIXOhhN_it7_z3NByNeafYOB8nCnKT2WLWJ5sTLkx7ppS4myQvd3XNG2Vn9lxpJT_tmHiDVNHGzlSp53zVCbyG2deuQ9v6Yjl8Llv4NH5tH9QzOA"
    service = "google"  # 或其他您想测试的服务
    
    # 创建FiveSim实例
    fivesim = FiveSim(
        service=service,
        token=token,
        country='hongkong'
    )
    
    try:
        # 测试获取手机号
        phone_number, order_id = fivesim.get_phone(send_prefix=False)
        print(f"获取到的手机号: {phone_number}")
        print(f"订单ID: {order_id}")
        return order_id
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return None

def test_get_cancel(order_id):
    token = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzQyODI3MzIsImlhdCI6MTc0Mjc0NjczMiwicmF5IjoiZmE5ZTE5NjhhZjBkYWIzMzMyNWU1NDEwNzUwYWQ4OGYiLCJzdWIiOjMxMDkwODN9.DjPMLsqvAR4RoW0e-DyC9eKJjENt4wwhC7FCItzk7e-tyCOVGxZ-oKyDzrFEUDFHomjcSM2Uy9G53_AlAg8XTYsCYZ3PvoX_Kewol494i-47Z2MMFf9kG6fdXzRP3IVTW7AjOBMryU96FtYph4cdQTmCq4dheu9rcyR-B7AWrRHauta0ub1IBSOi8-kKIWmYXCi9kOLZYGy-R0mN05txtQa-KccCVekzjGzUGJsIXOhhN_it7_z3NByNeafYOB8nCnKT2WLWJ5sTLkx7ppS4myQvd3XNG2Vn9lxpJT_tmHiDVNHGzlSp53zVCbyG2deuQ9v6Yjl8Llv4NH5tH9QzOA"
    service = "google"
    
    fivesim = FiveSim(
        service=service,
        token=token,
        country='hongkong'
    )
    
    try:
        # 测试取消订单
        status = fivesim.get_cancel(order_id)
        print(f"取消订单状态: {status}")
    except Exception as e:
        print(f"取消订单时发生错误: {str(e)}")

if __name__ == "__main__":
    # 先获取一个订单ID
    order_id = test_get_phone()
    if order_id:
        # 然后尝试取消这个订单
        id = str(order_id)
        test_get_cancel(id) 