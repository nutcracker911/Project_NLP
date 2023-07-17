# -*- coding: utf-8 -*-
import os
import sys
path = os.path.dirname(__file__)
# путь к проекту
sys.path.append(path)
from variables_and_libs import subprocess,Celery,torch,AutoTokenizer,AutoModelForSequenceClassification,NAME_MODEL_NLP_TOXICITY,DICT_MODEL

subprocess.run(["redis-server", f"{path}/helper/config_redis_celery.conf"], stdout=subprocess.PIPE)

file = open(f"{path}/helper/config_redis_celery.conf")
for line in file:
    if "port" in line.split():
        redis_url = f"redis://localhost:{line.split()[1]}"
        break
    else:
        print("Порт Redis для Celery не найден")
        exit(0)
    

celery = Celery("task", 
                backend=redis_url,
                broker_connection_retry_on_startup=True,
                broker=redis_url)

@celery.task(name="start_model_nlp")
def start_model_nlp():
    tokenizer = AutoTokenizer.from_pretrained(NAME_MODEL_NLP_TOXICITY)
    model = AutoModelForSequenceClassification.from_pretrained(NAME_MODEL_NLP_TOXICITY)
    DICT_MODEL['bert_tokenizer'] = tokenizer
    DICT_MODEL['bert_model'] = model



@celery.task(name="predict_nlp_model")
def predict_nlp_model(text,aggregate):
    with torch.no_grad():
        inputs = DICT_MODEL['bert_tokenizer'](text, return_tensors='pt', truncation=True, padding=True).to(DICT_MODEL['bert_model'].device)
        proba = torch.sigmoid(DICT_MODEL['bert_model'](**inputs).logits).cpu().numpy()
    if isinstance(text, str):
        proba = proba[0]
    print(proba)
    if aggregate:
        return 1 - proba.T[0] * (1 - proba.T[-1])
    return proba

@celery.task(name="kill_model_nlp")
def kill_model_nlp(name):
    
    if name in DICT_MODEL:
        del DICT_MODEL[name]
    else:
        pass



# celery -A Project_NLP.celery_server_task:celery worker --pool=prefork --concurrency=4
# celery -A Project_NLP.celery_server_task:celery flower