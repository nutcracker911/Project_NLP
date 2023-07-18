# -*- coding: utf-8 -*-
import os
import sys
path = os.path.dirname(__file__)
# путь к проекту
sys.path.append(path)
path_celery = (".").join(path.split(os.getcwd())[1].split("/")[1:])
# путь к файлам для запуска Celery

from variables_and_libs import FastAPI, uvicorn, subprocess, DataFromBot,KillNameModel, BackgroundTasks,LABEL
from helper.bd_redis import Redis
from celery_server_task import start_model_nlp,predict_nlp_model,kill_model_nlp


subprocess.run(["redis-server", f"{path}/helper/config_redis.conf"], stdout=subprocess.PIPE)
# запуск сервера Redis


subprocess.Popen(["celery", "-A", f"{path_celery}.celery_server_task:celery", "worker","--pool=prefork", "--concurrency=4"], stdout=subprocess.PIPE)
for x in range(1000000):
    pass
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
    
    start_model_nlp.delay()
    #запуск нейросети BERT
    return {"status":"complite",
            "data":None}


@app.post(
    "/model/predict",
    description = "Обработка пользовательского сообщения")
async def predict_phrase_user(item: DataFromBot):
    # print(item)
    

    
    
    # print(redIs.get_redis(item.client_id))

    
    # print(type(DICT_MODEL['bert_tokenizer']))
    result = predict_nlp_model.delay(item.phrase).get()
    # print(LABEL[str(result.index(max(result)))])
    
    redIs.set_redis(item.client_id,{"phrase":item.phrase,
                                    "label":LABEL[str(result.index(max(result)))]})
    print(redIs.get_redis(item.client_id))
    
    return item


@app.post(
    "/model/kill_model",
    description = "Завершение работы моделей")
async def kill_model(item:KillNameModel):

    kill_model_nlp.delay(item.name_model)
    
    return {"status":"complite",
            "data":None}

if __name__ == "__main__":
    uvicorn.run(app,
                host="0.0.0.0",
                port=80)

subprocess.run(["redis-cli", "-p","6378","shutdown"], stdout=subprocess.PIPE)
subprocess.run(["redis-cli", "-p","6380","shutdown"], stdout=subprocess.PIPE)