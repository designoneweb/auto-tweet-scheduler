# ChatGPT Tweet Scheduler

ChatGPT Tweet Scheduler is a browser-based application that automatically schedules and posts content to Twitter using ChatGPT by OpenAI to generate posts based on user input. 

## Features

- Generate posts using ChatGPT by OpenAI
- Approve or edit generated posts before scheduling
- Schedule posts with customizable intervals
- Automatically post scheduled content to Twitter

## Requirements

- Python 3.6 or higher
- Flask
- Tweepy
- openai
- python-dotenv
- apscheduler
- Pillow

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/auto-social-media-scheduler.git
cd auto-social-media-scheduler
```
2. Create a virtual environment and activate it:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

4. Create a .env file in the root directory of the project and copy content from example_env.txt into it. Replace YOUR_OPENAI_API_KEY, YOUR_TWITTER_API_KEY, OUR_TWITTER_API_SECRET_KEY, YOUR_TWITTER_ACCESS_TOKEN, YOUR_TWITTER_ACCESS_TOKEN_SECRET in the .env file with your actual API keys and access tokens.

5. Run the application:

```bash
python3 app.py
```

The application will be available at http://127.0.0.1:5000/ in your web browser.

## Usage

1. Open the application in your web browser.
2. Enter a post subject and the number of posts to generate, then click "Generate Posts."
3. Review, edit if desired, and approve the generated posts.
4. Enter the start date, start time, and interval for scheduling the posts.
5. Click "Schedule Posts" to schedule the approved posts.

The scheduled posts will be automatically published to your connected Twitter and Facebook accounts at the specified times.