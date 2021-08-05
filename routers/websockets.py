from fastapi import APIRouter, WebSocket,Cookie

import dbinteractions
from functions_and_utils import templates,ALLOWED_EXTENSIONS,access_tokens,secret_key,MAX_NUM_LOGGED_IN,session_token_list
from typing import Optional
import json

ws = APIRouter(prefix="/websocket")


@ws.websocket('/up_post')
async def up_post(websocket: WebSocket, session_token: str = Cookie(None)):
    await websocket.accept()
    if session_token in session_token_list:
        data = await websocket.receive()
        data = json.loads(data['text'])
        dbinteractions.insert_post_like(data['vid'],access_tokens[session_token]['user_id'] ,True)


@ws.websocket('/down_post')
async def up_post(websocket: WebSocket, session_token: str = Cookie(None)):
    await websocket.accept()
    if session_token in session_token_list:
        data = await websocket.receive()
        data = json.loads(data['text'])
        dbinteractions.insert_post_like(data['vid'], access_tokens[session_token]['user_id'], False)
