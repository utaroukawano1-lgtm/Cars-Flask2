from flask import Flask, g, render_template, request, redirect, url_for
import sqlite3

DATABASE = "Cars.db"
app = Flask(__name__)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.route("/")
def home():
    sql = """
            SELECT Cars.CarsID,Makers.Name,Cars.Model,Cars.ImageURL
            FROM Cars
            JOIN Makers ON Makers.MakerID=Cars.MakerID;
            """
    sql_trending = """
SELECT Cars.CarsID, Makers.Name, Cars.Model, Cars.ImageURL
FROM Cars
JOIN Makers ON Makers.MakerID = Cars.MakerID
WHERE Makers.Name = 'Bugatti'
ORDER BY Cars.CarsID DESC
LIMIT 1;
"""
    results = query_db(sql)
    trending = query_db(sql_trending)

    return render_template("home.html", results=results, trending=trending,)
    

@app.route("/Cars/<int:id>")
def Cars(id):
    sql = """SELECT * FROM Cars 
    JOIN Makers ON Makers.MakerID=Cars.MakerID
    WHERE Cars.CarsID = ?;"""
    result = query_db(sql, [id,],True)
    return render_template("Cars.html" , Cars = result)

@app.route("/article/<int:id>")
def article(id):
    sql = """
        SELECT Cars.CarsID, Makers.Name, Cars.Model, Cars.ImageURL
        FROM Cars
        JOIN Makers ON Makers.MakerID = Cars.MakerID
        WHERE Cars.CarsID = ?;
    """
    car = query_db(sql, [id], one=True)

    return render_template("article.html", car=car)

@app.route('/makers/<int:id>')
def maker(id):
    sql = """
                Select Cars.CarsID,Makers.Name,Cars.Model,Cars.ImageURL
                FROM Cars
                JOIN Makers ON Makers.MakerID=Cars.MakerID
                WHERE Makers.MakerID = ?;"""

    results = query_db(sql, (id,))

    return render_template("makers.html", results=results)


@app.route("/search")
def search():
    query = request.args.get("query")
    print("query:",query)
    cars = {
        "bugatti": 0,
        "lamborghini": 1,
        "porsche": 2,
        "ferrari": 3,
        "koenigsegg": 4,
        "pagani": 5
    }
    supercars = {
        "bugatti chiron": 0,
    }
    if query:
        query = query.lower()
        if query in cars:
            return redirect(url_for("maker", id=cars[query]))
        elif query in supercars:
            return redirect(url_for("Cars", id=supercars[query]))

    return "Car not found"

@app.route("/Contact")
def Contact():
    return render_template("Contact.html")

if __name__ == "__main__":
    app.run(debug=True)
