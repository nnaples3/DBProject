from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="university"
    )

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/testdb")
def testdb():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM student LIMIT 5;")
    rows = cursor.fetchall()

    return str(rows)

if __name__ == "__main__":
    app.run(debug=True)