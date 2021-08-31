from hashlib import sha256
import datetime
from functions_and_utils import conn


def insert_user(login, password):
    passwd =sha256(password.encode('utf-8')).hexdigest()
    with conn.cursor() as curs:
        curs.execute('''INSERT INTO public.users(user_login, user_password, created_on, last_login,  tag_whitelist, tag_blacklist,status,warn_count,is_banned)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);''',
                     (login,passwd,datetime.datetime.now(), datetime.datetime.now(), '','',False,0,False))
        conn.commit()
    with conn.cursor() as curs:
        curs.execute('''SELECT * FROM public.users WHERE user_login=%s;''', (login,))
        return curs.fetchone()


def insert_photo(uid, pid):
    with conn.cursor() as curs:
        curs.execute('''INSERT INTO public.users_pfps(user_id, profile_picture_id) VALUES (%s,%s);''', (uid, pid))
        conn.commit()


def insert_adminpost(uid, descr, tags, title):
    with conn.cursor() as curs:
        curs.execute('''INSERT INTO public.admin_posts(admark_id, created_on ,description, tags, title) VALUES (%s,%s,%s,%s,%s);''', (uid,datetime.datetime.now(), descr,tags,title))
        conn.commit()


def check_login(login):
    with conn.cursor() as curs:
        curs.execute('''SELECT * FROM public.users WHERE user_login=%s;''', (login,))
        if len(curs.fetchall())==0:
            return False
        else:
            return True


def evaluate_credentials(login, password):
    passwd = sha256(password.encode('utf-8')).hexdigest()
    with conn.cursor() as curs:
        curs.execute('''SELECT * FROM public.users WHERE user_login=%s AND user_password =%s;''', (login,passwd))
        return curs.fetchone()


def delete_user(login):
    with conn.cursor() as curs:
        curs.execute('''DELETE FROM users WHERE user_login=%s RETURNING user_id;''', (login,))
        conn.commit()
        return curs.fetchone()


def delete_pfp(uid):
    with conn.cursor() as curs:
        curs.execute('''DELETE FROM users_pfps WHERE user_id=%s RETURNING profile_picture_id;''', (uid,))
        conn.commit()


def get_uid(login):
    with conn.cursor() as curs:
        curs.execute('''SELECT * FROM users WHERE user_login=%s;''', (login,))
        return curs.fetchone()


def insert_video(uid, vid,tags,description,title):
    with conn.cursor() as curs:
        curs.execute('''INSERT INTO public.videos(user_id, vid_id,title, created_on, description,  tags)
    VALUES (%s,%s,%s,%s,%s,%s);''',
                     (int(uid),vid,title,datetime.datetime.now(), description,tags))
        conn.commit()


def on_login(login):
    with conn.cursor() as curs:
        curs.execute('''UPDATE users SET last_login=%s WHERE user_login=%s;''',
                     (datetime.datetime.now(), login))


def get_video_by_id(vid):
    with conn.cursor() as curs:
        curs.execute('''SELECT * FROM videos WHERE vid_id=%s;''', (vid,))
        return curs.fetchone()


def get_user_by_id(uid):
    with conn.cursor() as curs:
        curs.execute('''SELECT * FROM users WHERE user_id=%s;''', (uid,))
        return curs.fetchone()


def find_pfp_by_id(uid):
    with conn.cursor() as curs:
        curs.execute('''SELECT * FROM users_pfps WHERE user_id=%s;''', (uid,))
        return curs.fetchone()


def get_video_by_user_id(uid):
    with conn.cursor() as curs:
        curs.execute('''SELECT * FROM videos WHERE user_id=%s;''', (uid,))
        return curs.fetchall()


def get_vpost_by_tag(querystr):
    with conn.cursor() as curs:
        curs.execute('''SELECT * FROM videos WHERE tags LIKE %s;''', (querystr,))
        return curs.fetchall()


def get_apost_by_tag(querystr):
    with conn.cursor() as curs:
        curs.execute('''SELECT * FROM admin_posts WHERE tags LIKE %s;''', (querystr,))
        return curs.fetchall()


def get_user_by_name(querystr):
    with conn.cursor() as curs:
        curs.execute('''SELECT * FROM users WHERE user_login LIKE %s;''', (querystr,))
        return curs.fetchall()


def get_post_by_content(querystr):
    with conn.cursor() as curs:
        curs.execute('''SELECT * FROM videos WHERE title LIKE %s OR description LIKE %s;''', (querystr,querystr))
        return curs.fetchall()


def get_apost_by_content(querystr):
    with conn.cursor() as curs:
        curs.execute('''SELECT * FROM admin_posts WHERE title LIKE %s OR description LIKE %s;''', (querystr,querystr))
        return curs.fetchall()


