from fastapi import FastAPI, Request, APIRouter,Depends,HTTPException,Response,Cookie,status
from fastapi.responses import HTMLResponse, RedirectResponse,StreamingResponse
import  dbinteractions
from functions_and_utils import templates,ALLOWED_EXTENSIONS,access_tokens,secret_key,MAX_NUM_LOGGED_IN,session_token_list, ALLOWED_VIDEO_EXTENSIONS
import uuid, os

user = APIRouter(prefix="/user")


@user.get('/add_video')
def add_video(request:Request, session_token: str = Cookie(None)):
    if not session_token in session_token_list:
        return RedirectResponse('/general/login', status_code=302)
    return templates.TemplateResponse('add_video_post.html',{'request':request,
                                                             'logged_in':True,
                                                             'cuser_id':access_tokens[session_token]['user_id'],
                                                             'isadmin':access_tokens[session_token]['status']})



@user.post('/add_video')
async def add_video(request:Request, session_token: str = Cookie(None)):
    if not session_token in session_token_list:
        return RedirectResponse('/general/login', status_code=302)
    form_data = await request.form()
    title=form_data['Title']
    tags = form_data['Tags']
    file = form_data['file']
    description = form_data['Description']
    if file.filename != '' and file.filename.split('.')[-1] in ALLOWED_VIDEO_EXTENSIONS:
        newname =uuid.uuid4().int
        while os.path.exists(os.path.join('../video_files/', str(newname))):
            newname = uuid.uuid4().int
        file.filename = newname
        contents=await file.read()
        #print(os.listdir())
        with open(os.path.join('video_files', str(file.filename)), 'wb+') as f:
            f.write(contents)
        uid = dbinteractions.get_uid(access_tokens[session_token]['login'])[0];
        if len(description)>2000:
            description=description[:2000]
        if len(tags)>500:
            tags=tags[:500]
        dbinteractions.insert_video(uid,newname,tags,description,title)
    return

