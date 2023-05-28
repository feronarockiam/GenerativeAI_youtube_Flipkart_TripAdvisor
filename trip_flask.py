import sys
from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import openai

app = Flask(__name__)

chrome_options = Options()
chrome_options.add_argument("--headless")

# default number of scraped pages
num_page = 2

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        prompts = request.form.getlist('prompt')

        review_list = scrape_reviews(url)
        responses = generate_responses(prompts, review_list)

        return render_template('trip_results.html', responses=responses)

    return render_template('index2.html')

def scrape_reviews(url):
    webdriver_path = "/path/to/chromedriver"
    # import the webdriver
    driver = webdriver.Chrome(executable_path=webdriver_path, options=chrome_options)
    driver.get(url)
    review_list = []
    # change the value inside the range to save more or less reviews
    for i in range(0, num_page):

        # expand the review 
        time.sleep(2)

        container = driver.find_elements(By.XPATH,"//div[@data-reviewid]")
    

        for j in range(len(container)):

            review = container[j].find_element(By.XPATH,".//span[@class='QewHA H4 _a']").text.replace("\n", "  ")
            review_list.append(review)
    return review_list

def generate_responses(prompts, review_list):
    responses = []
    for prompt in prompts:
        full_prompt = f"{prompt}\nReview text: {review_list}"
        response = get_completion(full_prompt)
        responses.append(response)
    return responses

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,  # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

if __name__ == '__main__':
    openai.api_key = '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'
    app.run(debug=True)

