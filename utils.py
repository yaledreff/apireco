import os
import shutil

PATH_ARTICLES = '/data/dfArticlesActive.csv'
PATH_ARTICLES_USERS = '/data/dfArticlesPerActiveUser.csv'
PATH_PREDICTIONS = '/data/dfPredictions.csv'

def save_file(file, path):
    if os.path.exists(path):
        os.remove(path)
        print("Ancien fichier " + path + " supprimé")
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"info": f"file '{file.filename}' saved at '{path}'"}

def save_articles(uploadfile):
    result = save_file(uploadfile, PATH_ARTICLES)
    return result

def save_users(uploadfile):
    result = save_file(uploadfile, PATH_ARTICLES_USERS)
    return result

def getListUsers(dfArticlesPerActiveUser):
    lstUsers = dfArticlesPerActiveUser['user_id'].unique().tolist()
    return lstUsers

def save_preds(dfPreds):
    dfPreds.to_csv(PATH_PREDICTIONS)