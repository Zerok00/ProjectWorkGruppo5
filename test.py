from flask import Flask, jsonify, render_template, request, redirect, url_for
import folium

app = Flask(__name__)
@app.route("/")
def homepage():
    mappa = folium.Map([42, 12.5], zoom_start=6)
    mappa.get_root().width = "800px"
    mappa.get_root().height = "600px"
    folium.Marker(location=[41.89,12.492]).add_to(mappa)
    iframe = mappa.get_root()._repr_html_()
    return render_template("homepage.html", iframe=iframe)

if __name__ == '__main__':zz
    app.run(debug=True)