import sqlite3
from typing import List, Optional

class SchoolSystem:
    def __init__(self, db_name: str = "school.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        """Initializes database tables for subjects, students, and enrollments."""
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS subjects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    teacher TEXT NOT NULL
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS enrollments (
                    student_id INTEGER,
                    subject_id INTEGER,
                    grade REAL DEFAULT NULL,
                    PRIMARY KEY (student_id, subject_id),
                    FOREIGN KEY (student_id) REFERENCES students (id),
                    FOREIGN KEY (subject_id) REFERENCES subjects (id)
                )
            """)

    # --- SUBJECT MANAGEMENT ---
    def add_subject(self, code: str, name: str, teacher: str):
        try:
            with self.conn:
                self.conn.execute(
                    "INSERT INTO subjects (code, name, teacher) VALUES (?, ?, ?)",
                    (code.upper(), name, teacher)
                )
            print(f"✅ Subject '{name}' ({code.upper()}) added successfully!")
        except sqlite3.IntegrityError:
            print(f"❌ Error: Subject code '{code.upper()}' already exists.")

    def list_subjects(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, code, name, teacher FROM subjects")
        subjects = cursor.fetchall()
        
        print("\n--- 📚 School Subjects ---")
        if not subjects:
            print("No subjects found.")
            return
        for sub in subjects:
            print(f"[{sub[0]}] {sub[1]} - {sub[2]} (Teacher: {sub[3]})")

    # --- STUDENT MANAGEMENT ---
    def add_student(self, name: str, email: str):
        try:
            with self.conn:
                self.conn.execute(
                    "INSERT INTO students (name, email) VALUES (?, ?)",
                    (name, email)
                )
            print(f"✅ Student '{name}' registered successfully!")
        except sqlite3.IntegrityError:
            print(f"❌ Error: Student with email '{email}' already exists.")

    # --- ENROLLMENT & GRADES ---
    def enroll_student(self, student_id: int, subject_id: int):
        try:
            with self.conn:
                self.conn.execute(
                    "INSERT INTO enrollments (student_id, subject_id) VALUES (?, ?)",
                    (student_id, subject_id)
                )
            print(f"✅ Student {student_id} enrolled in Subject {subject_id}!")
        except sqlite3.IntegrityError:
            print("❌ Enrollment failed: Either student/subject ID doesn't exist or student is already enrolled.")

    def assign_grade(self, student_id: int, subject_id: int, grade: float):
        with self.conn:
            cursor = self.conn.execute(
                "UPDATE enrollments SET grade = ? WHERE student_id = ? AND subject_id = ?",
                (grade, student_id, subject_id)
            )
            if cursor.rowcount > 0:
                print(f"✅ Grade {grade} assigned successfully!")
            else:
                print("❌ Student is not enrolled in this subject.")

    def show_student_report(self, student_id: int):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM students WHERE id = ?", (student_id,))
        student = cursor.fetchone()
        if not student:
            print("❌ Student not found.")
            return

        cursor.execute("""
            SELECT s.code, s.name, e.grade 
            FROM enrollments e
            JOIN subjects s ON e.subject_id = s.id
            WHERE e.student_id = ?
        """, (student_id,))
        records = cursor.fetchall()

        print(f"\n--- 🎓 Report Card for {student[0]} ---")
        if not records:
            print("No enrolled subjects found.")
            return

        total_grade = 0
        graded_count = 0
        for code, sub_name, grade in records:
            grade_str = f"{grade:.2f}" if grade is not None else "N/A"
            print(f"• {code}: {sub_name} | Grade: {grade_str}")
            if grade is not None:
                total_grade += grade
                graded_count += 1

        if graded_count > 0:
            print(f"📊 Average Grade: {total_grade / graded_count:.2f}")


# --- INTERACTIVE CLI ---
def main():
    system = SchoolSystem()

    while True:
        print("\n=== SCHOOL SUBJECT SYSTEM ===")
        print("1. Add Subject")
        print("2. List All Subjects")
        print("3. Add Student")
        print("4. Enroll Student in Subject")
        print("5. Assign Grade")
        print("6. View Student Report")
        print("7. Exit")
        
        choice = input("\nSelect an option (1-7): ").strip()

        if choice == "1":
            code = input("Subject Code (e.g., MATH101): ")
            name = input("Subject Name: ")
            teacher = input("Teacher Name: ")
            system.add_subject(code, name, teacher)

        elif choice == "2":
            system.list_subjects()

        elif choice == "3":
            name = input("Student Name: ")
            email = input("Student Email: ")
            system.add_student(name, email)

        elif choice == "4":
            s_id = int(input("Student ID: "))
            sub_id = int(input("Subject ID: "))
            system.enroll_student(s_id, sub_id)

        elif choice == "5":
            s_id = int(input("Student ID: "))
            sub_id = int(input("Subject ID: "))
            grade = float(input("Grade (0-100): "))
            system.assign_grade(s_id, sub_id, grade)

        elif choice == "6":
            s_id = int(input("Student ID: "))
            system.show_student_report(s_id)

        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid option, please try again.")

if __name__ == "__main__":
    main()
