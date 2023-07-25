from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Post
from . import db
import json
import praw
import os
import requests
from currentsapi import CurrentsAPI
from joblib import delayed, Parallel

reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
    user_agent=os.getenv('REDDIT_USER_AGENT'),
    # username=os.getenv('REDDIT_USERNAME'),
    # password=os.getenv('REDDIT_PASSWORD')",
)

news_api = CurrentsAPI(api_key=os.getenv('CURRENTS_API_KEY'))

def search_news(keyword, limit=10):
    posts = news_api.search(keywords=keyword, limit=10, language='en')
    res = []
    for post in posts['news'][:limit]:
        res.append({'title': post['title'], 'text': post['description']})
    return res

def wiki_helper(page_id, char_limit=400):
    # print(id)
    extract_url = f"https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&exchars={char_limit}&pageids={page_id}"
    extract_response = requests.get(extract_url)
    extract_data = extract_response.json()

    extract_text = list(extract_data['query']['pages'].values())[0]['extract']
    title = list(extract_data['query']['pages'].values())[0]['title']
    return {'title': title, 'text':extract_text}

def wiki_search(keyword, char_limit=400, limit=10):
  # Search Wikipedia to get page IDs
    import time
    start = time.monotonic()
    search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={keyword}&format=json"
    search_response = requests.get(search_url)
    search_data = search_response.json()

    mid = time.monotonic()
    print('time to search: ', mid - start)

    # results = []
    # for page in search_data['query']['search'][:limit]:
    #     results.append(wiki_helper(page['pageid'], char_limit))

    results = Parallel(n_jobs=10)(delayed(wiki_helper)(page['pageid'], char_limit) for page in search_data['query']['search'][:limit])

    end = time.monotonic()
    print('time to get extracts: ', end - mid)
    print('total: ', end - start)
    return results

IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']

def is_image_link(url):
    return any(ext in url.lower() for ext in IMAGE_EXTENSIONS)

def search_reddit(keyword, subreddit='all', sort='new', limit=50):
    posts = reddit.subreddit(subreddit).search(keyword, sort=sort, time_filter='all', limit=limit)
    res = []
    for post in posts:
        if post.is_self or not is_image_link(post.url):
            res.append({'title': post.title, 'text': post.selftext})
    return res
      

views = Blueprint('views', __name__)



@views.route('/', methods=['GET','POST'])
@login_required
def home():
    if request.method == 'POST':
        text = request.form['search_text']
        # res = requests.get(f'https://www.reddit.com/search.json?q={text}')
        # res = res.json()
        # for post in res['data']['children'][:5]:
        #     print(post.get('data',{}).get('title'))

    return render_template("home.html", user=current_user)

posts_global = []

@views.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    # print(Post.query.all())
    # import time
    # start = time.monotonic()
    global posts_global
    # print(request.form.get('search_text')) # DO THE SEARCH HERE
    if request.form.get('search_text'):
        posts = wiki_search(request.form.get('search_text'))
        posts_global = posts
    else:
        posts = posts_global
    # print(posts)
    # mid = time.monotonic()
    # print('time to search: ', mid - start)
    user_categories = set()
    for post in current_user.saved:
        user_categories.add(post.category)
    # print(user_categories)
    user_categories = list(user_categories)
    user_categories = [x for x in user_categories if x not in [None,'']]
    # print('time for db: ', time.monotonic() - mid)
    # print('total: ', time.monotonic() - start)
    return render_template("search.html", posts=posts, user=current_user, user_categories=user_categories)

@views.route('/save', methods=['POST'])
def save_post():
    title = request.form['title']
    text = request.form['text']
    new_category = request.form['newCategory']
    category = request.form.get("category") if request.form.get("category") else new_category
    
    # print("new_category: ",new_category)
    # print("category: ",category)
    # print("title: ",title)
    data = json.dumps({'title': title, 'text': text})
    new_post = Post(data=data, category=category, user_id=current_user.id)
    db.session.add(new_post)
    db.session.commit()
    flash('Post saved!', category='success')
    return redirect(url_for('views.search'))

@login_required
@views.route('/saved', methods=['GET', 'POST'])
def saved():
    user_posts = []
    for post in current_user.saved:
        if post.data:
            user_posts.append({**json.loads(post.data),**{'category': post.category, 'id': post.id}})
        print("id: ",post.id)
    pivoted_data = {}

# Loop through each post and group them by category
    for post in user_posts:
        category_name = post.get('category')
        category_name = 'Uncategorized' if not category_name else category_name
        post_data = {k: v for k, v in post.items() if k != 'category'}
        
        if category_name not in pivoted_data:
            pivoted_data[category_name] = {'category': category_name, 'posts': [post_data]}
        else:
            pivoted_data[category_name]['posts'].append(post_data)

    # The variable 'pivoted_data' now contains the data pivoted by categories
    pivoted_list = list(pivoted_data.values())
    return render_template("saved.html", user=current_user, posts=pivoted_list)

# @login_required
# @views.route('/delete-post', methods=['POST'])
# def delete_post():  
#     post = json.loads(request.data) # this function expects a JSON from the INDEX.js file
#     print("post", post)
#     postId = post['postId']
#     print("postid:", postId)
#     post = Post.query.get(postId)
#     print("post: ", post)
#     if post:
#         print('yes')
#         if post.user_id == current_user.id:
#             db.session.delete(post)
#             db.session.commit()

#     return redirect(url_for('views.saved'))



@views.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    # Your code to delete the post with the given ID from the database
    # For example, you could use an ORM like SQLAlchemy to perform the deletion
    # Make sure to handle any errors or validations as needed
    # print("postid:", post_id)
    post = Post.query.get(post_id)
    # print("post: ", post)
    if post:
        if post.user_id == current_user.id:
            db.session.delete(post)
            db.session.commit()

    # After deleting the post, you can redirect the user to the page with the list of posts
    return redirect(url_for('views.saved'))