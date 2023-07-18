# -*- coding: utf-8 -*-
import os
import sys
path = os.path.dirname(__file__)
# путь к проекту
sys.path.append(path)
path_celery = (".").join(path.split(os.getcwd())[1].split("/")[1:])
# путь к файлам для запуска Celery

from variables_and_libs import FastAPI, uvicorn, subprocess, DataFromBot,KillNameModel,GetDialogs, json,BackgroundTasks,LABEL
from helper.bd_redis import Redis
from celery_server_task import start_model_nlp,predict_nlp_model,kill_model_nlp

subprocess.run(["redis-server", f"{path}/helper/config_redis_celery.conf"], stdout=subprocess.PIPE)
# запуск сервера Redis для Celery
subprocess.run(["redis-server", f"{path}/helper/config_redis.conf"], stdout=subprocess.PIPE)
# запуск сервера Redis


subprocess.Popen(["celery", "-A", f"{path_celery}.celery_server_task:celery", "worker","--pool=prefork", "--concurrency=4"], stdout=subprocess.PIPE)
for x in range(100000000):
    pass
# задержка
subprocess.Popen(["celery", "-A", f"{path_celery}.celery_server_task:celery", "flower"], stdout=subprocess.PIPE)
# запуск Celery для работы с очередями

redIs = Redis()
redIs.connect_redis()
# инициализация работы класса по работе с Redis


app = FastAPI(title="Global API", 
              debug=True,
              docs_url="/")
# инициализация работы FastAPI


@app.post(
    "/model/start",
    description = "Запуск нейросети для обработки эмоциональной составляющей")
async def start_model():
    
    """
    Данная функция необходима для того чтобы осуществить процесс
    запуска моделей в режиме очереди
    """
    
    start_model_nlp.delay()

    return {"status":"complite",
            "data":None}


@app.post(
    "/model/predict",
    description = "Обработка пользовательского сообщения")
async def predict_phrase_user(item: DataFromBot):
    
    """
    Данная функция необходима для того чтобы осуществить процесс
    предсказания полученного текста
    """

    result = predict_nlp_model.delay(item.phrase).get()

    redIs.set_redis(item.client_id,{"phrase":item.phrase,
                                    "label":LABEL[str(result.index(max(result)))],
                                    "score":str(max(result))}) 
    return {"status":"complite",
            "data":None}

@app.post(
    "/phrase/get",
    description = "Получение всех сообщений пользователя с лейблами")
async def get_phrase_in_redis(item: GetDialogs):
    
    """
    Данная функция необходима для того чтобы осуществить процесс
    получения данных с Redis
    """
    
    result = redIs.get_redis(item.client_id)
    out = []
    for x in range(len(result)):
        out.append(json.loads(result[x]))
    return out
    

@app.post(
    "/model/kill_model",
    description = "Завершение работы моделей")
async def kill_model(item:KillNameModel):

    """
    Данная функция необходима для того чтобы осуществить процесс
    выключения модели
    """
    
    kill_model_nlp.delay(item.name_model)
    
    return {"status":"complite",
            "data":None}

if __name__ == "__main__":
    uvicorn.run(app,
                host="0.0.0.0",
                port=80)

subprocess.run(["redis-cli", "-p","6378","shutdown"], stdout=subprocess.PIPE)
subprocess.run(["kill", "-9", "$(lsof -t -i:5555)"], stdout=subprocess.PIPE)
subprocess.run(["redis-cli", "-p","6380","shutdown"], stdout=subprocess.PIPE)

