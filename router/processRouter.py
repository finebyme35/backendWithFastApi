from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from controller import ProcessMinerController, HeuristicNetImageController
from database import database
from models import ProcessMinerModel
from fastapi.responses import  JSONResponse
from fastapi import APIRouter, UploadFile, HTTPException


processRouter = APIRouter()

@processRouter.post("/process/", response_model=list[ProcessMinerModel.Miner])
async def read_items(skip: int = 0, client: AsyncIOMotorClient = Depends(database.get_database)):
    allProcess = await ProcessMinerController.get_all_process(client, skip=skip)
    return allProcess

@processRouter.post("/process/id", response_model=ProcessMinerModel.Miner)
async def read_item(request_body: ProcessMinerModel.MinerId, client: AsyncIOMotorClient = Depends(database.get_database)):
    id = request_body.id
    if id is None:
        raise HTTPException(status_code=400, detail="ID is required in the request body")
    
    process = await ProcessMinerController.get_process(client, id)
    if process is None:
        raise HTTPException(status_code=404, detail="Process not found")
    
    return process


@processRouter.post("/heuristics-net-image")
def get_heuristics_net_image():
    json_content = HeuristicNetImageController.generate_heuristics_net_image()
    if json_content is not None:
        return JSONResponse(content={"jsonFile": json_content})
    else:
        return JSONResponse(content={"error": "Failed to generate Heuristics Net image"}, status_code=500)
    
@processRouter.post("/bulk-import")
async def bulk_import_endpoint(file: UploadFile = UploadFile(...), client: AsyncIOMotorClient = Depends(database.get_database)):
    try:
        print(file)
        result = await HeuristicNetImageController.bulk_import(client, file)
        return {"message": "Data imported successfully", "result": result}
    except HTTPException as e:
        return {"error": str(e)}