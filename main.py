'''
Create a web application using the Twitter API that allows users to
search for tweets based on a keyword. It should display the results and
allow users to save their favorite tweets and categorize them by
creating tags.
Users should be able to view their saved tweets on a separate page.
This page should also allow users to modify the tags they have
associated with any saved tweet.
1. Implement Auth
2. Deploy the application on Netlify and Cockroach DB (free quota
for both services should be enough)
Following are optional but you get extra points if you can demonstrate
each of the following capabilities:
1. Basic Front-end: Use Material Design principles for all the pages
2. Basic NLP: Attach a sentiment label (positive, negative, neutral)
to each saved tweet
3. Real-time: Extra points if you can make the app real-time using
Web Sockets.'''


from flask import Flask
from flask import render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import tweepy
import requests


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


app = Flask(__name__)
app.config['SECRET_KEY'] = 'ssecretkey'


from app import create_app

app = create_app()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')