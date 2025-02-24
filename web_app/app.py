from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    config = {
        "file_names": ["fritschi.jpg", "hexe.jpg", "spoerri.jpg", "basler.jpg", "fisch.jpg", 
                      "affe.jpg", "sau.jpg", "krieger.jpg", "clown.jpg", "hase.jpg", 
                      "einhorn.png", "grinch.jpg", "alien.jpg", "teufel.jpg", "guy.jpg", 
                      "ueli.jpg", "steampunk.jpg", "pippi.jpg", "wonderwoman.jpg", "federer.jpg"],
        "labels": ["zünftig", "rüüdig", "kult-urig", "appropriated", "laborig", 
                 "huereaffig", "sauglatt", "kriegerisch", "creepy", "cute", 
                 "magisch", "cringe", "extraterrestrisch", "teuflisch", "random", 
                 "schwurblig", "boomerig", "feministisch", "superstark", "bönzlig"],
        "priority_list": [1, 2, 3, 4, 13, 6, 7, 8, 9, 10, 11, 17, 5, 14, 15, 16, 12, 18, 19, 20],
        "scaling_factor": 0.75
    }
    return render_template('index.html', **config)

if __name__ == '__main__':
    app.run(debug=True)