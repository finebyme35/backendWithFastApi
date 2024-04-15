from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI
import os
import json

DATABASE_URL = "mongodb://localhost:27017"
DB_NAME = "processMinerTask"
COLLECTION_NAME = "processMiner"

# diğer dosyalarda kullanmak için yazılmıştır.
client = AsyncIOMotorClient(DATABASE_URL)
db = client[DB_NAME]


async def get_database() -> AsyncIOMotorClient:
    return client

async def init_db(app: FastAPI):
    app.mongodb_client = AsyncIOMotorClient(DATABASE_URL)
    app.mongodb = app.mongodb_client[DB_NAME]
    app.collection = app.mongodb[COLLECTION_NAME]
    # DİKKAT!!!! Database verilerini silmek ve tekrar mock data yüklemek için yazılmıştır.
    # await destroy_and_bulk_import(app)

    # database yoksa kurulup mockData import işlemi
    if DB_NAME not in await app.mongodb_client.list_database_names():
        await app.mongodb_client.drop_database(DB_NAME)
        await bulk_import(app)

    # database mevcut ancak içinde veri yok bulk import mock data işlemi
    if await app.mongodb.processMiner.count_documents({}) == 0:
        await bulk_import(app)

async def close_db(app: FastAPI):
    app.mongodb_client.close()



async def bulk_import(app: FastAPI):
    try:
        current_script_directory = os.path.dirname(os.path.abspath(__file__))
        project_root_directory = os.path.abspath(os.path.join(current_script_directory, '..'))
        relative_path = "mock/mockData.json"

        json_path = os.path.join(project_root_directory, relative_path)
        data_list = []

        if json_directory.endswith(".json"):
            json_path = os.path.join(json_directory, json_directory)
            with open(json_path, "r") as json_file:
                data_list.append(json.load(json_file))

        for data_item in data_list[0]:
            await app.mongodb.processMiner.insert_one(data_item)
    except Exception as e:
        print(f"Error during bulk import: {e}")

async def destroy_and_bulk_import(app: FastAPI):
    try:
        # tüm database kaldırır.
        await app.mongodb.processMiner.delete_many({})

        return {"status": "success", "message": "Database destroyed and bulk import completed"}
    except Exception as e:
        return {"status": "error", "message": f"Error during destroy and bulk import: {e}"}

