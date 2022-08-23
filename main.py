# This is a sample Python script.

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import csv
import os
from io import BytesIO
from tempfile import NamedTemporaryFile

import pandas as pd

from fastapi import FastAPI
from fastapi import File
from fastapi import UploadFile
import uvicorn

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from model import *
from utils import *

app = FastAPI()
# chargement des données : matrice de factorisation SVD [Modèle collaboratif]
dfPreds = pd.read_csv('/data/dfPredictions.csv').set_index('click_article_id')
dfPreds.columns = dfPreds.columns.astype(int)
dfArticlesActive = pd.read_csv('/data/dfArticlesActive.csv')
dfArticlesPerActiveUser = pd.read_csv('/data/dfArticlesPerActiveUser.csv')

@app.get("/")
def read_root():
    return {"message": "Welcome from the API"}

@app.get("/coucou")
def read_coucou():
    return {"message": "Coucou from the API"}

# ****************************** USERS AND ARTICLES DATA MANAGEMENT *****************************

@app.post("/articles")
async def articles2(file: UploadFile = File(...)):
    return save_articles(file)

@app.post("/users")
def articles2(file: UploadFile = File(...)):
    return save_users(file)

# ****************************** RECOMMENDATION MODEL [TRAIN + PREDICT] *****************************

@app.post("/train")
def predict():
    return {"message": "coucou le train"}

@app.post("/predict")
def predict(param: ParamPred):
    userId = param.getUserId()
    topN = param.getTopN()
    # Instanciation de la classe de recommandation (collaborative model)
    cfRecommenderModel = CFRecommender(dfPreds)
    # Liste les articles déjà lus par l'utilisateurs (exclus des recommandations)
    itemsToIgnore = get_items_interacted(userId, dfArticlesPerActiveUser)
    # prediction
    pred = cfRecommenderModel.recommend_items(userId, itemsToIgnore, topN)
    response = ResponsePreds(pred).getPreds()
    responseJson = jsonable_encoder(response)
    return JSONResponse(content=responseJson)

if __name__ == "__main__":
    uvicorn.run("main:app")
