from models import ProcessMinerModel
from database import database
from motor.motor_asyncio import AsyncIOMotorClient


async def get_all_process(db: AsyncIOMotorClient, skip: int = 0):
    all_processes = await db.processMinerTask.processMiner.find({}).skip(skip).to_list(length=None)
    return all_processes

async def get_process(db: AsyncIOMotorClient, id: int):
    process = await db.processMinerTask.processMiner.find_one({"id": id})
    return process

