from fastapi import FastAPI, APIRouter, Body, Request, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup as bs4
from fastapi import HTTPException
from pymongo import MongoClient
from typing import List
import validators
import requests
import time
import re


app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_db_client():
    uri = "mongodb+srv://nikhil:123@fastapicluster.bxwuasi.mongodb.net/?retryWrites=true&w=majority"
    app.mongodb_client = MongoClient(uri)
    app.database = app.mongodb_client['fastApiCluster']
    print("Hurry! Connected to the MongoDB database.")

@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()


@app.get("/")
def read_root():
    time.sleep(2)
    return {"version": "1.0.0","name":"Chat-bot","author":"Nikhil chauhan"}

@app.get("/download")
def dowload_data(url:str=''):
    if not url:
        raise HTTPException(status_code=404, detail="url is required!")
    else:
        is_valid = validators.url(url)
        if is_valid:
            html = requests.get(url)
            soup = bs4(html.content, "lxml")
            body = soup.get_text()
            body = body.replace("\n\n", "")
            body = body.replace("   ", " ")
            new_list_item = app.database["chatBotDB"].insert_one({"data": body})
            return {"data": body}
        else:
            raise HTTPException(status_code=404, detail="not a valid url!")

@app.get("/search")
def search_data(term:str=''):
    if not term:
        raise HTTPException(status_code=404, detail="term is required!")
    else:
        rgx = re.compile(f'.*{term}.*', re.IGNORECASE)
        list_item = app.database["chatBotDB"].find({'data':rgx})
        temp_return_array = []
        if not list_item:
            raise HTTPException(status_code=404, detail="no data found!")
        else:
            for data in list_item:
                for item in data:
                    temp_return_array.append(data['data'])            
        return {"data": temp_return_array}


