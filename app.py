from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import sqlite3
from functools import wraps
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def login_required(f):
    @wraps(f)
    def cek_login(*args, **kwargs):
        if "logged_in" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return cek_login

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "siber" and password == "siber123":
            session["logged_in"] = True
            return redirect(url_for("index"))
        else:
            return "Login gagal! Username atau password salah."

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

@app.route('/')
@login_required
def index():
    # RAW Query
    students = db.session.execute(text('SELECT * FROM student')).fetchall()
    return render_template('index.html', students=students)

# @app.route('/add', methods=['POST'])
# def add_student():
#     name = request.form['name']
#     age = request.form['age']
#     grade = request.form['grade']
    

#     connection = sqlite3.connect('instance/students.db')
#     cursor = connection.cursor()

#     # RAW Query
#     # db.session.execute(
#     #     text("INSERT INTO student (name, age, grade) VALUES (:name, :age, :grade)"),
#     #     {'name': name, 'age': age, 'grade': grade}
#     # )
#     # db.session.commit()
#     query = f"INSERT INTO student (name, age, grade) VALUES ('{name}', {age}, '{grade}')"
#     print(name,age,grade)
#     cursor.execute(query)
#     connection.commit()
#     connection.close()
#     return redirect(url_for('index'))

@app.route('/add', methods=['POST'])
@login_required
def add_student():
    name = request.form['name']
    age = request.form['age']
    grade = request.form['grade']
    
    # [PERBAIKAN]
    db.session.execute(
        text("INSERT INTO student (name, age, grade) VALUES (:name, :age, :grade)"),
        {'name': name, 'age': age, 'grade': grade}
    )
    db.session.commit()

    return redirect(url_for('index'))

# @app.route('/delete/<string:id>') 
# def delete_student(id):
#     # RAW Query
#     db.session.execute(text(f"DELETE FROM student WHERE id={id}"))
#     db.session.commit()
#     return redirect(url_for('index'))

# [PERBAIKAN] dari GET jadi POST untuk mencegah CSRF (CWE-352 sih) (nanti sama Sudes)
@app.route('/delete/<int:id>', methods=['POST']) 
@login_required
def delete_student(id):
    # [PERBAIKAN]
    db.session.execute(
        text("DELETE FROM student WHERE id=:student_id"),
        {'student_id': id}
    )
    db.session.commit()
    return redirect(url_for('index'))


# @app.route('/edit/<int:id>', methods=['GET', 'POST'])
# def edit_student(id):
#     if request.method == 'POST':
#         name = request.form['name']
#         age = request.form['age']
#         grade = request.form['grade']
        
#         # RAW Query
#         db.session.execute(text(f"UPDATE student SET name='{name}', age={age}, grade='{grade}' WHERE id={id}"))
#         db.session.commit()
#         return redirect(url_for('index'))
#     else:
#         # RAW Query
#         student = db.session.execute(text(f"SELECT * FROM student WHERE id={id}")).fetchone()
#         return render_template('edit.html', student=student)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        grade = request.form['grade']
        
        # [PERBAIKAN] Pake Parameterized Query 
        db.session.execute(
            text("UPDATE student SET name=:name, age=:age, grade=:grade WHERE id=:id"),
            {'name': name, 'age': age, 'grade': grade, 'id': id}
        )
        db.session.commit()
        return redirect(url_for('index'))
    else:
        # [PERBAIKAN] Pake Parameterized Query 
        student = db.session.execute(
            text("SELECT * FROM student WHERE id=:id"),
            {'id': id}
        ).fetchone()
        return render_template('edit.html', student=student)
    
    
# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)

