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

# vars

STUDENT_ID = '24158' # Fixed student ID to mimic being logged in as student


# ------





@app.route("/")
def index():
    return render_template("index.html")

# Main student access area (dashboard)
# Displays links to all functions (register class, drop class, etc)
@app.route("/student-portal")
def student_portal():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM student LIMIT 5;")
    rows = cursor.fetchall()

    return str(rows)


# Check final grades
@app.route("/student-portal/grades")
def grades():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM takes WHERE ID = %s;", (STUDENT_ID,))
    rows = cursor.fetchall()

    return "GRADES: \n" + str(rows)

# Check courses based on semester (what is status?)
@app.route("/student-portal/courses", methods=["GET", "POST"])
def courses():
    selected_semester = request.form.get("semester")
    db = get_db()
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT s.ID, s.name, t.course_id, t.semester, t.year, t.sec_id, t.grade
        FROM student s
        JOIN takes t ON s.ID = t.ID
        WHERE s.ID = %s
    """

    params = [STUDENT_ID]

    if selected_semester and selected_semester != "all":
        query += " AND t.semester = %s"
        params.append(selected_semester)

    cursor.execute(query, params)
    semester_rows = cursor.fetchall()

    cursor.execute("""
        SELECT DISTINCT semester
        FROM takes
        WHERE ID = %s
    """, (STUDENT_ID,))
    semesters = cursor.fetchall()

    return render_template(
        "/student/courses.html",
        student_id = STUDENT_ID,
        semesters = semesters,
        semester_rows = semester_rows,
        selected_semester = selected_semester,
    )


# Check section information
@app.route("/student-portal/section")
def section():
    course_id = request.args.get("course_id")
    sec_id    = request.args.get("sec_id")
    semester  = request.args.get("semester")
    year      = request.args.get("year")
    db = get_db()
    cursor = db.cursor(dictionary=True)

    print(sec_id)

    query = """
        SELECT s.building, s.room_number, s.time_slot_id
        FROM section s
        WHERE s.course_id = %s
        AND s.sec_id    = %s
        AND s.semester  = %s
        AND s.year      = %s
    """

    cursor.execute(query, (course_id, sec_id, semester, year))
    section_info = cursor.fetchall()
    print(section_info)
    return render_template(
        "student/section.html",
        section_info = section_info,
        course_id=course_id,
        sec_id=sec_id,
        semester=semester,
        year=year
    )

# Check advisor information
@app.route("/student-portal/advisor")
def advisor():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT s.ID, s.name, t.course_id, t.semester, t.year, t.sec_id, t.grade
        FROM student s
        JOIN takes t ON s.ID = t.ID
        WHERE s.ID = %s
    """

    cursor.execute(query, )

# Test route to ensure local connection is working
@app.route("/testdb")
def testdb():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM student LIMIT 5;")
    rows = cursor.fetchall()

    return str(rows)

if __name__ == "__main__":
    app.run(debug=True)