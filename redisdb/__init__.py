import redis
import collections 
import json
import threading
class RedisDB():
    
    def __init__(self, redis_info, log_info):
        self.lock     = threading.Lock()
        self.log_info = log_info
        self.logger   = log_info.init_class_logger( self.__class__.__name__ )

        self.redis_info = redis_info

        host = self.redis_info.get_host()
        port = self.redis_info.get_port()
        pswd = self.redis_info.get_password()

        self.client = redis.Redis(host, port=port)

    def get_line_data(self, line_name):
        
        raw_data = self.client.get( line_name )
        if raw_data:
            data = raw_data.decode("utf-8")
            self.logger.info(f"Redis Collected Data: {json.loads(data)}")
            return json.loads(data)

        else:
            self.logger.info(f"Key not available")