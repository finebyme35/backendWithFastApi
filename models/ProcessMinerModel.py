from typing import List, Optional
from fastapi import HTTPException
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
from database import database
from pydantic import BaseModel
import pandas as pd
import pm4py
from bson import ObjectId

class EventLogModel(BaseModel):
    log_path: str
class MinerId(BaseModel):
    id: int
class Miner(BaseModel):
    _id: ObjectId
    caseId: int
    startTimestamp: str
    completeTimestamp: str
    activity: str
    resource: str
    role: str
    processId: Optional[int]
    id: Optional[int]


class ProcessMiner:
    collection = database.db.processes

    @staticmethod
    async def mine_process(log_path: str) -> str:
        # dosyaları ayırma
        file_extension = log_path.split('.')[-1].lower()

        if file_extension == 'csv':
            dataframe = pd.read_csv(log_path, sep=',')
        elif file_extension == 'xlsx':
            dataframe = pd.read_excel(log_path)
        elif file_extension == 'xes':
            event_log = pm4py.read_xes(log_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        if file_extension != 'xes':
            # pm4py için dataframe
            dataframe = pm4py.format_dataframe(dataframe, case_id='Case İD', activity_key='Activity',
                                               start_timestamp_key='Start Timestamp', timestamp_key='Complete Timestamp')

            # dataframe log a çevirme
            event_log = pm4py.convert_to_event_log(dataframe)

        # heuristic uygulama
        net, initial_marking, final_marking = heuristics_miner.apply_heu(event_log, dependency_threshold=0.99)

        # model kaydetme
        process_data = {
            "net": net,
            "initial_marking": initial_marking,
            "final_marking": final_marking
        }
        result = await ProcessMiner.collection.insert_one(process_data)

        return str(result.inserted_id)

    @staticmethod
    async def get_process(process_id: str) -> dict:
        process = await ProcessMiner.collection.find_one({"_id": process_id})
        if process is None:
            raise HTTPException(status_code=404, detail="Process not found")
        return process
