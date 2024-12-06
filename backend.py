import sqlite3
import os


def connect():
    '''Create a database if not existed and make a connection to it.
    Also, sets up the trigger and view if they do not already exist.
    '''
    conn = sqlite3.connect("Students.db")
    cur = conn.cursor()
    
    # Create the main table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS data1 (
            id INTEGER PRIMARY KEY, 
            fn TEXT, 
            ln TEXT, 
            term INTEGER, 
            gpa REAL,
            grade TEXT,
            course TEXT,
            teacher TEXT
        )
    """)
    
    # Create a log table for the trigger
    cur.execute("""
        CREATE TABLE IF NOT EXISTS data1_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            old_data TEXT,
            new_data TEXT,
            change_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create the trigger for logging updates
    cur.execute("""
        CREATE TRIGGER IF NOT EXISTS log_data1_update
        AFTER UPDATE ON data1
        FOR EACH ROW
        BEGIN
            INSERT INTO data1_log (old_data, new_data)
            VALUES (
                json_object('id', OLD.id, 'fn', OLD.fn, 'ln', OLD.ln, 'term', OLD.term, 'gpa', OLD.gpa, 'grade', OLD.grade, 'course', OLD.course, 'teacher', OLD.teacher),
                json_object('id', NEW.id, 'fn', NEW.fn, 'ln', NEW.ln, 'term', NEW.term, 'gpa', NEW.gpa, 'grade', NEW.grade, 'course', NEW.course, 'teacher', NEW.teacher)
            );
        END;
    """)

     # Create the trigger for updating the grade based on GPA
    cur.execute("""
        CREATE TRIGGER IF NOT EXISTS update_grade_after_update
        AFTER UPDATE ON data1
        FOR EACH ROW
        WHEN NEW.grade != (CASE
            WHEN NEW.gpa >= 3.7 THEN 'A'
            WHEN NEW.gpa >= 3.0 THEN 'B'
            WHEN NEW.gpa >= 2.0 THEN 'C'
            ELSE 'F'
        END)
        BEGIN
            UPDATE data1
            SET grade = CASE
                WHEN NEW.gpa >= 3.7 THEN 'A'
                WHEN NEW.gpa >= 3.0 THEN 'B'
                WHEN NEW.gpa >= 2.0 THEN 'C'
                ELSE 'F'
            END
            WHERE id = NEW.id;
        END;

    """)

    # Create the trigger for automatically updating the grade based on GPA
    cur.execute("""
        CREATE TRIGGER IF NOT EXISTS update_grade
        AFTER INSERT ON data1
        FOR EACH ROW
        BEGIN
            UPDATE data1 
            SET grade = (CASE
                WHEN NEW.gpa >= 3.7 THEN 'A'
                WHEN NEW.gpa >= 3.0 THEN 'B'
                WHEN NEW.gpa >= 2.0 THEN 'C'
                ELSE 'F'
            END)
            WHERE id = NEW.id;
        END;
    """)
    
    # Create a view to list students with GPA above 3.0
    cur.execute("""
        CREATE VIEW IF NOT EXISTS high_gpa_students AS
        SELECT id, fn, ln, term, gpa, grade, course, teacher
        FROM data1 
        WHERE gpa > 3.0
    """)
    
    conn.commit()
    conn.close()


def insert(fn, ln, term, gpa, course, teacher):
    '''Insertion function to insert a new student into the database.'''
    conn = sqlite3.connect("Students.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO data1 (fn, ln, term, gpa, course, teacher) VALUES (?, ?, ?, ?, ?, ?)", (fn, ln, term, gpa, course, teacher))
    conn.commit()
    conn.close()


def view():
    '''View function to show the content of the main table.'''
    conn = sqlite3.connect("Students.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM data1")
    rows = cur.fetchall()
    conn.close()
    return rows


def view_high_gpa_students():
    '''View function to show the content of the high GPA students view.'''
    conn = sqlite3.connect("Students.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM high_gpa_students")
    rows = cur.fetchall()
    conn.close()
    return rows


def search(fn="", ln="", term="", gpa="", course="", teacher=""):
    '''Search function to find specific students in the database.'''
    conn = sqlite3.connect("Students.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM data1 WHERE fn=? OR ln=? OR term=? OR gpa=? OR course=? OR teacher=?", (fn, ln, term, gpa, course, teacher))
    rows = cur.fetchall()
    conn.close()
    return rows


def delete(id):
    '''Delete function to remove a student by ID.'''
    conn = sqlite3.connect("Students.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM data1 WHERE id=?", (id,))
    conn.commit()
    conn.close()


def update(id, fn, ln, term, gpa, course, teacher):
    '''Update function to modify a student's data by ID.'''
    conn = sqlite3.connect("Students.db")
    cur = conn.cursor()
    cur.execute("UPDATE data1 SET fn=?, ln=?, term=?, gpa=?, course=?, teacher=? WHERE id=?", (fn, ln, term, gpa, course, teacher, id,))
    conn.commit()
    conn.close()


def delete_data():
    '''Delete the database file and reset it.'''
    if os.path.exists("Students.db"):
        os.remove("Students.db")
    connect()


connect()