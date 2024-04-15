import pm4py
import pandas as pd
import json
import pydotplus
import os
from fastapi import File, UploadFile, HTTPException
import io
import csv
from motor.motor_asyncio import AsyncIOMotorClient
import chardet
from models.ProcessMinerModel import Miner
import re


def xlsx_to_dataframe(xlsx_path):
    # excel okuma
    df = pd.read_excel(xlsx_path)
    # boşlukları temizleme
    df.columns = df.columns.str.replace(" ", "")

    # dataframe json kaydetme
    records = df.to_dict(orient='records')

    if records is not None:
        i = 1
        # Her kaydı düzenleme
        for record in records:
            new_record = {}
            # Ayırma ve dictionary'e ekleme
            for col in df.columns:
                keys = col.split(',')
                values = str(record[col]).split(',') if col in record else [""]
                new_record.update(zip(keys, values))
            if 'CaseID' in new_record:
                new_record['CaseID'] = int(new_record['CaseID'])
            record.clear()
            record.update(new_record)

    result_df = pd.DataFrame(records)

    return result_df
def generate_heuristics_net_image():
    try:
        current_script_directory = os.path.dirname(os.path.abspath(__file__))
        project_root_directory = os.path.abspath(os.path.join(current_script_directory, '..'))
        relative_path = "mock/PurchasingExample.xlsx"

        json_path = os.path.join(project_root_directory, relative_path)
        dataframe = xlsx_to_dataframe(json_path)
        dataframe = pm4py.format_dataframe(dataframe, case_id='CaseID', activity_key='Activity',
                                           start_timestamp_key='StartTimestamp', timestamp_key='CompleteTimestamp')
        log = pm4py.convert_to_event_log(dataframe)
        heu_net = pm4py.discover_heuristics_net(log)
        
        if heu_net is None:
            raise ValueError("Heuristics Net is not generated successfully.")
        

        dot_graph = pm4py.visualization.heuristics_net.visualizer.get_graph(heu_net=heu_net)
        dot_format = dot_graph.to_string()

        pydot_graph = pydotplus.graph_from_dot_data(dot_format)
        nodes = []
        edges = []

        for edge in pydot_graph.get_edges():
            source = edge.get_source().strip('"') 
            target = edge.get_destination().strip('"') 
            weight = edge.get_attributes().get('weight', 1.0) 

            edges.append({"source": source, "target": target, "weight": float(weight)})

            if {"id": source, "label": source} not in nodes:
                nodes.append({"id": source, "label": source})
            if {"id": target, "label": target} not in nodes:
                nodes.append({"id": target, "label": target})

        d3_data = {
            "nodes": nodes,
            "links": edges
        }

        json_data = json.dumps(d3_data, indent=2)
        relative_path_json = "image/d3_data.json"

        json_path_d3 = os.path.join(project_root_directory, relative_path_json)
        with open(json_path_d3, 'w') as json_file:
            json_file.write(json_data)

        return json.loads(json_data)
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
    
def xlsx_to_json(dict_data):
    modified_records = []
    if dict_data is not None:
        i = 1
        df = pd.DataFrame(dict_data)
        
        # Her kaydı düzenleme
        for _, record in df.iterrows():
            new_record = {}
            # Ayırma ve dictionary'e ekleme
            for col in df.columns:
                keys = col.split(',')
                values = str(record[col]).split(',') if col in record else [""]
                new_record.update(zip(keys, values))
            if 'CaseID' in new_record:
                new_record['CaseID'] = int(new_record['CaseID'])
            new_record = {re.sub(r' (\w)', lambda m: m.group(1).upper(), k.lower()): v for k, v in new_record.items()}
            new_record["processId"] = 1
            new_record["id"] = i
            i += 1
            modified_records.append(new_record)
    return modified_records


async def bulk_import(db: AsyncIOMotorClient, file: UploadFile = File(...)):
    try:
        data_list = []

        contents = await file.read()

        result = chardet.detect(contents)
        detected_encoding = result['encoding'] if result['encoding'] else 'utf-8'

        if file.filename.endswith(".csv"):
            csv_reader = csv.DictReader(io.StringIO(detected_encoding))
            data_list = list(csv_reader)
        elif file.filename.endswith(".xlsx"):
            df = pd.read_excel(io.BytesIO(contents))
            data_list = df.to_dict(orient='records')
        elif file.filename.endswith(".xes"):
            xes_log = pm4py.read_xes(io.BytesIO(contents))
            data_list = pm4py.convert_to_dataframe(xes_log)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        newDataList = xlsx_to_json(data_list)
        for data_item in newDataList:
            print(data_item)
            miner_data = Miner(**data_item)

            try:
                result = await db.processMinerTask.processMiner.insert_one(dict(miner_data))
                if result.inserted_id is not None:
                    print(f"Successfully inserted document with ID: {result.inserted_id}")
                else:
                    print("Failed to insert document.")
            except Exception as e:
                print(f"Error during insertion: {e}")
                continue

        return {"message": "Bulk import completed."}


    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during bulk import: {e}")