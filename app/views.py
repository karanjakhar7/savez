from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Post
from . import db
import json
import praw

reddit = praw.Reddit(
    client_id="9uCqLjONJDLFDh8vDb22-g",
    client_secret="kH8x0BrGo1OeTDzpz5pA3CrZWyBTuQ",
    user_agent="Temp by /u/thecockydev",
    # username="thecockydev",
    # password="password10026",
)

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

# reddit_posts = [
#     {
#         "title": "First Post",
#         "text": "Hello Reddit! This is my first post on this awesome platform."
#     },
#     {
#         "title": "Exciting News",
#         "text": "I just got accepted into my dream college! I can't believe it!"
#     },
#     {
#         "title": "Subreddit Recommendation",
#         "text": "Hey everyone, do you know any interesting subreddits about science and technology?"
#     },
#     {
#         "title": "Funny Cat Video",
#         "text": "Check out this hilarious cat video I found! It made my day."
#     },
#     {
#         "title": "Discussion Topic",
#         "text": "What are your thoughts on climate change? Let's have a meaningful discussion."
#     }
# ]


@views.route('/', methods=['GET','POST'])
def home():
    if request.method == 'POST':
        text = request.form['search_text']
        # res = requests.get(f'https://www.reddit.com/search.json?q={text}')
        # res = res.json()
        # for post in res['data']['children'][:5]:
        #     print(post.get('data',{}).get('title'))

    return render_template("home.html", user=current_user)

@views.route('/search', methods=['GET', 'POST'])
def search():
    # print(Post.query.all())
    print(request.form.get('search_text')) # DO THE SEARCH HERE

    reddit_posts = search_reddit(request.form.get('search_text'))
    print(reddit_posts)
    user_categories = set()
    for post in current_user.saved:
        user_categories.add(post.category)
    # print(user_categories)
    return render_template("search.html", posts=reddit_posts, user=current_user, user_categories=list(user_categories))

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

@login_required
@views.route('/delete-post', methods=['POST'])
def delete_post():  
    post = json.loads(request.data) # this function expects a JSON from the INDEX.js file
    postId = post['postId']
    post = Post.query.get(postId)
    if post:
        if post.user_id == current_user.id:
            db.session.delete(post)
            db.session.commit()

    return redirect(url_for('views.saved'))
