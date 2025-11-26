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
CURRENT_YEAR = 2022


# ------

# STUDENT todo
# register & drop
# modify personal info (not id)



@app.route("/")
def index():
    return render_template("index.html")

# Main student access area (dashboard)
# Displays links to all functions (register class, drop class, etc)
@app.route("/student-portal")
def student_portal():
    return render_template("student/student_portal.html")


# Check final grades
@app.route("/student-portal/grades")
def grades():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM takes WHERE ID = %s;", (STUDENT_ID,))
    rows = cursor.fetchall()

    return "GRADES: \n" + str(rows)

# Check courses based on semester 
# TODO: if year and semester match the current then its status: active
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
        SELECT i.ID, i.name, i.dept_name
        FROM advisor a
        JOIN instructor i ON a.i_ID = i.ID
        WHERE a.s_ID = %s
    """

    cursor.execute(query, (STUDENT_ID,))
    advisor_info = cursor.fetchone()
    return str(advisor_info)

# Registration portal
@app.route("/student-portal/register")
def register():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    # List classes
    # Must join with instructor,
    # Building

    query = """
        SELECT * FROM section WHERE semester = 'Spring' and year = 2022
    """

    cursor.execute(query)
    courses = cursor.fetchall()

    # Add button
    return render_template("student/register.html", 
                           courses=courses)

# Route to actually perform the class add from given url parameters
@app.route("/student-portal/register/add")
def add():
    course_id = request.args.get("course_id")
    sec_id    = request.args.get("sec_id")
    semester  = request.args.get("semester")
    year      = request.args.get("year")
    db = get_db()
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT *
        FROM takes
        WHERE ID = %s
        AND course_id = %s
        AND sec_id = %s
        AND semester = %s
        AND year = %s
    """

    cursor.execute(query, (STUDENT_ID, course_id, sec_id, semester, year))
    exists = cursor.fetchone()

    if exists:
        return "Already registered for this course"
    
    insert_query = """
        INSERT INTO takes (ID, course_id, sec_id, semester, year)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (STUDENT_ID, course_id, sec_id, semester, year))
    db.commit()

    return "Registration successful!"

# Drop portal
@app.route("/student-portal/drop")
def drop():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT s.ID, s.name, t.course_id, t.semester, t.year, t.sec_id, t.grade
        FROM student s
        JOIN takes t ON s.ID = t.ID
        WHERE s.ID = %s
    """

    cursor.execute(query, (STUDENT_ID,))
    active_courses = cursor.fetchall()

    print(active_courses)

    return render_template("student/drop.html", courses=active_courses)

# Route to actually perform the drop from given url parameters
@app.route("/student-portal/drop/remove")
def remove():
    course_id = request.args.get("course_id")
    sec_id    = request.args.get("sec_id")
    semester  = request.args.get("semester")
    year      = request.args.get("year")
    db = get_db()
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT *
        FROM takes
        WHERE ID = %s
        AND course_id = %s
        AND sec_id = %s
        AND semester = %s
        AND year = %s
    """

    cursor.execute(query, (STUDENT_ID, course_id, sec_id, semester, year))
    exists = cursor.fetchone()

    if not exists:
        return "Not registered for this course!"
    
    delete_query = """
        DELETE FROM takes
        WHERE ID = %s
        AND course_id = %s
        AND sec_id = %s
        AND semester = %s
        AND year = %s
    """
    cursor.execute(delete_query, (STUDENT_ID, course_id, sec_id, semester, year))
    db.commit()

    return "Drop course success!"


# Allow update: Major (pick from list of choices)
# Allow name change
@app.route("/student-portal/update-info", methods=["GET", "POST"])
def update_info():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT ID, name, dept_name 
        FROM student
        WHERE ID = %s
    """, (STUDENT_ID,))
    student = cursor.fetchone()

    cursor.execute("SELECT dept_name FROM department ORDER BY dept_name;")
    departments = cursor.fetchall()

    if request.method == "POST":
        new_name = request.form.get("name")
        new_major = request.form.get("dept_name")

        update_query = """
            UPDATE student
            SET name = %s, dept_name = %s
            WHERE ID = %s
        """
        cursor.execute(update_query, (new_name, new_major, STUDENT_ID))
        db.commit()

        return render_template(
            "student/update_success.html",
            name=new_name,
            major=new_major
        )

    return render_template(
        "student/update_info.html",
        student=student,
        departments=departments
    )


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