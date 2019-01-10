import os
import sqlite3
import create_db


# the main function
def main():
    os.remove("schedule.db")
    create_db.main()
    data_base_existed = os.path.isfile("schedule.db")
    database_connection = sqlite3.connect("schedule.db")  # connect to the database
    with database_connection:
        cursor = database_connection.cursor()
        cursor.execute("""SELECT count(*) as tot FROM courses""")
        courses_num = int(cursor.fetchone()[0])
        i = 1
        while data_base_existed and courses_num > 0:  # run as long as the database exists and there are courses left to assign
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
                                    classroom.current_course_id = 0""")
            if int(cursor.fetchone()[0]) > 0:
                for result in cursor.fetchall():
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
            cursor.execute("""SELECT 
                                  classroom.location, 
                                  course.course_name,
                                  classroom.id
                              FROM 
                                  classrooms as classroom 
                              JOIN 
                                  courses as course 
                              ON 
                                  classroom.id = course.class_id 
                              AND 
                                  classroom.current_course_time_left > 0""")
            for result in cursor.fetchall():
                print("(" + str(i) + ") " + result[0] + ": occupied by " + result[1])
                cursor.execute("""UPDATE
                                      classrooms
                                  SET
                                      current_course_time_left = current_course_time_left - 1
                                  WHERE
                                      classrooms.id = ? """, [result[2]])
            cursor.execute("""SELECT 
                                   classroom.location, 
                                   course.course_name,
                                   course.id
                              FROM 
                                   classrooms as classroom 
                              JOIN 
                                   courses as course 
                              ON 
                                   classroom.id = course.class_id 
                              AND 
                                   classroom.current_course_time_left = 0""")
            for result in cursor.fetchall():
                print("(" + str(i) + ") " + result[0] + ": " + result[1] + " is done")
                cursor.execute("""DELETE FROM courses WHERE courses.id = ?""", [result[2]])
            i = i + 1


if __name__ == '__main__':
    main()
