from fastapi import FastAPI, Request, APIRouter,Depends,HTTPException,Response,Cookie,status
from fastapi.responses import HTMLResponse, RedirectResponse,StreamingResponse
import  dbinteractions
from functions_and_utils import templates,ALLOWED_EXTENSIONS,access_tokens,secret_key,MAX_NUM_LOGGED_IN,session_token_list, ALLOWED_VIDEO_EXTENSIONS
import uuid, os

admin = APIRouter(prefix="/admin")


@admin.get('/add_adminpost')
def add_adminpost(request:Request, session_token: str = Cookie(None)):
    print('ok')
    if session_token not in session_token_list:
        return RedirectResponse('/general/login', status_code=302)
    if not dbinteractions.isadmin(access_tokens[session_token]['user_id']):
        return RedirectResponse('/general/login', status_code=302)
    return templates.TemplateResponse('add_adminpost.html',{'request':request,
                                                            'logged_in':True,
                                                            'cuser_id':access_tokens[session_token]['user_id'],
                                                            'isadmin': access_tokens[session_token]['status']})


@admin.post('/add_adminpost')
async def add_adminpost_backgr(request:Request, session_token: str = Cookie(None)):
    if session_token not in session_token_list:
        return RedirectResponse('/general/login', status_code=302)
    if not dbinteractions.isadmin(access_tokens[session_token]['user_id']):
        return RedirectResponse('/general/login', status_code=302)
    form_data = await request.form()
    print(form_data)
    descr= form_data['Description'] if len(form_data['Description'])<5000 else form_data['Description'][:5000]
    tags=form_data['Tags'] if len(form_data['Tags'])<1000 else form_data['Tags'][:1000]
    dbinteractions.insert_adminpost(access_tokens[session_token]['user_id'],descr,tags,form_data['Title'])
    return RedirectResponse('/general/login', status_code=302)


@admin.get('/action')
async def perform_admin_action(request:Request, session_token: str = Cookie(None)):
    if session_token in session_token_list:
        logged_in = True
        cuser_id = access_tokens[session_token]['user_id']
        isadmin = access_tokens[session_token]['status']
    else:
        logged_in = False
        cuser_id = ''
        isadmin = False
        return RedirectResponse('/', status_code=302)
    return templates.TemplateResponse('admin_panel.html',{'request':request,
                                                          'logged_in':True,
                                                          'cuser_id':access_tokens[session_token]['user_id'],
                                                          'isadmin': access_tokens[session_token]['status']})


@admin.post('/action/{action_number}')
async def recive_admin_action(action_number:int ,request:Request, session_token: str = Cookie(None)):
    if session_token in session_token_list:
        logged_in = True
        cuser_id = access_tokens[session_token]['user_id']
        isadmin = access_tokens[session_token]['status']
    else:
        logged_in = False
        cuser_id = ''
        isadmin = False
        return RedirectResponse('/', status_code=302)
    if action_number==1:
        form_data = await request.form()
        dbinteractions.issue_ban(form_data['user_id'], form_data['duration'])
    elif action_number==2:
        form_data = await request.form()
        dbinteractions.issue_ban(form_data['user_id'],-1)
    elif action_number==3:
        form_data = await request.form()
        dbinteractions.unban(form_data['user_id'])

    return templates.TemplateResponse('admin_panel.html', {'request': request,
                                                           'logged_in': True,
                                                           'cuser_id': access_tokens[session_token]['user_id'],
                                                           'isadmin': access_tokens[session_token]['status']})