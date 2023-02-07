from fastapi import FastAPI, Request, Response, HTTPException, UploadFile, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, validator
from hashlib import sha256
from jinja2 import Template
from fastapi.responses import RedirectResponse
from playhouse.shortcuts import model_to_dict
import datetime
import pytz
import peewee
import uuid
import os

time_zone = pytz.timezone('Asia/Kolkata')

app = FastAPI()
templates = Jinja2Templates(directory="templates")

db = peewee.SqliteDatabase("final_data.db")

class Category(peewee.Model):
    category_name = peewee.CharField()

    class Meta:
        database = db





class Article(peewee.Model):
    # user_info = peewee.ForeignKeyField(User, to_field='username')
    category_name = peewee.ForeignKeyField(Category, to_field='category_name')
    title = peewee.CharField()
    thumbnail = peewee.CharField()
    created_at = peewee.DateTimeField(default = datetime.datetime.now(time_zone).strftime("%Y-%m-%d %H: %M:%S"))
    updated_at = peewee.DateTimeField(default = datetime.datetime.now(time_zone).strftime("%Y-%m-%d %H: %M:%S"))
    text = peewee.CharField()
    short_description = peewee.CharField()

    class Meta:
        database = db



def create_tables():
    with db:
        db.create_tables([Article , Category])

# allow running from the command line

create_tables()

# Category.create(category_name = 'View All')
# Category.create(category_name ='Design')
# Category.create(category_name = 'Product')
# Category.create(category_name  ='Software Engineering')
# Category.create(category_name  ='Customer Service')
# Article.create(category_name='Design', title='Testing', thumbnail='dummy', text='dumyyedhsgerghrwhearhrwhgaehae', short_description='kuch ni h')


@app.get("/articles/")
def get_articles():
    articles = Article.select()
    return [{"title": article.title ,"description": article.text} for  article in articles]


@app.get("/article/{id}")
def get_single_article(id : int):
    article = Article.select().where(Article.id == id).first()
    # single_article = Article.get(Article.id == id)
    return {
        "title": article.title,
        "text": article.text
    }
    

@app.get("/category/{category_name}")
async def get_user_posts(category_name : str):
    try:
        category = Category.get(Category.category_name == category_name)
    except Category.DoesNotExist:
        raise HTTPException(status_code=400, detail="Category not found")
    
    articles = Article.select().where(Article.category_name == category)
    category_articles = [{"category_name": article.title, "description": article.text} for article in articles]
    
    
    return [model_to_dict(article) for article in articles]

@app.post("/create_article")
async def create_post(request: Request):
    request_data = await request.json()
    # token = request.headers.get("Authorization")
    title = request_data.get("title")
    text = request_data.get("text")
    category_name = request_data.get("category_name")
    short_description = request_data.get("short_description")
    thumbnail = request_data.get("thumbnail")
    # print(image_url)
    

    # try:
    #     authentication = Authentication.get(Authentication.token == token)
    #     user = authentication.user
    # except Authentication.DoesNotExist:
    #     raise HTTPException(status_code=400, detail="Invalid Token")

    try:
        new_article = Article.create(
            title=title,
            text=text,
            category_name=category_name,
            short_description = short_description,
            thumbnail = thumbnail       
        )
    except peewee.IntegrityError as e:
        raise HTTPException(status_code=400, detail="Error creating post")

    return {"message": "Post created successfully"}


@app.put("/edit_articles/{article_id}")
async def update_article(request : Request, article_id: int):
    try:
        request_data = await request.json()
    # token = request.headers.get("Authorization")
        article = Article.get(Article.id == article_id)
        article.title = request_data.get("title")
        article.text = request_data.get("text")
        article.category_name = request_data.get("category_name")
        article.updated_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        article.thumbnail = request_data.get("thumbnail")
        article.short_description = request_data.get("short_description")
        article.save()
        return {"message": "Article updated successfully", 'article': article}
    except Article.DoesNotExist:
        raise HTTPException(status_code=404, detail="Article not found")


@app.delete("/delete_article/{id}")
async def deleteArticle(id): 
    try:
        query = Article.delete().where(Article.id == int(id))
        print(query)
        query.execute()
        return {'status': status.HTTP_200_OK}
    except Article.DoesNotExist:
        return {'message': 'Article Does Not Exist'}
