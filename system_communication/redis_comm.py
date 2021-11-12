from redisdb import RedisDB

class RedisComm():

    def __init__(self, fh_main, log_info ):
        self.log_info = log_info
        self.logger   = log_info.init_class_logger( self.__class__.__name__ )

        redis_info   = fh_main.redisdb_info()
        self.redisdb = RedisDB( redis_info, self.log_info )

    def get_redis(self):
        return self.redisdb   

    