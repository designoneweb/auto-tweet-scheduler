import os
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify
import openai
import tweepy
from dotenv import load_dotenv
import threading
from threading import Thread
import time

app = Flask(__name__)

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET_KEY = os.getenv("TWITTER_API_SECRET_KEY")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET_KEY)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)

SCHEDULED_POSTS_FILE = "scheduled_posts.json"


def read_scheduled_posts():
    if not os.path.exists(SCHEDULED_POSTS_FILE):
        return []

    try:
        with open(SCHEDULED_POSTS_FILE, "r") as file:
            content = file.read()
            if not content:
                return []
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def write_scheduled_posts(scheduled_posts):
    with open(SCHEDULED_POSTS_FILE, "w") as file:
        json.dump(scheduled_posts, file)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/test_twitter_credentials")
def test_twitter_credentials():
    try:
        user_profile = api.verify_credentials()
        return f"Authenticated user: {user_profile.screen_name}"
    except Exception as e:
        return f"Error: {e}"


@app.route("/generate_post", methods=["POST"])
def generate_post():
    post_subject = request.form.get("post_subject")
    num_posts = int(request.form.get("number_of_posts", 1))

    prompt = f"Create a viral Twitter post about {post_subject} with popular and relevant hashtags."
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150,
        n=num_posts,
        stop=None,
        temperature=0.8,
    )

    generated_posts = [choice.text.strip() for choice in response.choices]

    scheduled_posts = read_scheduled_posts()
    for index, post in enumerate(generated_posts):
        scheduled_posts.append({
            "id": f"{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}-{index}",
            "content": post,
            "approved": False,
            "scheduled_time": None,
        })
    write_scheduled_posts(scheduled_posts)

    post_ids = [post["id"] for post in scheduled_posts[-num_posts:]]  # Get the last num_posts ids

    return jsonify({"generated_posts": generated_posts, "post_ids": post_ids})  # Include post_ids in the response


@app.route('/approve_post', methods=['POST'])
def approve_post():
    post_id = request.form.get('post_id')
    content = request.form.get('content')

    scheduled_posts = read_scheduled_posts()

    for post in scheduled_posts:
        if post['id'] == post_id:
            post['content'] = content
            post['approved'] = True
            break

    write_scheduled_posts(scheduled_posts)

    return jsonify(success=True)


@app.route("/schedule_posts", methods=["POST"])
def schedule_posts():
    start_date = request.form.get("start_date")
    start_time = request.form.get("start_time")
    interval_value = int(request.form.get("interval_value"))
    interval_unit = request.form.get("interval_unit")
    posts = request.form.getlist("posts[]")

    scheduled_posts = read_scheduled_posts()

    start_datetime = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
    interval_mapping = {"hours": timedelta(hours=1), "days": timedelta(days=1), "weeks": timedelta(weeks=1)}

    for post in posts:
        for scheduled_post in scheduled_posts:
            if scheduled_post["content"] == post and scheduled_post["approved"]:
                scheduled_post["scheduled_time"] = start_datetime.isoformat()  # Convert to string using isoformat before saving
                start_datetime += interval_mapping[interval_unit] * interval_value

    write_scheduled_posts(scheduled_posts)
    return "Posts scheduled successfully."


def background_scheduler():
    while True:
        time.sleep(60)  # Check every minute
        scheduled_posts = read_scheduled_posts()

        now = datetime.now().strftime("%Y-%m-%dT%H:%M:00")

        for post in scheduled_posts:
            if post["approved"] and post["scheduled_time"] == now:
                post_to_twitter(post["content"])
                post["approved"] = False  # Mark the post as unapproved after posting

        # Update the JSON file with the new status
        write_scheduled_posts(scheduled_posts)


def post_to_twitter(text):
    try:
        print(f"Posting to Twitter: {text}")
        api.update_status(text)
        print(f"Successfully posted to Twitter: {text}")
        return "success"
    except Exception as e:
        print(f"Error posting to Twitter: {e}")
        return str(e)


def check_and_publish_scheduled_posts():
    while True:
        scheduled_posts = read_scheduled_posts()

        for post in scheduled_posts:
            if post["approved"] and post["scheduled_time"] is not None:
                scheduled_time = datetime.fromisoformat(str(post["scheduled_time"]))  # Ensure scheduled_time is a string
                now = datetime.now()

                if now >= scheduled_time:
                    text = post["content"]
                    print(f"Posting to Twitter: {text}")
                    # Post to Twitter
                    post["published"] = True
                    write_scheduled_posts(scheduled_posts)

        time.sleep(60)


def remove_scheduled_post(post_id):
    scheduled_posts = read_scheduled_posts()
    scheduled_posts = [post for post in scheduled_posts if post["id"] != post_id]
    write_scheduled_posts(scheduled_posts)


if __name__ == "__main__":
    scheduler_thread = threading.Thread(target=background_scheduler, daemon=True)
    scheduler_thread.start()

    app.run(debug=True)

