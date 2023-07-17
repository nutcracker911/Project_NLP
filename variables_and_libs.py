import json
import pytz
import uvicorn
import requests
import asyncio
import redis

import subprocess
import threading
import asyncio
from pprint import pprint
from datetime import datetime
from pydantic import BaseModel
from fastapi import FastAPI, Request, BackgroundTasks
from minio import Minio
import io
import logging
import torch
from celery import Celery
from transformers import AutoTokenizer, AutoModelForSequenceClassification


class DataFromBot(BaseModel):
    client_id : str
    phrase : str
    
class KillNameModel(BaseModel):
    name_model: str

    
global HOST_NAME_REDIS
HOST_NAME_REDIS = "127.0.0.1"
# домен редиса

global PORT_REDIS
PORT_REDIS = 6378
# порт редиса

global NAME_MODEL_NLP_TOXICITY
NAME_MODEL_NLP_TOXICITY = 'cointegrated/rubert-tiny-toxicity'
# название нейромодели для работы с токсичностью

global DICT_MODEL
DICT_MODEL = {}
# хранение всех необходимых нейромоделей в оперативной памяти