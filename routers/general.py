from typing import Optional
from fastapi import FastAPI, Request, APIRouter,Depends,HTTPException,Response,Cookie,status
from fastapi.responses import HTMLResponse, RedirectResponse,StreamingResponse
import os
import datetime
from hashlib import sha256
import  dbinteractions
import functions_and_utils
from functions_and_utils import templates,ALLOWED_EXTENSIONS,access_tokens,secret_key,MAX_NUM_LOGGED_IN,session_token_list
import uuid
from fastapi_sessions import SessionCookie
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from operator import itemgetter

general = APIRouter(prefix="/general")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@general.get("/register" ,response_class=HTMLResponse)
def read_item(request:Request,session_token: str = Cookie(None)):
    if session_token in session_token_list:
        logged_in = True
        cuser_id = access_tokens[session_token]['user_id']
        isadmin=access_tokens[session_token]['status']
        return templates.TemplateResponse('feed.html', {'request': request, 'logged_in': logged_in, 'cuser_id':cuser_id, 'isadmin':isadmin})
    else:
        logged_in = False
        cuser_id = ''
        isadmin = False

    return templates.TemplateResponse('register.html',{'request':request, 'logged_in':logged_in, 'cuser_id':cuser_id, 'isadmin':isadmin})


@general.post('/register')
async def validate_register(request:Request, response:Response):
    form_data = await request.form()
    #print(form_data)
    login=form_data['login']
    if login=='':
        return templates.TemplateResponse('register.html', {'request': request, 'message':'Login cannot be empty'})
    if dbinteractions.check_login(login):
        return templates.TemplateResponse('register.html', {'request': request, 'message': 'Login already taken'})

    password=form_data['password']
    password2=form_data['password_repeated']
    if password!=password2 or password2=='' or password2=='':
        return templates.TemplateResponse('register.html', {'request': request, 'message':'Nonempty passwords must match'})

    user_saved = dbinteractions.insert_user(login, password)

    file=form_data['file']
    if file.filename!='' and file.filename.split('.')[-1] in ALLOWED_EXTENSIONS:
        newname =uuid.uuid4().int
        while os.path.exists(os.path.join('../profile_pictures/', str(newname))):
            newname = uuid.uuid4().int
        file.filename = newname
        contents=await file.read()
        #print(os.listdir())
        with open(os.path.join('profile_pictures', str(file.filename)), 'wb+') as f:
            f.write(contents)
    else:
        newname=-1

    dbinteractions.insert_photo(user_saved[0], newname)

    session_token = sha256(
        f"{secret_key}{login}{password}{datetime.datetime.today()}".encode()).hexdigest()
    access_tokens[session_token] = {'login': user_saved[1], 'status': user_saved[7], 'tag_whitelist': user_saved[5],
                                    'tag_blacklist': user_saved[6], 'user_id':user_saved[0]}
    session_token_list.append(session_token)
    if len(access_tokens) > MAX_NUM_LOGGED_IN:
        tmp = session_token_list[0]
        session_token_list.pop(0)
        access_tokens.pop(tmp)
    logged_in=True
    isadmin = dbinteractions.isadmin(user_saved[0])

    #response = RedirectResponse('/', status_code=302)
    response = templates.TemplateResponse('feed.html',{'request':request, 'logged_in':logged_in, 'cuser_id':user_saved[0],'isadmin':isadmin})
    response.set_cookie(key='session_token', value=session_token, max_age=43200)
    return response


#dbinteractions.insert_user(login, password, conn)

@general.get("/login" ,response_class=HTMLResponse)
def read_item(request:Request,session_token: str = Cookie(None)):
    #print(access_tokens)
    if session_token in session_token_list:
        return RedirectResponse('/',status_code=302)
    return templates.TemplateResponse('login.html',{'request':request, 'logged_in':False})


@general.post("/login")
async def read_item(response: Response,request: Request,form_data:OAuth2PasswordRequestForm=Depends(),  session_token: str = Cookie(None)):
    if session_token in session_token_list:
        logged_in = True
        cuser_id = access_tokens[session_token]['user_id']
        isadmin=access_tokens[session_token]['status']
    else:
        logged_in = False
        cuser_id = ''
        isadmin = False
    if session_token in session_token_list:
        logged_in=True
        return  templates.TemplateResponse('feed.html',{'request':request, 'logged_in':logged_in})
        #return RedirectResponse('/',status_code=302)
    user_data = dbinteractions.evaluate_credentials(form_data.username, form_data.password)
    #print(user_data)
    if user_data is None:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    else:
        if functions_and_utils.check_for_ban(user_data[0]) is True:
            return RedirectResponse('/banned', status_code=302)
        dbinteractions.on_login(user_data[1])
        #update last login
        session_token = sha256(
            f"{secret_key}{form_data.username}{form_data.password}{datetime.datetime.today()}".encode()).hexdigest()
        access_tokens[session_token]={'login':user_data[1],'status':user_data[7],'tag_whitelist':user_data[5],'tag_blacklist':user_data[6], 'user_id':user_data[0]}
        session_token_list.append(session_token)
        if len(access_tokens)>MAX_NUM_LOGGED_IN:
            tmp=session_token_list[0]
            session_token_list.pop(0)
            access_tokens.pop(tmp)
        logged_in=True
        response = templates.TemplateResponse('feed.html', {'request': request, 'logged_in': logged_in, 'cuser_id':user_data[0], 'isadmin':user_data[7]})
        #response=RedirectResponse('/',status_code=302)
        response.set_cookie(key='session_token', value=session_token,max_age=43200)
        return response


