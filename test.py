from flask import Flask, jsonify, render_template, request, redirect, url_for
import folium

app = Flask(__name__)
@app.route("/")
def homepage():
    mappa = folium.Map([45.465, 9.185], zoom_start=8) #mappa centrata su Milano che inquadra la lombardia
    mappa.get_root().width = "40%"
    folium.Marker(location=[45.464,9.191]).add_to(mappa)    #segnalino sul duomo di milano
    iframe = mappa.get_root()._repr_html_()
    return render_template("homepage.html", iframe=iframe)

if __name__ == '__main__':
    app.run(debug=True)