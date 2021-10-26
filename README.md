# mytube-videos-webiste

This project is a barebone video aggregator with basic account management and administrative fuctions. Database used is heroku's postgresql. Whole project is written in fastapi.
As a challange I tried to limit usage of javascript as much as possible.

docs:
dbinteractions.py contains all fuctions required to communicate with database. The connection to database is created in functions_and_utils.py
functions_and_utils.py contains functions extracted from the post/get handlers in oreder to reduce their size
main.py is a main file of the project
routers/admin.py contains handlers for strictly administrative actions
routers/general.py contains handlers for general actions
routers/user.py contains handlers for user(mostly post related) actions
routers/websockters.py manages websockets
video content is stored locally in video_files folder as well as profile pictures are in profile_pictures

```text

db tables:
                 List of relations
 Schema |       Name       | Type  |     Owner
--------+------------------+-------+----------------
 public | admin_posts      | table | -
 public | comments         | table | -
 public | comments_replies | table | -
 public | post_comments    | table | -
 public | user_bans        | table | -
 public | users            | table | -
 public | users_likes      | table | -
 public | users_pfps       | table | -
 public | users_post_likes | table | -
 public | videos           | table | -
 
 descriptions of db tables:
                         Table "public.admin_posts"
   Column    |            Type             | Collation | Nullable | Default
-------------+-----------------------------+-----------+----------+---------
 admark_id   | integer                     |           | not null |
 created_on  | timestamp without time zone |           | not null |
 description | character varying(5000)     |           |          |
 tags        | character varying(1000)     |           |          |
 title       | character varying(80)       |           |          |
 aps_id      | character varying(40)       |           |          |
 
                                             Table "public.comments"
   Column   |            Type             | Collation | Nullable |                   Default
------------+-----------------------------+-----------+----------+----------------------------------------------
 comment_id | integer                     |           | not null | nextval('comments_comment_id_seq'::regclass)
 user_id    | integer                     |           | not null |
 created_on | timestamp without time zone |           | not null |
 text       | character varying(3000)     |           | not null |
 
            Table "public.comments_replies"
  Column   |  Type   | Collation | Nullable | Default
-----------+---------+-----------+----------+---------
 parent_id | integer |           | not null |
 child_id  | integer |           | not null |
 
                     Table "public.post_comments"
   Column   |         Type          | Collation | Nullable | Default
------------+-----------------------+-----------+----------+---------
 post_id    | character varying(40) |           | not null |
 comment_id | integer               |           | not null |
 
                          Table "public.user_bans"
   Column   |            Type             | Collation | Nullable | Default
------------+-----------------------------+-----------+----------+---------
 user_id    | integer                     |           | not null |
 ban_data   | integer                     |           | not null |
 day_issued | timestamp without time zone |           | not null |
 
                                             Table "public.users"
    Column     |            Type             | Collation | Nullable |                Default
---------------+-----------------------------+-----------+----------+----------------------------------------
 user_id       | integer                     |           | not null | nextval('users_user_id_seq'::regclass)
 user_login    | character varying(50)       |           | not null |
 user_password | character varying(64)       |           | not null |
 created_on    | timestamp without time zone |           | not null |
 last_login    | timestamp without time zone |           |          |
 tag_whitelist | character varying(500)      |           |          |
 tag_blacklist | character varying(500)      |           |          |
 status        | boolean                     |           |          |
 warn_count    | integer                     |           |          |
 is_banned     | boolean                     |           |          |
 
               Table "public.users_likes"
   Column   |  Type   | Collation | Nullable | Default
------------+---------+-----------+----------+---------
 user_id    | integer |           | not null |
 comment_id | integer |           | not null |
 
                           Table "public.users_pfps"
       Column       |         Type          | Collation | Nullable | Default
--------------------+-----------------------+-----------+----------+---------
 user_id            | integer               |           | not null |
 profile_picture_id | character varying(40) |           | not null |
 
                  Table "public.users_post_likes"
 Column  |         Type          | Collation | Nullable | Default
---------+-----------------------+-----------+----------+---------
 user_id | integer               |           | not null |
 vid_id  | character varying(40) |           | not null |
 value   | smallint              |           | not null |
 
                            Table "public.videos"
   Column    |            Type             | Collation | Nullable | Default
-------------+-----------------------------+-----------+----------+---------
 user_id     | integer                     |           | not null |
 vid_id      | character varying(40)       |           | not null |
 created_on  | timestamp without time zone |           | not null |
 description | character varying(2000)     |           |          |
 tags        | character varying(500)      |           |          |
 title       | character varying(80)       |           |          |
 ```
