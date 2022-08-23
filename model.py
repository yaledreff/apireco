
import pandas as pd

from scipy.sparse import csr_matrix
import sklearn
from sklearn.model_selection import train_test_split
from pydantic import BaseModel
from surprise import SVD, accuracy
from scipy.sparse.linalg import svds

# ****************************** MODEL TRAINING *****************************

def setMinArticlesViews(dfArticlesPerActiveUser, minViews=2):
    # Retire les articles qui n'ont pas un minimum de vues de 'minViews'
    dfArticlesViews = dfArticlesPerActiveUser[['click_article_id', 'session_id']].groupby(['click_article_id']).count().reset_index()
    lstArticlesOut = dfArticlesViews[dfArticlesViews['session_id'] <= minViews]['click_article_id'].unique().tolist()
    dfArticlesPerActiveUser = dfArticlesPerActiveUser[~dfArticlesPerActiveUser['click_article_id'].isin(lstArticlesOut)]
    return dfArticlesPerActiveUser

def getSVDFactoMatrix(dfArticlesPerActiveUser):
    dfUsersItemsPivotMatrix = dfArticlesPerActiveUser.pivot(index='user_id', columns='click_article_id', values='session_id').fillna(0)
    usersItemsPivotMatrix = dfUsersItemsPivotMatrix.values
    usersIds = list(dfUsersItemsPivotMatrix.index)
    #Factorisation de la matrice
    usersItemsPivotSparseMatrix = csr_matrix(usersItemsPivotMatrix)
    U, sigma, Vt = svds(usersItemsPivotSparseMatrix, k=15)

    return 'coucou'

def train_model():
    dfArticlesPerActiveUser = pd.read_csv('data/dfArticlesPerActiveUser.csv')
    dfArticlesPerActiveUser = setMinArticlesViews(dfArticlesPerActiveUser, 2)
    # Séparation des données d'entraînements et tests pour mesurer la performance du modèle entrainé
    dfUsersActivityTrain, dfUsersActivityTest = sklearn.model_selection.train_test_split(dfArticlesPerActiveUser,
                                                                                         stratify=dfArticlesPerActiveUser['user_id'],
                                                                                         test_size=0.20,
                                                                                         random_state=2)

# ****************************** MODEL PREDICT *****************************

class ParamPred(BaseModel):
    userId: int
    topN: int
    def getUserId(self):
        return self.userId
    def getTopN(self):
        return self.topN

class ResponsePred():
    articleId: int
    score: float
    def __init__(self, articleId, score):
        self.articleId = articleId
        self.score = score
    def setPred(self, articleId, score):
        self.articleId = articleId
        self.score = score
    def getarticleId(self):
        return self.articleId
    def getScore(self):
        return self.score

class ResponsePreds():
    preds = []
    def __init__(self, dfPreds):
        self.preds = self.create(dfPreds)
    def getPreds(self):
        return self.preds
    def addPred(self, pred):
        self.preds.append(pred)
    def create(self, dfPreds):
        lstPreds = dfPreds.values.tolist()
        response = [ResponsePred(int(articleId), score) for articleId,  score in lstPreds]
        return response

class CFRecommender:
    MODEL_NAME = 'Collaborative Filtering'

    def __init__(self, dfPredictions):
        self.dfPredictions = dfPredictions

    def get_model_name(self):
        return self.MODEL_NAME

    def recommend_items(self, userId, itemsToIgnore=[], topn=10):
        # Get and sort the user's predictions
        sortedUserPredictions = self.dfPredictions[userId].sort_values(ascending=False) \
            .reset_index().rename(columns={userId: 'recStrength'})
        # Recommend the highest predicted rating movies that the user hasn't seen yet.
        dfRecommendations = sortedUserPredictions[~sortedUserPredictions['click_article_id'].isin(itemsToIgnore)] \
            .sort_values('recStrength', ascending=False) \
            .head(topn)
        return dfRecommendations

def get_items_interacted(user_id, dfUserActivity):
    # On récupere les id d'articles consultés pour un utilisateur donnée.
    interacted_items = dfUserActivity.loc[user_id]['click_article_id']
    return set(interacted_items if type(interacted_items) == pd.Series else [interacted_items])
