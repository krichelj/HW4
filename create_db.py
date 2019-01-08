import sqlite3
import atexit
import sys

connection = sqlite3.connect('schedule.db')  # connect to the database


# register a function to be called immediately when the interpreter terminates
def close_db():
    connection.commit()
    connection.close()


atexit.register(close_db)


# the main() function
def main():
    create_tables()

    with open(sys.argv[1]) as words_file:
        word_generator = parse_words(words_file)
        for word in word_generator:
            print(word)

    # config_file = open(sys.argv[1], 'r')
    # for line in config_file:
    #     line_type = line[0]
    #     if line_type == 'C':
    #         print(line[3])


# our application API:

def create_tables():
    connection.executescript("""
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
            expected_output     TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS classrooms (
            id INTEGER PRIMARY KEY,
            location TEXT NOT NULL,
            current_course_id INTEGER NOT NULL,
            current_course_time_left INTEGER NOT NULL
        );
    """)


def insert_course(id, course_name, student, number_of_students, class_id, course_length):
    connection.execute("""
          INSERT INTO courses (id, course_name, student, number_of_students, class_id, course_length) VALUES (?, ?, ?, ?, ?, ?)
    """, [id, course_name, student, number_of_students, class_id, course_length])


def insert_student(grade, expected_output):
    connection.execute("""
          INSERT INTO students (grade, expected_output) VALUES (?, ?)
    """, [grade, expected_output])


def insert_classroom(id, location, current_course_id, current_course_time_left):
    connection.execute("""
          INSERT INTO classrooms (id, location, current_course_id, current_course_time_left) VALUES (?, ?, ?, ?)
    """, [id, location, current_course_id, current_course_time_left])


def parse_words(config_file):
    for line in config_file:
        for word in line.split():
            yield word
