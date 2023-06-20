from variables_and_libs import threading, asyncio

def decorator_async_function(func_in):
    
    def func_async(payload):
            async def async_func(payload):
                func_in(payload)
            asyncio.run(async_func(payload))
    
    def wrapper(*args, **kwargs):
        threading.Thread(target=func_async, args=([*args])).start()
    
    return wrapper