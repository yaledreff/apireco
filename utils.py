import os
import shutil

PATH_ARTICLES = 'data/dfArticlesActive.csv'
PATH_ARTICLES_USERS = 'data/dfArticlesPerActiveUser.csv'

def save_file(file, path):
    if os.path.exists(path):
        os.remove(path)
        print("Ancien fichier " + path + " supprimé")

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return True

def save_articles(uploadfile):
    return save_file(uploadfile, PATH_ARTICLES)

def save_users(uploadfile):
    return save_file(uploadfile, PATH_ARTICLES_USERS)