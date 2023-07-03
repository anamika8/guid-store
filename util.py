import secrets
import datetime
import time
import re

class GuidUtil:

    @staticmethod
    def generate_random_guid():
        hex_string = '0123456789ABCDEF'
        generated_string = ''.join([secrets.choice(hex_string) for x in range(32)])
        return generated_string
    
    @staticmethod
    def is_hex(s):
        pattern = re.compile(r'^[0-9A-F]+$', re.IGNORECASE)
        return bool(re.match(pattern, s))
    
    @staticmethod
    def is_expired_time(given_time):
        current_time = int(time.time())
        return int(given_time) < current_time

    @staticmethod
    def is_time_format_correct(given_time):
        pattern = r'\D'
        if bool(re.search(pattern, given_time)):
            return False
        return True
    
    @staticmethod
    def generate_expiration_time():
        # method to get the Unix formatted expiration time 
        current_time = datetime.datetime.now()
        # 30 days from current time
        expiration_time = current_time + datetime.timedelta(days=30)
        # convert to unix time
        unix_time = int(time.mktime(expiration_time.timetuple()))
        return unix_time
