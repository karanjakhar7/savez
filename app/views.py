from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Post
from . import db
import json

views = Blueprint('views', __name__)

reddit_posts = [
    {
        "title": "First Post",
        "text": "Hello Reddit! This is my first post on this awesome platform."
    },
    {
        "title": "Exciting News",
        "text": "I just got accepted into my dream college! I can't believe it!"
    },
    {
        "title": "Subreddit Recommendation",
        "text": "Hey everyone, do you know any interesting subreddits about science and technology?"
    },
    {
        "title": "Funny Cat Video",
        "text": "Check out this hilarious cat video I found! It made my day."
    },
    {
        "title": "Discussion Topic",
        "text": "What are your thoughts on climate change? Let's have a meaningful discussion."
    }
]


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
    return render_template("search.html", posts=reddit_posts, user=current_user)

@views.route('/save', methods=['POST'])
def save_note():
    title = request.form['title']
    text = request.form['text']
    data = json.dumps({'title': title, 'text': text})
    new_note = Post(data=data, user_id=current_user.id)  #providing the schema for the note 
    db.session.add(new_note) #adding the note to the database 
    db.session.commit()
    flash('Post saved!', category='success')
    return redirect(url_for('views.search'))

@views.route('/saved', methods=['GET', 'POST'])
def saved():
    user_posts = []
    for post in current_user.saved:
        if post.data:
            user_posts.append(json.loads(post.data))
    print(current_user.saved)
    return render_template("saved.html", user=current_user, posts=user_posts)
