import os
import pandas as pd
import requests
from flask import Flask, request, send_file, render_template
import zipfile

app = Flask(__name__)

API_KEY = os.environ.get("STABILITY_API_KEY")  # Stored in Render

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    df = pd.read_excel(file)

    os.makedirs("images", exist_ok=True)

    url = "https://api.stability.ai/v2beta/stable-image/generate/core"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "image/png",
        "Content-Type": "application/json"
    }

    for _, row in df.iterrows():
        name = row["Name"]
        prompt = row["Prompt"]

        payload = {
            "model": "stable-diffusion-xl-beta-v2-2-2",
            "prompt": prompt,
            "output_format": "png"
        }

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            with open(f"images/{name}.png", "wb") as f:
                f.write(response.content)

    # Zip
    with zipfile.ZipFile("images.zip", "w") as zipf:
        for file in os.listdir("images"):
            zipf.write(f"images/{file}")

    return send_file("images.zip", as_attachment=True)
