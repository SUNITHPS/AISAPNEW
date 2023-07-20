from flask import Flask, render_template, request
import os
import openai
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

openai.api_key = "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"

def search_sap_community(question):
    # Perform a search on the SAP Community website
    search_url = f"https://community.sap.com/search?q={question}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract the URL of the first search result
    first_result = soup.find("a", class_="question-item-title")
    if first_result:
        return first_result["href"]
    else:
        return None

def ask_sap_bot(question):
    # Format user input as a prompt
    prompt = f"User: {question}\nSAP Bot:"

    # Truncate the prompt to fit within the model's maximum context length
    max_prompt_length = 4096
    prompt_truncated = prompt[:max_prompt_length]

    # Generate a response from the ChatGPT API using the truncated prompt
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt_truncated,
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.9
    )

    # Extract the generated answer from the API response
    answer = response.choices[0].text.strip().split("SAP Bot:")[-1].strip()

    # If the answer is not satisfactory, search on SAP Community website
    if "Sorry, I don't have the answer" in answer:
        search_result = search_sap_community(question)
        if search_result:
            answer += f"\nYou can find more information on the SAP Community website:\n{search_result}"
    
    return answer

# Example usage
question = "what is read table"
answer = ask_sap_bot(question)
print(answer)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chatbot", methods=["POST"])
def chatbot():
    question = request.form["question"]
    answer = ask_sap_bot(question)
    return answer

if __name__ == "__main__":
    # Run the Flask app on any available network interface
    app.run(host="0.0.0.0", port=os.environ.get("PORT"))