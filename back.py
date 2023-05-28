from flask import Flask, render_template, request, jsonify
from googleapiclient.discovery import build
import re
import openai

app = Flask(__name__)

openai.api_key = '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'
api_key = "AIzaSyBUGlfG33K_KjDg2SkpzkKGRilinBMBxzE"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        youtube_url = request.form['youtube_url']
        video_id = re.findall(r"v=([^&]+)", youtube_url)[0]
        youtube = build('youtube', 'v3', developerKey=api_key)
        comments = []
        next_page_token = None
        comment_count = 0
        while comment_count < 50:
            comments_response = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=100,
                pageToken=next_page_token
            ).execute()
            for comment in comments_response["items"]:
                comment_text = comment["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                comments.append(comment_text)
                comment_count += 1
                if comment_count >= 50:
                    break
            next_page_token = comments_response.get("nextPageToken")
            if not next_page_token:
                break
        youtube_review = '\n'.join(comments)
        return render_template('index.html', youtube_review=youtube_review)
    return render_template('index.html')



@app.route('/generate', methods=['POST'])
def generate():
    get_prompt = request.json['prompt']
    youtube_review = request.json['youtube_review']

    prompt = f"""{get_prompt}
        Review text: '''{youtube_review}'''
        """
    messages = [{"role":"system", "content":"Your name is Scrappy.AI. You are mainly for analyzing the comments of the youtube video and answer the prompts of the users who ask about the youtube video"},{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.5
    )
    generated_response = response.choices[0].message["content"]
    return jsonify(generated_response)


if __name__ == '__main__':
    app.run()