import sys
from slugify import slugify

def generate_slug(cursor, name, id, table_name):
    slug = slugify(name)
    
    cursor.execute(
        "SELECT exists(SELECT true FROM {0} WHERE slug=%s)".format(table_name), (
            slug,
        )
    )
    
    slug_already_exists = cursor.fetchone()[0]
    
    if not slug_already_exists or id == 0:
        return slug
    
    return "{0}-{1}".format(slug, id)

def username_from_id(cursor, user_id):
    try:
        cursor.execute(
            "SELECT username FROM bulbs_User WHERE id = %s", (user_id, )
        )
        
        username = cursor.fetchone()[0]
    except Exception as e:
        raise ValueError("failed to get username")
        
    return username
    
def number_of_threads(cursor, forum_id):
    try:
        cursor.execute(
            "SELECT count(id) FROM bulbs_Post WHERE subcategory_id = %s \
             AND parent_post IS NULL", (forum_id, )
         )
         
        views = cursor.fetchone()[0]
    except Exception as e:
        raise ValueError("failed to get amount of threads")
        
    return views
    
def number_of_posts(cursor, forum_id):
    try:
        cursor.execute(
            "SELECT count(id) FROM bulbs_Post WHERE subcategory_id = %s \
             AND parent_post IS NOT NULL", (forum_id, )
         )
         
        posts = cursor.fetchone()[0]
    except Exception as e:
        raise ValueError("failed to get amount of posts")
        
    return posts
    
def number_of_views(cursor, thread_id):
    try:
        cursor.execute(
            "SELECT views FROM bulbs_PostView WHERE post_id = %s", (thread_id, )
        )
        
        views = cursor.fetchone()[0]
    except ValueError as e:
        raise ValueError("failed to get amount of thread views")
        
    return views
    
def number_of_replies(cursor, thread_id):
    try:
        cursor.execute(
            "SELECT count(id) FROM bulbs_Post WHERE parent_post = %s", 
                (thread_id, )
        )
    
        replies = cursor.fetchone()[0]
    except ValueError as e:
        raise ValueError("failed to get amount of thread replies")

    return replies
    
def subcategory_title_from_id(cursor, subcategory_id):
    try:
        cursor.execute(
            "SELECT title FROM bulbs_Subcategory WHERE id = %s", (subcategory_id, )
        )
        
        title = cursor.fetchone()[0]
    except Exception as e:
        raise ValueError("failed to get subcat name from id")
        
    return title
    
def subcategory_moderators(cursor, subcategory_id):
    try:
        cursor.execute(
            "SELECT subcat_id, user_id, username FROM bulbs_Moderator \
             WHERE subcat_id = %s", (subcategory_id, )
        )
        
        mods = cursor.fetchone()[0]
    except TypeError as e:
        return None # no moderators for the forum in question
        
    return mods
    
def last_post(cursor, subcategory_id, parent_post=None):
    ''' parent_post is set to None by default, if parent post is provided then 
        we'll return the last post data for a thread
    '''
    
    if parent_post is not None:
        cursor.execute(
            "SELECT user_id, to_char(date, 'Mon FMDD, YYYY HH:MI AM') FROM bulbs_post \
             WHERE parent_post = %s ORDER BY date DESC LIMIT 1", (parent_post, )
         )
         
        data = cursor.fetchone()
    else:
        cursor.execute(
            "SELECT user_id, to_char(date, 'Mon FMDD, YYYY HH:MI AM'), id \
             FROM bulbs_post WHERE subcategory_id = %s ORDER BY date DESC LIMIT 1",
                 (subcategory_id, )
         )
         
        data = cursor.fetchone()
            
    if data is None:
        return None
    
    last_post = {
        "user_id": data[0],
        "date":    data[1]
    }

    last_post["username"] = username_from_id(cursor, last_post["user_id"])
    
    if parent_post is not None: 
        # this is true if this function was queried for a thread
        # no other information is required to display for a thread so we return the dict
        return last_post
    
    last_post["post_id"] = data[2] 
    
    try:
        cursor.execute(
            "SELECT parent_post FROM bulbs_Post WHERE subcategory_id = %s ORDER BY date \
             DESC LIMIT 1", (subcategory_id, )
         )
         
        last_post["root_id"] = cursor.fetchone()[0]
    except TypeError as e:
        cursor.execute(
            "SELECT id FROM bulbs_Post WHERE subcategory_id = %s ORDER BY date \
             DESC LIMIT 1", (forum_id, )
         )
         
        last_post["root_id"] = cursor.fetchone()[0]
        
    return last_post
    
def is_root_post(cursor, post_id):
    # this will return true if the post is the first in a thread
    try:
        cursor.execute("SELECT parent_post FROM bulbs_Post WHERE id = %s", (post_id, ))
        parent_id = cursor.fetchone()[0]
    except TypeError as e:
        return False
        
    return True
    
def thread_pages(cursor, thread_id):
    rows_per_page = 15        
    cursor.execute(
        "SELECT count(*) FROM bulbs_Post WHERE id = %s OR parent_post = %s",
            (thread_id, thread_id)
    )
    
    total_rows = cursor.fetchone()[0]
    pages = int(total_rows / 15 if total_rows % 15 == 0  else (total_rows / 15) + 1)
    
    return pages