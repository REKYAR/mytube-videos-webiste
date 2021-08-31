import re
from fastapi.templating import Jinja2Templates
import psycopg2
import dbinteractions
import datetime

templates = Jinja2Templates(directory='templates')
#consts
ALLOWED_EXTENSIONS = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']
ALLOWED_VIDEO_EXTENSIONS=['webm']
MAX_NUM_LOGGED_IN=10



with open('db_config.cfg','r') as f:
    DATABASE_URL=f.read().strip()
#adjustment for heroku hosting
#DATABASE_URL = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL, sslmode='require')


#adjustment for heroku hosting
#secret_key = os.environ.get('secret_key')
with open('secret_key.cfg','r') as f:
    secret_key=f.read().strip()

access_tokens={}
session_token_list=[]


def build_post_comment_tree(pid):
    idlist=[]
    completelist=[]
    top_level_comments=dbinteractions.get_top_comments(pid)
    if not top_level_comments:
        return  completelist
    for thread in top_level_comments:
        fullthread=build_comment_tree(thread, 0)
        if fullthread is not None:
            idlist+=fullthread
    for comment, indent in idlist:
        completelist.append((dbinteractions.get_comment_data(comment,indent),indent))
    return completelist


def build_comment_tree(cid, indent):
    crlist=[(cid, indent)]
    child_comments= dbinteractions.get_child_comments(cid)
    if not child_comments:
        return crlist
    else:
        for comment in child_comments:
            crlist += build_comment_tree(comment, indent + 1)
        return crlist


def check_for_ban(uid):
    bans=dbinteractions.get_ban_by_uid(uid)
    print(bans)
    if not bans:
        return False
    else:
        for ban in bans:
            print(ban)
            if ban[1]==-1:
                print('indef')
                return True
            if  ban[2]+datetime.timedelta(days=ban[1])> datetime.datetime.now():
                print('fin')
                return True
        return False


#     def build_thread(cid, comtree):
#
#         offset = 0
#         for index, item in enumerate(comtree):
#             if str(item['_id']) == cid:
#                 root_index = index
#                 root = item
#                 break
#         comms = list(comments.find({'reply_id': cid}))
#         comms = comms[::-1]
#         # print(comms)
#         if len(comms) == 0:
#             return comtree
#         else:
#             for comment in comms:
#                 comment['depth'] = root['depth'] + 1
#                 # com_id = str(comment.get('_id'))
#                 for comment_media in comment['media'].values():
#                     if not os.path.exists(path.join(app.config['DOWNLOAD_FOLDER'], comment_media)):
#                         with open(path.join(app.config['DOWNLOAD_FOLDER'], comment_media), 'wb+') as my_file:
#                             files.download_to_stream(ObjectId(comment_media), my_file)
#                     comtree.insert(root_index + 1, comment)
#             build_thread(str(comment['_id']), comtree)
#             return comtree