@general.get("/logout")
def logout(request:Request,session_token: str = Cookie(None)):
    print(session_token)
    print(session_token_list)
    print(access_tokens)
    if session_token in session_token_list:
        session_token_list.pop(session_token_list.index(session_token))
        access_tokens.pop(session_token)
    return templates.TemplateResponse('feed.html', {'request': request, 'logged_in': False})


@general.get("/remove_account")
def remove_account(session_token: str = Cookie(None)):
    if session_token in session_token_list:
        print(access_tokens[session_token]['login'])
        uid=dbinteractions.delete_user(access_tokens[session_token]['login'])[0]
        pid=dbinteractions.delete_pfp(uid)[0]
        os.remove(os.path.join('profile_pictures', pid))
        #delete from fileststem
        session_token_list.pop(session_token_list.index(session_token))
        access_tokens.pop(session_token)
    return RedirectResponse('/', status_code=302)


@general.get('/video_post/{vid}')
async def inspect_video(vid, request:Request,session_token: str = Cookie(None)):
    if session_token in session_token_list:
        logged_in = True
        cuser_id = access_tokens[session_token]['user_id']
        isadmin=access_tokens[session_token]['status']
    else:
        logged_in = False
        cuser_id = ''
        isadmin=False
    qresult = dbinteractions.get_video_by_id(vid)
    if qresult is None:
        return RedirectResponse('/noresource',status_code=302)
    usr = dbinteractions.get_user_by_id(qresult[0])
    if usr is None:
        usr=['x','deleted']
    pval=dbinteractions.get_post_points(vid)
    comms=functions_and_utils.build_post_comment_tree(vid)
    return templates.TemplateResponse('inspect_video_post.html',{
        'request':request,
        'video_title':qresult[5],
        'upload_date':qresult[2],
        'vid':vid,
        'video_tags':qresult[4].split(';'),
        'video_description':qresult[3],
        'user_id':qresult[0],
        'user_name':usr[1],
        'logged_in':logged_in,
        'cuser_id':cuser_id,
        'isadmin':isadmin,
        "pval":pval,
        "comms":comms
    })

@general.get('/vpost/{vid}')
async def inspect_vpost(vid, request:Request):
    qresult = dbinteractions.get_video_by_id(vid)
    if qresult is None:
        return RedirectResponse('/noresource',status_code=302)
    def iterfile():
        with open(os.path.join('video_files/',qresult[1]), mode="rb") as file:
            yield from file

    return StreamingResponse(iterfile(), media_type='video/webm')

@general.get('/user/{uid}')
async  def inspect_profile(uid, request:Request,session_token: str = Cookie(None)):
    if session_token in session_token_list:
        logged_in = True
        cuser_id = access_tokens[session_token]['user_id']
        isadmin=access_tokens[session_token]['status']
    else:
        logged_in = False
        cuser_id = ''
        isadmin=False
    qresult = dbinteractions.get_user_by_id(uid)
    if qresult is None:
        return RedirectResponse('/noresource',status_code=302)
    q2result=dbinteractions.find_pfp_by_id(qresult[0])
    if q2result is None:
        return RedirectResponse('/noresource',status_code=302)
    if q2result[1]=='-1':
        ppath=os.path.join('../../static/', 'defaults/pfp.png')
    else:
        ppath=os.path.join('../../profile_pictures/', q2result[1])
    return templates.TemplateResponse('inspect_profile.html',{
        'request':request,
        'pic_id':ppath,
        'user_id':qresult[0],
        'user_login':qresult[1],
        'last_login':qresult[4],
        'created_on':qresult[3],
        'status':'admin' if qresult[7] is True else 'regular user',
        'is_banned':qresult[9],
        'logged_in':logged_in,
        'cuser_id':cuser_id,
        'isadmin':isadmin
    })

@general.get('/user_posts/{uid}')
async def get_user_comments(uid, request:Request,session_token: str = Cookie(None)):
    if session_token in session_token_list:
        logged_in = True
        cuser_id = access_tokens[session_token]['user_id']
        isadmin=access_tokens[session_token]['status']
    else:
        logged_in = False
        cuser_id = ''
        isadmin=False
    reslist=[]
    qresult=dbinteractions.get_video_by_user_id(uid)
    if qresult is None:
        reslist.append('this user has not posted anything')
    else:
        reslist=list(map(itemgetter(1),qresult))
    return templates.TemplateResponse('view_posts.html',{
        'request':request,
        'content_list':reslist,
        'logged_in':logged_in,
        'cuser_id':cuser_id,
        'isadmin':isadmin
    })

