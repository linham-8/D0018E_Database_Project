from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    temp_skins = [{f"name": f"Skin {i}"} for i in range(67)]
    return render_template("index.html", temp_skins=temp_skins)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
