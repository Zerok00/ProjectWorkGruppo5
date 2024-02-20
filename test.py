from flask import Flask, jsonify, render_template, request, redirect, url_for
import folium

app = Flask(__name__)
#ciao ciao
@app.route("/")
def homepage():
    mappa = folium.Map([42, 12.5], zoom_start=6)
    mappa.get_root().width = "800px"
    print("ciao")
    folium.Marker(location=[41.89,12.492]).add_to(mappa)
    print("hola")
    return render_template("homepage.html", iframe=iframe)

if __name__ == '__main__':
    app.run(debug=True)