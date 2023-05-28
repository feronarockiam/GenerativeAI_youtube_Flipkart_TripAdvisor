from flask import Flask, redirect, render_template, request
from bs4 import BeautifulSoup as soup
import urllib.request
import requests
import openai
import sys
app = Flask(__name__)


def get_main_HTML(base_URL=None):
    search_url = f"{base_URL}"
    with urllib.request.urlopen(search_url) as url:
        page = url.read()
    return soup(page, "html.parser")


def get_prod_HTML(self, productLink=None):
    '''
    returns each product HTML page after parsing it with soup
    '''
    prod_page = requests.get(productLink)
    return soup(prod_page.text, "html.parser")


@app.route('/')
def home():
    return render_template('index1.html')


@app.route('/process', methods=['POST'])
def process():
    productLink = request.form['productLink']
    get_prompt = request.form['getPrompt']
    openai.api_key = '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'

    prod_HTML = get_main_HTML(productLink)
    comment_boxes = prod_HTML.find_all('div', {'class': 't-ZTKy'})
    review_list = []
    for i in comment_boxes:
        review_string = i.getText()
        modified_string = review_string.replace("READ MORE", "")
        review_list.append(modified_string)

    def get_completion(prompt):
        messages = [{"role":"system","content":"Your name is Scrappy.Ai. Your aim at providing answer to the user based on e-commerce products"},{"role": "user", "content": prompt}]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0,  # this is the degree of randomness of the model's output
        )
        return response.choices[0].message["content"]

    flipkart_review = review_list

    prompt = f"""{get_prompt}
    Review text: '''{flipkart_review}'''
    """
    response = get_completion(prompt)
    return render_template('result.html', response=response)




if __name__ == '__main__':
    app.run(port=4000)
