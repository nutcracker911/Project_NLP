# -*- coding: utf-8 -*-
path = "/Users/o.nikolaev/Desktop/AI-GIT/beck/API01/low_code/project_1/Project_NLP"
import sys
sys.path.append(path)

from variables_and_libs import FastAPI, uvicorn, DataFromBot,subprocess
from helper.decorators import decorator_async_function

subprocess.run(["redis-server", f"{path}/helper/config_redis.conf"], stdout=subprocess.PIPE)
# инициализация работы Redis

app = FastAPI(title="AI API", 
              debug=True,
              docs_url="/")
# инициализация работы FastAPI



@app.post(
    "/model/predict",
    description="Обработка пользовательского сообщения"
)
async def predict_phrase_user (item: DataFromBot):
    
    return item





if __name__ == "__main__":
    uvicorn.run(app,
                host="0.0.0.0",
                port=80)

subprocess.run(["redis-cli", "-p","6378","shutdown"], stdout=subprocess.PIPE)