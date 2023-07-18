from variables_and_libs import redis, HOST_NAME_REDIS, PORT_REDIS, json

class Redis():
    
    def __init__(self, 
                host = HOST_NAME_REDIS,
                port= PORT_REDIS) -> None:
        
        self.host = host
        self.port = port
    
        
    def connect_redis(self):
        self.r = redis.Redis(host=self.host, 
                            port=self.port, 
                            db = 0,
                            decode_responses=True)

    def set_redis(self, key:str, value:dict):
        
        self.r.hset(key,json.dumps(value,ensure_ascii=False))
    
    def get_redis(self, key:str):
        return self.r.hgetall(key)