@general.get('/query')
async def search_for(request:Request, query:str,session_token: str = Cookie(None)):
    if session_token in session_token_list:
        logged_in = True
        cuser_id = access_tokens[session_token]['user_id']
        isadmin=access_tokens[session_token]['status']
    else:
        logged_in = False
        cuser_id = ''
        isadmin=False
    data = query.strip()
    print(data)
    if data[0]=='#':
        results = dbinteractions.get_vpost_by_tag('%'+data[1:]+'%')
        results = list(zip(['2']*len(results),results))
    elif data[0]=='@':
        results = dbinteractions.get_user_by_name('%'+data[1:]+'%')
        results = list(zip(['1'] * len(results), results))
    elif data[0] == '$':
        results = dbinteractions.get_apost_by_tag('%' + data[1:] + '%')
        results = list(zip(['3'] * len(results), results))
    else:
        results = dbinteractions.get_post_by_content('%'+data+'%')
        results = list(zip(['2'] * len(results), results))
        results2=dbinteractions.get_apost_by_content('%'+data+'%')
        results2 = list(zip(['3'] * len(results2), results2))
        results=results + results2
    print(results)
    return templates.TemplateResponse('query_results.html',{'request':request,
                                                            'results':results,
                                                            'logged_in':logged_in,
                                                            'cuser_id':cuser_id,
                                                            'isadmin':isadmin})


@general.get('/admin_post/{pid}')
async def inspect_apost(pid, request:Request,session_token: str = Cookie(None)):
    if session_token in session_token_list:
        logged_in = True
        cuser_id = access_tokens[session_token]['user_id']
        isadmin=access_tokens[session_token]['status']
    else:
        logged_in = False
        cuser_id = ''
        isadmin=False
    qresult = dbinteractions.get_apost_by_id(pid)
    if qresult is None:
        return RedirectResponse('/noresource',status_code=302)
    usr = dbinteractions.get_user_by_id(qresult[0])
    if usr is None:
        usr=['x','deleted']
    return templates.TemplateResponse('inspect_video_post.html',{
        'request':request,
        'title':qresult[4],
        'upload_date':qresult[1],
        'tags':qresult[3].split(';'),
        'video_description':qresult[2],
        'user_id':qresult[0],
        'user_name':usr[1],
        'logged_in':logged_in,
        'cuser_id':cuser_id,
        'isadmin':isadmin
    })

@general.get('/add_comment/{pid}')
async def add_comment(pid, request:Request,session_token: str = Cookie(None)):
    if session_token in session_token_list:
        logged_in = True
        cuser_id = access_tokens[session_token]['user_id']
        isadmin=access_tokens[session_token]['status']
        return templates.TemplateResponse('add_comment.html', {
            'request': request,
            'logged_in': logged_in,
            'cuser_id': cuser_id,
            'isadmin': isadmin,
            'pid':pid
        })
    else:
        return RedirectResponse('/general/video_post/'+pid, status_code=302)


@general.post('/add_comment/{pid}')
async def post_comment(pid, request:Request,session_token: str = Cookie(None)):
    if session_token in session_token_list:
        logged_in = True
        cuser_id = access_tokens[session_token]['user_id']
        isadmin=access_tokens[session_token]['status']
    else:
        logged_in = False
        cuser_id = ''
        isadmin=False
        return RedirectResponse('/general/video_post/'+pid, status_code=302)
    form_data = await request.form()
    comment_text = form_data['Comment']
    dbinteractions.save_comment(pid, comment_text, cuser_id)
    return RedirectResponse('/general/video_post/' + pid, status_code=302)


@general.get('/add_reply/{pid}/{cid}')
async def add_reply(cid,pid, request:Request,session_token: str = Cookie(None)):
    if session_token in session_token_list:
        logged_in = True
        cuser_id = access_tokens[session_token]['user_id']
        isadmin=access_tokens[session_token]['status']
        return templates.TemplateResponse('add_reply.html', {
            'request': request,
            'logged_in': logged_in,
            'cuser_id': cuser_id,
            'isadmin': isadmin,
            'pid':pid,
            'cid':cid
        })
    else:
        return RedirectResponse('/general/video_post/'+pid, status_code=302)


@general.post('/add_reply/{pid}/{cid}')
async def post_comment(pid,cid, request:Request,session_token: str = Cookie(None)):
    if session_token in session_token_list:
        logged_in = True
        cuser_id = access_tokens[session_token]['user_id']
        isadmin=access_tokens[session_token]['status']
    else:
        logged_in = False
        cuser_id = ''
        isadmin=False
        return RedirectResponse('/general/video_post/'+pid, status_code=302)
    form_data = await request.form()
    comment_text = form_data['Comment']
    dbinteractions.save_reply(cid, comment_text, cuser_id)
    return RedirectResponse('/general/video_post/' + pid, status_code=302)