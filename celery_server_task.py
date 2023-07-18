# -*- coding: utf-8 -*-
import os
import sys
path = os.path.dirname(__file__)
sys.path.append(path)
# путь к проекту

from variables_and_libs import subprocess,Celery,torch,AutoTokenizer,AutoModelForSequenceClassification,pickle,register,NAME_MODEL_NLP_TOXICITY,DICT_MODEL

register('pickle', 
        lambda x: pickle.dumps(x), 
        lambda x: pickle.loads(x), 
        'application/x-python-serialize')
# серилиализация pickle формата


file = open(f"{path}/helper/config_redis_celery.conf")
for line in file:
    if "port" in line.split():
        redis_url = f"redis://localhost:{line.split()[1]}"
        break
    else:
        print("Порт Redis для Celery не найден")
        exit(0)


celery = Celery("task", 
                backend = redis_url,
                task_serializer = 'pickle',
                result_serializer = 'pickle',
                accept_content = ['pickle'],
                task_track_started = True,
                broker_connection_retry_on_startup = True,
                broker = redis_url)
# объявление переменной Celery


@celery.task(name="start_model_nlp")
def start_model_nlp():
    
    """
    Данная функция необходима для того чтобы осуществить процесс
    запуска моделей в режиме очереди
    """

    tokenizer = AutoTokenizer.from_pretrained(NAME_MODEL_NLP_TOXICITY)
    # подключение токенизатора BERT модели
    model = AutoModelForSequenceClassification.from_pretrained(NAME_MODEL_NLP_TOXICITY)
    # подключение модели BERT модели
    DICT_MODEL['bert_tokenizer'] = tokenizer
    DICT_MODEL['bert_model'] = model
    # добавление в общий словарь данных для работы


@celery.task(name="predict_nlp_model")
def predict_nlp_model(text):
    
    """
    Данная функция необходима для того чтобы осуществить процесс
    предсказания модели относительно токсичности текста
    """
    
    with torch.no_grad():
        inputs = DICT_MODEL['bert_tokenizer'](text, return_tensors='pt', truncation=True, padding=True).to(DICT_MODEL['bert_model'].device)
        # токенизация
        proba = torch.sigmoid(DICT_MODEL['bert_model'](**inputs).logits).cpu().numpy()
        # использование модели для получения классификации
        
    if isinstance(text, str):
        proba = proba[0]
    return proba.tolist()


@celery.task(name="kill_model_nlp")
def kill_model_nlp(name):
    
    """
    Данная функция необходима для того чтобы осуществить процесс
    освобождения ОЗУ от нейросетей
    """
    
    if name in DICT_MODEL:
        del DICT_MODEL[name]
    else:
        pass



# celery -A Project_NLP.celery_server_task:celery worker --pool=prefork --concurrency=4
# celery -A Project_NLP.celery_server_task:celery flower