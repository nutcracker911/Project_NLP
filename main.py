# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/o.nikolaev/Desktop/AI-GIT/beck/API01/low_code/project_1/Project_NLP")
from variables_and_libs import FastAPI, uvicorn


app = FastAPI(title="AI API")
# инициализация работы FastAPI

if __name__ == "__main__":
    uvicorn.run(app,
                host="0.0.0.0",
                port=80)
