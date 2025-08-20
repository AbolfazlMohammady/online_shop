import requests
import json
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from .models import Order
import logging

logger = logging.getLogger(__name__)

class ZarinPalPaymentGateway:
    """درگاه پرداخت زرین‌پال"""
    
    # URLs for different environments
    SANDBOX_URL = "https://sandbox.zarinpal.com"
    PRODUCTION_URL = "https://www.zarinpal.com"
    
    def __init__(self, merchant_id, sandbox=True):
        self.merchant_id = merchant_id
        self.sandbox = sandbox
        self.base_url = self.SANDBOX_URL if sandbox else self.PRODUCTION_URL
    
    def create_payment_request(self, order, callback_url):
        """
        ایجاد درخواست پرداخت
        
        Args:
            order: شیء سفارش
            callback_url: آدرس بازگشت بعد از پرداخت
            
        Returns:
            dict: نتیجه درخواست شامل success, authority, payment_url
        """
        try:
            # آماده‌سازی داده‌های درخواست
            payment_data = {
                "merchant_id": self.merchant_id,
                "amount": int(order.total_amount),  # مبلغ به تومان
                "description": f"پرداخت سفارش #{order.id} - {order.user.username}",
                "callback_url": callback_url,
                "mobile": order.receiver_phone,
                "email": order.user.email if hasattr(order.user, 'email') else "",
            }
            
            # ارسال درخواست به زرین‌پال
            response = requests.post(
                f"{self.base_url}/pg/rest/WebGate/PaymentRequest.json",
                json=payment_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('Status') == 100:
                    # موفقیت‌آمیز
                    authority = result.get('Authority')
                    
                    # بروزرسانی سفارش با شناسه مرجع
                    order.payment_authority = authority
                    order.save(update_fields=['payment_authority'])
                    
                    # ایجاد لینک پرداخت
                    payment_url = f"{self.base_url}/pg/StartPay/{authority}"
                    
                    logger.info(f"درخواست پرداخت موفق برای سفارش #{order.id} - Authority: {authority}")
                    
                    return {
                        'success': True,
                        'authority': authority,
                        'payment_url': payment_url,
                        'message': 'درخواست پرداخت با موفقیت ایجاد شد'
                    }
                else:
                    # خطا در ایجاد درخواست
                    error_message = result.get('Errors', {}).get('Message', 'خطا در ایجاد درخواست پرداخت')
                    logger.error(f"خطا در ایجاد درخواست پرداخت برای سفارش #{order.id}: {error_message}")
                    
                    return {
                        'success': False,
                        'message': error_message,
                        'error_code': result.get('Status')
                    }
            else:
                logger.error(f"خطا در ارتباط با زرین‌پال برای سفارش #{order.id}: HTTP {response.status_code}")
                return {
                    'success': False,
                    'message': 'خطا در ارتباط با درگاه پرداخت'
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"خطا در ارتباط با زرین‌پال برای سفارش #{order.id}: {str(e)}")
            return {
                'success': False,
                'message': 'خطا در ارتباط با درگاه پرداخت'
            }
        except Exception as e:
            logger.error(f"خطای غیرمنتظره در ایجاد درخواست پرداخت برای سفارش #{order.id}: {str(e)}")
            return {
                'success': False,
                'message': 'خطای غیرمنتظره در ایجاد درخواست پرداخت'
            }
    
    def verify_payment(self, authority, amount):
        """
        تایید پرداخت
        
        Args:
            authority: شناسه مرجع پرداخت
            amount: مبلغ پرداخت شده
            
        Returns:
            dict: نتیجه تایید شامل success, ref_id, status_code
        """
        try:
            # آماده‌سازی داده‌های تایید
            verification_data = {
                "merchant_id": self.merchant_id,
                "authority": authority,
                "amount": int(amount)
            }
            
            # ارسال درخواست تایید به زرین‌پال
            response = requests.post(
                f"{self.base_url}/pg/rest/WebGate/PaymentVerification.json",
                json=verification_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('Status') == 100:
                    # تایید موفق
                    ref_id = result.get('RefID')
                    
                    logger.info(f"تایید پرداخت موفق - Authority: {authority}, RefID: {ref_id}")
                    
                    return {
                        'success': True,
                        'ref_id': ref_id,
                        'status_code': result.get('Status'),
                        'message': 'پرداخت با موفقیت تایید شد'
                    }
                else:
                    # خطا در تایید
                    error_message = result.get('Errors', {}).get('Message', 'خطا در تایید پرداخت')
                    logger.error(f"خطا در تایید پرداخت - Authority: {authority}: {error_message}")
                    
                    return {
                        'success': False,
                        'message': error_message,
                        'error_code': result.get('Status')
                    }
            else:
                logger.error(f"خطا در ارتباط با زرین‌پال برای تایید - Authority: {authority}: HTTP {response.status_code}")
                return {
                    'success': False,
                    'message': 'خطا در ارتباط با درگاه پرداخت'
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"خطا در ارتباط با زرین‌پال برای تایید - Authority: {authority}: {str(e)}")
            return {
                'success': False,
                'message': 'خطا در ارتباط با درگاه پرداخت'
            }
        except Exception as e:
            logger.error(f"خطای غیرمنتظره در تایید پرداخت - Authority: {authority}: {str(e)}")
            return {
                'success': False,
                'message': 'خطای غیرمنتظره در تایید پرداخت'
            }
    
    def get_payment_status_description(self, status_code):
        """دریافت توضیحات وضعیت پرداخت"""
        status_descriptions = {
            100: "پرداخت موفق",
            101: "پرداخت قبلاً تایید شده",
            200: "کاربر لغو کرده",
            -1: "اطلاعات ارسال شده ناقص است",
            -2: "IP یا مرچنت کد پذیرنده صحیح نیست",
            -3: "رقم تراکنش باید بین 10,000 و 50,000,000 تومان باشد",
            -4: "سطح پذیرنده پایین تر از سطح نقره ای است",
            -11: "درخواست مورد نظر یافت نشد",
            -12: "امکان ویرایش درخواست وجود ندارد",
            -21: "هیچ نوع عملیات مالی برای این تراکنش یافت نشد",
            -22: "تراکنش ناموفق می باشد",
            -33: "رقم تراکنش با رقم پرداخت شده مطابقت ندارد",
            -34: "سقف تقسیم تراکنش از لحاظ تعداد یا رقم عبور نموده",
            -40: "اجازه دسترسی به متد مورد نظر وجود ندارد",
            -41: "اطلاعات ارسال شده مربوط به AdditionalData غیرمعتبر می باشد",
            -42: "مدت زمان معتبر طول عمر شناسه پرداخت بین 3 دقیقه تا 45 روز می باشد",
            -54: "درخواست مورد نظر آرشیو شده",
            -101: "عملیات پرداخت ناموفق بوده است",
            -102: "خطا در تایید پرداخت",
            -103: "خطا در تایید پرداخت",
            -104: "خطا در تایید پرداخت",
            -105: "خطا در تایید پرداخت",
            -106: "خطا در تایید پرداخت",
            -107: "خطا در تایید پرداخت",
            -108: "خطا در تایید پرداخت",
            -109: "خطا در تایید پرداخت",
            -110: "خطا در تایید پرداخت",
            -111: "خطا در تایید پرداخت",
            -112: "خطا در تایید پرداخت",
            -113: "خطا در تایید پرداخت",
            -114: "خطا در تایید پرداخت",
            -115: "خطا در تایید پرداخت",
            -116: "خطا در تایید پرداخت",
            -117: "خطا در تایید پرداخت",
            -118: "خطا در تایید پرداخت",
            -119: "خطا در تایید پرداخت",
            -120: "خطا در تایید پرداخت",
            -121: "خطا در تایید پرداخت",
            -122: "خطا در تایید پرداخت",
            -123: "خطا در تایید پرداخت",
            -124: "خطا در تایید پرداخت",
            -125: "خطا در تایید پرداخت",
            -126: "خطا در تایید پرداخت",
            -127: "خطا در تایید پرداخت",
            -128: "خطا در تایید پرداخت",
            -129: "خطا در تایید پرداخت",
            -130: "خطا در تایید پرداخت",
            -131: "خطا در تایید پرداخت",
            -132: "خطا در تایید پرداخت",
            -133: "خطا در تایید پرداخت",
            -134: "خطا در تایید پرداخت",
            -135: "خطا در تایید پرداخت",
            -136: "خطا در تایید پرداخت",
            -137: "خطا در تایید پرداخت",
            -138: "خطا در تایید پرداخت",
            -139: "خطا در تایید پرداخت",
            -140: "خطا در تایید پرداخت",
            -141: "خطا در تایید پرداخت",
            -142: "خطا در تایید پرداخت",
            -143: "خطا در تایید پرداخت",
            -144: "خطا در تایید پرداخت",
            -145: "خطا در تایید پرداخت",
            -146: "خطا در تایید پرداخت",
            -147: "خطا در تایید پرداخت",
            -148: "خطا در تایید پرداخت",
            -149: "خطا در تایید پرداخت",
            -150: "خطا در تایید پرداخت",
            -151: "خطا در تایید پرداخت",
            -152: "خطا در تایید پرداخت",
            -153: "خطا در تایید پرداخت",
            -154: "خطا در تایید پرداخت",
            -155: "خطا در تایید پرداخت",
            -156: "خطا در تایید پرداخت",
            -157: "خطا در تایید پرداخت",
            -158: "خطا در تایید پرداخت",
            -159: "خطا در تایید پرداخت",
            -160: "خطا در تایید پرداخت",
            -161: "خطا در تایید پرداخت",
            -162: "خطا در تایید پرداخت",
            -163: "خطا در تایید پرداخت",
            -164: "خطا در تایید پرداخت",
            -165: "خطا در تایید پرداخت",
            -166: "خطا در تایید پرداخت",
            -167: "خطا در تایید پرداخت",
            -168: "خطا در تایید پرداخت",
            -169: "خطا در تایید پرداخت",
            -170: "خطا در تایید پرداخت",
            -171: "خطا در تایید پرداخت",
            -172: "خطا در تایید پرداخت",
            -173: "خطا در تایید پرداخت",
            -174: "خطا در تایید پرداخت",
            -175: "خطا در تایید پرداخت",
            -176: "خطا در تایید پرداخت",
            -177: "خطا در تایید پرداخت",
            -178: "خطا در تایید پرداخت",
            -179: "خطا در تایید پرداخت",
            -180: "خطا در تایید پرداخت",
            -181: "خطا در تایید پرداخت",
            -182: "خطا در تایید پرداخت",
            -183: "خطا در تایید پرداخت",
            -184: "خطا در تایید پرداخت",
            -185: "خطا در تایید پرداخت",
            -186: "خطا در تایید پرداخت",
            -187: "خطا در تایید پرداخت",
            -188: "خطا در تایید پرداخت",
            -189: "خطا در تایید پرداخت",
            -190: "خطا در تایید پرداخت",
            -191: "خطا در تایید پرداخت",
            -192: "خطا در تایید پرداخت",
            -193: "خطا در تایید پرداخت",
            -194: "خطا در تایید پرداخت",
            -195: "خطا در تایید پرداخت",
            -196: "خطا در تایید پرداخت",
            -197: "خطا در تایید پرداخت",
            -198: "خطا در تایید پرداخت",
            -199: "خطا در تایید پرداخت",
            -200: "خطا در تایید پرداخت",
        }
        
        return status_descriptions.get(status_code, f"وضعیت نامشخص: {status_code}")


# تنظیمات درگاه پرداخت
ZARINPAL_MERCHANT_ID = '44a8726a-97be-43b4-ad67-d4e7fe4eae72'
ZARINPAL_SANDBOX = True  # در محیط تست True کنید، در محیط تولید False کنید
ZARINPAL_CALLBACK_URL = 'http://127.0.0.1:8000/checkout/zarinpal/callback/'

# ایجاد نمونه درگاه پرداخت
payment_gateway = ZarinPalPaymentGateway(
    merchant_id=ZARINPAL_MERCHANT_ID,
    sandbox=ZARINPAL_SANDBOX
)
