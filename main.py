from typing import Optional
from fastapi import FastAPI, Request, APIRouter,Cookie,Depends, WebSocket
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pathlib import Path
import os
import psycopg2
import  dbinteractions
from routers import admin,general,user,websockets
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.security import OAuth2PasswordBearer
from functions_and_utils import templates,session_token_list,access_tokens



#configurating app
app = FastAPI()
app.include_router(general.general)
app.include_router(user.user)
app.include_router(admin.admin)
app.include_router(websockets.ws)

app.mount("/static",
          StaticFiles(directory=Path(__file__).parent.parent.absolute()/'static'),
          name='static')
app.mount("/video_files",
          StaticFiles(directory=Path(__file__).parent.parent.absolute()/'video_files'),
          name='video_files')
app.mount("/profile_pictures",
          StaticFiles(directory=Path(__file__).parent.parent.absolute()/'profile_pictures'),
          name='profile_pictures')

#pg:psql to open db

#email:mytube-auto@yandex.com
#login:mytube-auto
#passwd:vbrigbi4n5o;i8t905jhotnib...6u4g



@app.get("/")
def read_root(request:Request,session_token: str = Cookie(None)):
    if session_token in session_token_list:
        logged_in=True
        cuser_id=access_tokens[session_token]['user_id']
        isadmin=access_tokens[session_token]['status']
    else:
        logged_in=False
        cuser_id=''
        isadmin=False
    return templates.TemplateResponse('feed.html', {'request':request, 'logged_in':logged_in, 'cuser_id':cuser_id, 'isadmin':isadmin})

@app.get('/noresource')
def noresource():
    return 'hmm, It seems like the resource you are looking for does not exist.'
@app.get('/banned')
def noresource():
    return 'you have been banned'

# @app.websocket('/up_post')
# async def up_post(websocket: WebSocket):
#     print('CONNECTING...')
#     await websocket.accept()
#     print('CONNECTED')
#     while True:
#         data = await websocket.receive_json()
#         print(data)

