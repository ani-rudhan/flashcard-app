
from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    df = pd.read_csv("n5-vocab - Topic13.csv")
    if 'Unnamed: 0' in df.columns:
        df = df.drop(columns=['Unnamed: 0'])
    cards = df.to_dict(orient='records')
    return render_template('index.html', cards=cards)

if __name__ == '__main__':
    app.run(debug=True)