def isadmin(uid):
    with conn.cursor() as curs:
        curs.execute('''SELECT * FROM users WHERE user_id = %s;''', (uid,))
        val=curs.fetchone()
        if val is None:
            return False
        if val[7]:
            return True
        return False


def does_user_exist(login):
    with conn.cursor() as curs:
        curs.execute('''SELECT * FROM users WHERE user_login = %s;''', (login,))
        val = curs.fetchone()
        if val is None:
            return False
        return True


def get_apost_by_id(aps):
    with conn.cursor() as curs:
        curs.execute('''SELECT * FROM admin_posts WHERE aps_id = %s;''', (aps,))
        return curs.fetchone()


def insert_post_like(pid,uid,up):
    clear_user_like_on_post(pid,uid)
    if up is True:
        with conn.cursor() as curs:
            curs.execute(
                '''INSERT INTO public.users_post_likes(user_id, vid_id ,value) VALUES (%s,%s,%s);''',
                (uid, pid, 1))
        conn.commit()
    else:
        with conn.cursor() as curs:
            curs.execute(
                '''INSERT INTO public.users_post_likes(user_id, vid_id ,value) VALUES (%s,%s,%s);''',
                (uid, pid, -1))
        conn.commit()


def clear_user_like_on_post(pid,uid):
    with conn.cursor() as curs:
        curs.execute('''SELECT * FROM users_post_likes WHERE user_id = %s AND vid_id=%s;''', (uid,pid))
        val = curs.fetchone()
        if val is None:
            return
        curs.execute('''DELETE FROM users_post_likes WHERE user_id = %s AND vid_id=%s;''', (uid,pid))
        return


def get_post_points(pid):
    valpos=0
    valneg=0
    with conn.cursor() as curs:
        curs.execute(''' SELECT COUNT(*) FROM users_post_likes WHERE vid_id=%s AND value=1 ;''', (pid,))
        valpos = curs.fetchone()[0]
    with conn.cursor() as curs:
        curs.execute(''' SELECT COUNT(*) FROM users_post_likes WHERE vid_id=%s AND value=-1;''', (pid,))
        valneg = curs.fetchone()[0]
    return  valpos-valneg


def save_comment(pid, text,uid):
    comment_id=0
    with conn.cursor() as curs:
        curs.execute('''INSERT INTO public.comments(user_id, created_on, text) VALUES (%s,%s,%s) RETURNING comment_id;''', (uid,datetime.datetime.now() ,text))
        conn.commit()
        comment_id=curs.fetchone()[0]
    with conn.cursor() as curs:
        curs.execute('''INSERT INTO public.post_comments(post_id, comment_id) VALUES (%s,%s);''', (pid, comment_id))
        conn.commit()


def get_top_comments(pid):
    with conn.cursor() as curs:
        curs.execute('''SELECT comment_id FROM post_comments WHERE post_id=%s;''', (pid,))
        return curs.fetchall()


def get_comment_data(cid, indent):
    with conn.cursor() as curs:
        curs.execute('''SELECT user_id,created_on,text,comment_id FROM comments WHERE comment_id=%s;''', (cid,))
        cdata= curs.fetchone()
        curs.execute('''SELECT user_login FROM users WHERE user_id=%s;''', (cdata[0],))
        ulogin=curs.fetchone()[0]
        if ulogin is None:
            ulogin="deleted"
        return (cdata[0],cdata[1],cdata[2],ulogin,cdata[3])


def get_child_comments(cid):
    with conn.cursor() as curs:
        curs.execute('''SELECT child_id FROM comments_replies WHERE parent_id=%s;''', (cid,))
        return curs.fetchall()


def save_reply(cid, text,uid):
    comment_id = 0
    with conn.cursor() as curs:
        curs.execute(
            '''INSERT INTO public.comments(user_id, created_on, text) VALUES (%s,%s,%s) RETURNING comment_id;''',
            (uid, datetime.datetime.now(), text))
        conn.commit()
        comment_id = curs.fetchone()[0]
    with conn.cursor() as curs:
        curs.execute('''INSERT INTO public.comments_replies(parent_id, child_id) VALUES (%s,%s);''', (cid, comment_id))
        conn.commit()


def issue_ban(uid, duration):
    with conn.cursor() as curs:
        curs.execute('''INSERT INTO public.user_bans(user_id, ban_data ,day_issued) VALUES (%s,%s,%s);''', (uid,duration,datetime.datetime.now()))
        conn.commit()


def get_ban_by_uid(uid):
    with conn.cursor() as curs:
        curs.execute('''SELECT * FROM user_bans WHERE user_id=%s;''', (uid,))
        return curs.fetchall()


def unban(uid):
    with conn.cursor() as curs:
        curs.execute('''DELETE FROM public.user_bans WHERE user_id=%s;''', (uid,))
        conn.commit()