from typing import Union
from fastapi import FastAPI
from pymongo import MongoClient
import datetime

app = FastAPI()

client = MongoClient(username="root", password="password")
db = client.test_database
posts = db.posts
post = {"author": "Mike",
        "text": "My first blog post!",
        "tags": ["mongodb", "python", "pymongo"],
        "date": datetime.datetime.utcnow()}
posts.insert_one(post)
new_posts = [{"author": "Mike",
              "text": "Another post!",
              "tags": ["bulk", "insert"],
              "date": datetime.datetime(2009, 11, 12, 11, 14)},
             {"author": "Eliot",
              "title": "MongoDB is fun",
              "text": "and pretty easy too!",
              "date": datetime.datetime(2009, 11, 10, 10, 45)}]
result = posts.insert_many(new_posts)

@app.get("/")
def read_root():
    return {"hello":"world"}

@app.get("/posts")
def all_posts():
    return [post for post in posts.find()]

@app.get("/posts/author/{author}")
def posts_by_author(author):
    return [post for post in posts.find({"author":author})]

@app.get("/posts/author/{author}")
def posts_by_author(author):
    return [post for post in posts.find({"author":author})]


