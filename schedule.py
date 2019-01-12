import atexit
import os
import sqlite3

data_base_existed = os.path.isfile("schedule.db")
database_connection = sqlite3.connect("schedule.db")  # connect to the database


def select_free_classroom(cursor, i):
    cursor.execute("""SELECT
                           classroom.location,
                           course.course_name,
                           course.id,
                           course.course_length,
                           classroom.id,
                           course.number_of_students,
                           course.student
                      FROM
                           classrooms as classroom 
                      JOIN
                          courses as course 
                      ON
                          classroom.id = course.class_id 
                      AND
                          classroom.current_course_time_left = 0
                      AND
                          classroom.current_course_id = 0""")  # select all classrooms that are free
    for result in cursor.fetchall():
        cursor.execute("""SELECT classroom.current_course_id FROM classrooms as classroom
            WHERE classroom.id = ?""", [result[4]])  # select the current classroom again to see if its occupied
        current_classroom_course_id = int(cursor.fetchone()[0])
        cursor.execute("""SELECT student.count FROM students as student
                    WHERE student.grade = ?""", [result[6]])  # select the available number of students
        current_available_number_of_students = int(cursor.fetchone()[0])
        if current_classroom_course_id == 0 and current_available_number_of_students - result[5] >= 0:
            # if the current classroom is actually free and there are enough students
            print("(" + str(i) + ") " + result[0] + ": " + result[1] + " is schedule to start")
            cursor.execute("""UPDATE
                                   classrooms
                              SET
                                   current_course_id = ?,
                                   current_course_time_left = ?
                              WHERE
                                   classrooms.id = ? """, [result[2], result[3], result[4]])
            cursor.execute("""UPDATE students SET count = count - ? WHERE 
                students.grade = ? """, [result[5], result[6]])  # take the students from the students table


def select_occupied_classrooms(cursor, i):
    cursor.execute("""SELECT 
                           classroom.location, 
                           course.course_name,
                           classroom.id
                      FROM 
                           classrooms as classroom 
                      JOIN 
                           courses as course 
                      ON
                           classroom.current_course_id = course.id
                      AND 
                           classroom.current_course_time_left > 0
                      AND
                           classroom.current_course_time_left != course.course_length""")
    for result in cursor.fetchall():
        print("(" + str(i) + ") " + result[0] + ": occupied by " + result[1])


def select_done(cursor, i):
    cursor.execute("""SELECT 
                          classroom.location, 
                          course.course_name,
                          course.id,
                          classroom.id,
                          course.number_of_students,
                          course.student
                      FROM 
                          classrooms as classroom
                      JOIN
                          courses as course
                      ON 
                          classroom.current_course_id = course.id
                      AND 
                          classroom.current_course_time_left = 0""")  # select all classrooms that are to be freed
    for result in cursor.fetchall():
        print("(" + str(i) + ") " + result[0] + ": " + result[1] + " is done")
        cursor.execute("DELETE FROM courses WHERE courses.id = ?", [result[2]])  # delete the finished course
        cursor.execute("""UPDATE
                                classrooms
                          SET
                                current_course_id = 0,
                                current_course_time_left = 0
                          WHERE
                                id = ? """, [result[3]])  # free up the finished classroom
        cursor.execute("""SELECT
                              classroom.location,
                              course.course_name,
                              course.id,
                              course.course_length,
                              classroom.id,
                              course.number_of_students,
                              course.student
                          FROM
                              courses as course
                          JOIN
                              classrooms as classroom
                          ON
                              course.class_id = ? 
                          AND 
                              course.class_id = classroom.id""", [result[3]])  # select a new course for the freed up classroom
        result = cursor.fetchone()
        if result:
            cursor.execute("""SELECT
                                  *
                              FROM
                                  classrooms as classroom
                              WHERE
                                  classroom.current_course_id = ?""", [result[2]])  # check if the course is currently active
            result1 = cursor.fetchone()
            if result1 is None:
                print("(" + str(i) + ") " + result[0] + ": " + result[1] + " is schedule to start")
                cursor.execute("""UPDATE
                                       classrooms
                                  SET
                                       current_course_id = ?,
                                       current_course_time_left = ?
                                  WHERE
                                       classrooms.id = ? """, [result[2], result[3], result[4]])
                cursor.execute("""UPDATE
                                       students
                                  SET
                                       count = count - ?
                                  WHERE
                                       students.grade = ? """, [result[5], result[6]])


def decrement_time(cursor):
    cursor.execute("""UPDATE classrooms SET current_course_time_left = current_course_time_left - 1
        WHERE current_course_time_left > 0 """)


def count_num_of_courses(cursor):
    cursor.execute("""SELECT count(*) as tot FROM courses""")
    return int(cursor.fetchone()[0])


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
    if data_base_existed:
        cursor = database_connection.cursor()
        courses_num = count_num_of_courses(cursor)
        i = 0
        while courses_num > 0:  # run as long as there are courses left to assign
            select_free_classroom(cursor, i)
            select_occupied_classrooms(cursor, i)
            select_done(cursor, i)
            print_tables(cursor)
            decrement_time(cursor)
            courses_num = count_num_of_courses(cursor)
            i += 1
        cursor.close()


if __name__ == '__main__':
    main()
