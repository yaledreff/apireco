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

@app.get("/")
def read_root():
    return {"message": "Welcome from the API"}

@app.get("/coucou")
def read_coucou():
    return {"message": "Coucou from the API"}

# ****************************** USERS AND ARTICLES DATA MANAGEMENT *****************************

@app.post("/articles")
async def setArticles(file: UploadFile = File(...)):
    return save_articles(file)

@app.post("/users")
async def setUsers(file: UploadFile = File(...)):
    return save_users(file)

@app.get("/users")
async def getUsers():
    dfArticlesPerActiveUser = pd.read_csv(PATH_ARTICLES_USERS)
    lstUsers = getListUsers(dfArticlesPerActiveUser)
    responseJson = jsonable_encoder(lstUsers)
    return JSONResponse(content=responseJson)

# ****************************** RECOMMENDATION MODEL [TRAIN + PREDICT] *****************************

@app.post("/train")
async def predict():
    # chargement des données :
    dfArticlesActive = pd.read_csv(PATH_ARTICLES)
    dfArticlesPerActiveUser = pd.read_csv(PATH_ARTICLES_USERS)
    # retraitement des données (on limite le dataset aux utilisateurs ayant le plus de consult et aux articles les plus vus)
    dfArticlesPerActiveUser = setMinArticlesViews(dfArticlesPerActiveUser, minViews=100)
    dfArticlesPerActiveUser = setMinUsersViews(dfArticlesPerActiveUser, minViews=60)
    dfPreds = getSVDFactoMatrix(dfArticlesPerActiveUser)
    # Sauvegarde des prévisions
    save_preds(dfPreds)
    return {"message": "Entrainement terminé avec succès"}

@app.post("/predict")
async def predict(param: ParamPred):
    userId = param.getUserId()
    topN = param.getTopN()
    # chargement des données : matrice de factorisation SVD [Modèle collaboratif]
    dfPreds = pd.read_csv(PATH_PREDICTIONS).set_index('click_article_id')
    dfPreds.columns = dfPreds.columns.astype(int)
    dfArticlesPerActiveUser = pd.read_csv(PATH_ARTICLES_USERS)
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
