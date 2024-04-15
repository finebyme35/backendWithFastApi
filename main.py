from fastapi import FastAPI, Depends
from router.processRouter import processRouter
from database import database
from fastapi.middleware.cors import CORSMiddleware
from functools import partial

app = FastAPI()

perform_bulk_import = False

partial_init_db = partial(database.init_db, app=app)
partial_close_db = partial(database.close_db, app=app)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(processRouter, dependencies=[Depends(database.get_database)])

app.add_event_handler("startup", partial_init_db)
app.add_event_handler("shutdown", partial_close_db)
