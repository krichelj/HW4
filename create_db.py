import os
import sqlite3
import sys


# table construction function
def create_tables(database_connection):
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


def insert_course(database_connection, id, course_name, student, number_of_students, class_id, course_length):
    database_connection.execute("""
          INSERT OR REPLACE 
          INTO courses 
          (id, course_name, student, number_of_students, class_id, course_length) 
          VALUES (?, ?, ?, ?, ?, ?)
    """, [id, course_name, student, number_of_students, class_id, course_length])


def insert_student(database_connection, grade, count):
    database_connection.execute("""
          INSERT OR REPLACE 
          INTO students 
          (grade, count) 
          VALUES (?, ?)
    """, [grade, count])


def insert_classroom(database_connection, id, location, current_course_id, current_course_time_left):
    database_connection.execute("""
          INSERT OR REPLACE 
          INTO classrooms 
          (id, location, current_course_id, current_course_time_left) 
          VALUES (?, ?, ?, ?)
    """, [id, location, current_course_id, current_course_time_left])


def print_table(list_of_tuples):  # an aid function that was provided to to print a tuple
    for item in list_of_tuples:
        print(item)


def print_tables(cursor):  # an aid function to test the tables according to the specifications
    # print courses
    print("courses")
    cursor.execute("SELECT * FROM courses")
    # string_tuple_list = [tuple(map(str, eachTuple)) for eachTuple in cursor.fetchall()]
    print_table(cursor.fetchall())
    # print classrooms
    print("classrooms")
    cursor.execute("SELECT * FROM classrooms")
    print_table(cursor.fetchall())
    # print students
    print("students")
    cursor.execute("SELECT * FROM students")
    print_table(cursor.fetchall())


# the main function
def main():
    data_base_existed = os.path.isfile("schedule.db")
    database_connection = sqlite3.connect("schedule.db")  # connect to the database
    if not data_base_existed:  # checks if it's the first time creating the database
        with database_connection:
            cursor = database_connection.cursor()
            create_tables(database_connection)
            with open(sys.argv[1], 'r') as config_file:  # parse the config file
                for line in config_file:
                    line = line.replace('\n', '')
                    line_info = line.split(',')
                    for i in range(0, len(line_info)):  # strip all unnecessary characters
                        line_info[i] = line_info[i].strip(' ')
                        line_info[i] = line_info[i].strip('\r')
                        line_info[i] = line_info[i].strip('\t')
                    line_type = line_info[0]
                    if line_type == 'C':  # means we're typing in a course
                        insert_course(database_connection, int(line_info[1]), line_info[2],
                                      line_info[3], int(line_info[4]), int(line_info[5]), int(line_info[6]))
                    elif line_type == 'S':  # means we're typing in a student
                        insert_student(database_connection, line_info[1], int(line_info[2]))
                    elif line_type == 'R':  # means we're typing in a classroom
                        insert_classroom(database_connection, int(line_info[1]), line_info[2], 0, 0)
            print_tables(cursor)  # print the tables
            cursor.close()  # close the cursor
            database_connection.commit()  # save the changes made to the database


if __name__ == '__main__':
    main()
