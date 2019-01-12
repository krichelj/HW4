import os
import sqlite3
import atexit
import sys

data_base_existed = os.path.isfile("schedule.db")
database_connection = sqlite3.connect("schedule.db")  # connect to the database


# table construction function
def create_tables():
    database_connection.executescript("""
        CREATE TABLE IF NOT EXISTS courses (
            id      INTEGER     PRIMARY KEY,
            course_name    TEXT        NOT NULL,
            student TEXT NOT NULL,
            number_of_students INTEGER NOT NULL,
            class_id INTEGER REFERENCES classrooms(id),
            course_length INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS students (
            grade TEXT PRIMARY KEY,
            count INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS classrooms (
            id INTEGER PRIMARY KEY,
            location TEXT NOT NULL,
            current_course_id INTEGER NOT NULL,
            current_course_time_left INTEGER NOT NULL
        );
    """)


def insert_course(id, course_name, student, number_of_students, class_id, course_length):
    database_connection.execute("""
          INSERT OR REPLACE 
          INTO courses 
          (id, course_name, student, number_of_students, class_id, course_length) 
          VALUES (?, ?, ?, ?, ?, ?)
    """, [id, course_name, student, number_of_students, class_id, course_length])


def insert_student(grade, count):
    database_connection.execute("""
          INSERT OR REPLACE 
          INTO students 
          (grade, count) 
          VALUES (?, ?)
    """, [grade, count])


def insert_classroom(id, location, current_course_id, current_course_time_left):
    database_connection.execute("""
          INSERT OR REPLACE 
          INTO classrooms 
          (id, location, current_course_id, current_course_time_left) 
          VALUES (?, ?, ?, ?)
    """, [id, location, current_course_id, current_course_time_left])


def print_table(list_of_tuples):
    for item in list_of_tuples:
        print(item)


def print_tables(cursor):
    # print courses
    print("courses")
    cursor.execute("SELECT * FROM courses")
    print_table(cursor.fetchall())
    # print classrooms
    print("classrooms")
    cursor.execute("SELECT * FROM classrooms")
    print_table(cursor.fetchall())
    # print students
    print("students")
    cursor.execute("SELECT * FROM students")
    print_table(cursor.fetchall())


# register a function to be called immediately when the interpreter terminates
def close_database():
    database_connection.commit()
    database_connection.close()


atexit.register(close_database)


# the main function
def main():
    if not data_base_existed:  # First time creating the database.
        with database_connection:
            cursor = database_connection.cursor()
            create_tables()
            with open(sys.argv[1], 'r') as config_file:  # parse the config file
                for line in config_file:
                    line = line.replace("\n", "")
                    line_info = line.split(",")
                    line_type = line_info[0]
                    if line_type == 'C':  # means we're typing in a course
                        insert_course(int(line_info[1].strip(" ")), line_info[2].strip(" "),
                                      line_info[3].strip(" "), int(line_info[4].strip(" ")),
                                      int(line_info[5].strip(" ")),
                                      int(line_info[6].strip(" ")))
                    elif line_type == 'S':  # means we're typing in a student
                        insert_student(line_info[1].strip(" "), int(line_info[2].strip(" ")))
                    elif line_type == 'R':  # means we're typing in a classroom
                        insert_classroom(int(line_info[1].strip(" ")), line_info[2].strip(" "), 0, 0)
            print_tables(cursor)
            cursor.close()


if __name__ == '__main__':
    main()
