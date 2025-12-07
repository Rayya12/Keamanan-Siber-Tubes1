from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_wtf.csrf import CSRFProtect, generate_csrf
import sqlite3
import secrets

app = Flask(__name__)
# Generate secret key untuk session dan CSRF
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inisialisasi CSRF Protection
csrf = CSRFProtect(app)

db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'

# Middleware untuk inject CSRF token ke setiap response
@app.after_request
def inject_csrf_token(response):
    response.set_cookie('csrf_token', generate_csrf())
    return response

@app.route('/')
def index():
    # RAW Query
    students = db.session.execute(text('SELECT * FROM student')).fetchall()
    # Generate CSRF token untuk form
    csrf_token = generate_csrf()
    return render_template('index.html', students=students, csrf_token=csrf_token)

@app.route('/add', methods=['POST'])
def add_student():
    # Verifikasi CSRF token
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf(csrf_token):
        flash('CSRF token invalid atau expired', 'danger')
        return redirect(url_for('index'))
    
    name = request.form['name']
    age = request.form['age']
    grade = request.form['grade']
    
    # Validasi input
    if not name or not age or not grade:
        flash('Semua field harus diisi', 'danger')
        return redirect(url_for('index'))
    
    try:
        connection = sqlite3.connect('instance/students.db')
        cursor = connection.cursor()
        
        # Gunakan parameterized query untuk mencegah SQL injection
        query = "INSERT INTO student (name, age, grade) VALUES (?, ?, ?)"
        cursor.execute(query, (name, age, grade))
        connection.commit()
        connection.close()
        
        flash('Student berhasil ditambahkan', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('index'))

@app.route('/delete/<string:id>', methods=['POST'])  # Ubah ke POST untuk keamanan
def delete_student(id):
    # Verifikasi CSRF token dari form
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf(csrf_token):
        flash('CSRF token invalid atau expired', 'danger')
        return redirect(url_for('index'))
    
    try:
        # Gunakan parameterized query
        db.session.execute(text("DELETE FROM student WHERE id = :id"), {'id': id})
        db.session.commit()
        flash('Student berhasil dihapus', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    if request.method == 'POST':
        # Verifikasi CSRF token
        csrf_token = request.form.get('csrf_token')
        if not validate_csrf(csrf_token):
            flash('CSRF token invalid atau expired', 'danger')
            return redirect(url_for('index'))
        
        name = request.form['name']
        age = request.form['age']
        grade = request.form['grade']
        
        # Validasi input
        if not name or not age or not grade:
            flash('Semua field harus diisi', 'danger')
            return redirect(url_for('edit_student', id=id))
        
        try:
            # Gunakan parameterized query
            db.session.execute(
                text("UPDATE student SET name=:name, age=:age, grade=:grade WHERE id=:id"),
                {'name': name, 'age': age, 'grade': grade, 'id': id}
            )
            db.session.commit()
            flash('Student berhasil diupdate', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('edit_student', id=id))
    else:
        try:
            # Gunakan parameterized query
            student = db.session.execute(
                text("SELECT * FROM student WHERE id = :id"),
                {'id': id}
            ).fetchone()
            
            if not student:
                flash('Student tidak ditemukan', 'danger')
                return redirect(url_for('index'))
            
            csrf_token = generate_csrf()
            return render_template('edit.html', student=student, csrf_token=csrf_token)
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('index'))

# Fungsi untuk validasi CSRF token
def validate_csrf(token):
    from flask_wtf.csrf import validate_csrf as wtf_validate_csrf
    from wtforms import ValidationError
    
    try:
        wtf_validate_csrf(token)
        return True
    except ValidationError:
        return False

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)