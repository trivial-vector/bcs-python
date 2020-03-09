import json
import os
from datetime import datetime
from typing import Dict, Generator
import requests
from io import StringIO


class Bootcampspot:

    def __init__(self, email: str, password: str):
        '''Get Auth and call `/me` endpoint for course info.'''

        self.__creds = {"email": email,
                        "password": password}

        self.__bcs_root = "https://bootcampspot.com/api/instructor/v1"
        self.__login = requests.post(
            f"{self.__bcs_root}/login", json=self.__creds)
        self.__auth = self.__login.json()['authenticationInfo']['authToken']
        self.__head = {
            'Content-Type': 'application/json',
            'authToken': self.__auth
        }
        # Get relevent values
        me = requests.get(
            self.__bcs_root + "/me", headers=self.__head).json()
        self.user = me['userAccount']

        self.class_details = [{'courseName': enrollment['course']['name'], 'courseId': enrollment['courseId'], 'enrollmentId': enrollment['id']}
                              for enrollment in me['enrollments']]
        self.my_courses = [course['courseId']
                           for course in self.class_details]

        self.my_enrollments = [course['enrollmentId']
                               for course in self.class_details]

        self.my_cohorts = [course['courseName']
                           for course in self.class_details]

        self.__course = None
        self.__enrollment = None

    def __repr__(self):
        '''Return course details on print'''

        rows = len(self.my_courses)
        max_name = max([len(str(x)) for x in self.my_cohorts])

        if os.isatty(0):
            console_width, console_height = os.get_terminal_size()
            if rows+1 <= console_height and console_width >= max_name+40:
                name_fill = ' '*(max_name-11)

                def _repr_row_gen() -> Generator:
                    for idx, value in enumerate(reversed(self.class_details)):
                        course_pad = ' '*(9-len(str(value['courseId'])))
                        enroll_pad = ' '*(13-len(str(value['enrollmentId'])))
                        name_pad = ' ' * \
                            (max_name-len(str(value['courseName'])))
                        output_string = f"{idx}| {name_pad}{value['courseName']} |{course_pad}{value['courseId']} |{enroll_pad}{value['enrollmentId']} |\n"
                        yield output_string
                header = f" |{name_fill}  Class Name | courseID | enrollmentId |\n"
                output = StringIO("")
                output.write(header)
                output.write(f" {'-'*(len(header)-2)}\n")
                for row in _repr_row_gen():
                    output.write(row)
                return output.getvalue()
            else:
                return json.dumps(self.class_details)

        else:
            # @TODO: Make it pretty too
            return json.dumps(self.class_details)

    @property
    def enrollment(self):
        return self.__enrollment

    @enrollment.setter
    def enrollment(self, enrollmentId: int):
        if enrollmentId not in self.my_enrollments:
            msg = f'Invalid enrollmentId: {enrollmentId} not in your enrollments. Try one of these: {self.my_enrollments}'
            raise EnrollmentError(msg)
        elif not self._course == None:
            enroll_match = [
                enrollment for enrollment in self.class_details if course['courseId'] == self.__course][0]
            if not enrollmentId == enroll_match['enrollmentId']:
                msg = f"Invalid courseId: {enrollmentId} did not match enrollmentId for set courseId. Did you mean {enroll_match['enrollmentId']}"
                raise EnrollmentError(msg)
        else:
            self.__enrollment = enrollmentId

    @property
    def course(self):
        return self.__course

    @course.setter
    def course(self, courseId=int):
        if courseId not in self.my_courses:
            msg = f'Invalid courseId: {courseId} not in your courses. Try one of these: {self.my_courses}'
            raise CourseError(msg)
        elif not self.__enrollment == None:
            course_match = [
                course for course in self.class_details if course['enrollmentId'] == self.__enrollment][0]
            if not courseId == course_match['courseId']:
                msg = f"Invalid courseId: {courseId} did not match courseId for set enrollmentId. Did you mean {course_match['courseId']}"
                raise CourseError(msg)
        else:
            self.__course = courseId
            self.__enrollment = [course['enrollmentId']
                                 for course in self.class_details if course['courseId'] == self.__course][0]

    def __course_check(self, course):
        # Set courseId if not set
        if not course == None:
            if course not in self.my_courses:
                msg = f'Invalid courseId: {course} not in your courses. Try one of these: {self.my_courses}'
                raise CourseError(msg)
            else:
                enroll_match = [course['enrollmentId']
                                for course in self.class_details if course['courseId'] == self.__course][0]
                return course, enroll_match
        else:
            return self.__course, self.__enrollment

    def __enrollment_check(self, enrollment):
        # Set enrollmentId if not set
        if not enrollment == None:
            if enrollment not in self.my_enrollments:
                msg = f"Invalid enrollmentId: {enrollment} not in your enrollments. Try one of these: {self.my_enrollments}"
                raise EnrollmentError(msg)
            else:
                return enrollment
        else:
            return self.__enrollment

    def __call(self, endpoint=str, body=dict):
        '''Grab response from endpoint'''
        response = requests.post(
            f"{self.__bcs_root}/{endpoint}", headers=self.__head, json=body)
        if response.status_code == 200:
            return response.json()

    def grades(self, courseId=None, milestones=False):
        '''Grabs grades for students'''

        '''API Response:

          {
        "assignmentTitle": str,
        "studentName": str,
        "submitted": bool,
        "grade": str
        },
        '''

        courseId = self.__course_check(courseId)

        body = {'courseId': courseId}
        response = self.__call('grades', body)
        grades = {}

        def _value_check(grade):
            if type(grade) != str or grade == None:
                return "Not Submitted"
            else:
                return grade

        for assignment in response:
            if not milestones and 'Milestone' in assignment['assignmentTitle']:
                pass
            else:
                try:
                    grades[assignment['assignmentTitle']
                           ][assignment['studentName']] = _value_check(assignment['grade'])
                except:
                    grades[assignment['assignmentTitle']] = {
                        assignment['studentName']: _value_check(assignment['grade'])}

        return grades

    def sessions(self, course_id=None, enrollment_id=None, career_ok=False, orientation_ok=False):
        """Fetches session for course corresponding to courseId.

        Calls the sessions endpoint to retrieve details about a session

        Args:
            courseId (int): takes an integer corresponding to a courseId
            enrollmentId (int): takes an integer corresponding to an enrollmentId
            career_ok (bool): takes in a boolean to limit results to academic sessions.

        Returns:
            dict: The session details for the session matching session_id
        """
        if enrollment_id == None:
            course_id, enrollment_id = self.__course_check(course_id)
        else:
            enrollment_id = self.__enrollment_check(enrollment_id)

        body = {'enrollmentId': enrollment_id}

        # Perform API call
        sessions = self.__call('sessions', body=body)

        sessions_list = []

        def session_append(session):
            sessions_list.append({'id': session_info['id'],
                                  'name': session_info['name'],
                                  'short_description': session_info['shortDescription'],
                                  'long_description': session_info['longDescription'],
                                  'start_time': session_info['startTime'][:-1],
                                  'end_time': session_info['endTime'][:-1],
                                  'chapter': session_info['chapter'],
                                  'context': session_type,
                                  'classroom': session['classroom'],
                                  'video_url_list': session['videoUrlList']
                                  })

        def mask_check(session_type):
            if session_type == 'career':
                if career_ok:
                    return True
                else:
                    return False
            elif session_type == 'orientation':
                if orientation_ok:
                    return True
                else:
                    return False
            elif not course_id == None:
                if session_info['courseId'] == course_id:
                    return True
                else:
                    return False
            else:
                return True

        # Loop through current week sessions
        for session in sessions['calendarSessions']:

            session_info = session['session']
            session_type = session['context']['contextCode']

            # Filter on courseId and session code (to remove career entries)
            # Pull out session name, start time (ISO 8601 with UTC TZ removed)
            if mask_check(session_type):
                session_append(session)

        return sessions_list

    def attendance(self, course_id=None, by='session'):
        """Fetches attendance for each student/course.

        Calls the attendance uri and encodes the attendance value as a category.

        Args:
            course_id (int): takes an integer corresponding to a course_id

        Returns:
            dict: The student name, session name and attendance value.
        """
        course_id, enrollment_id = self.__course_check(course_id)

        body = {'courseId': course_id}
        response = self.__call(endpoint='attendance', body=body)

        def switch(session):
            if session['present'] == True and session['remote'] == False:
                return 'present'
            elif session['remote'] == True:
                return 'remote'
            elif session['excused'] == True and not session['excused'] == None:
                return 'excused'
            elif session['present'] == False and session['excused'] == False:
                return 'absent'

        attendance = {}
        by_not = 'student'

        if by == 'student':
            by_not = 'session'

        for session in response:
            try:
                attendance[session[by+'Name']][session[by_not+'Name']] = switch(
                    session)
            except:
                attendance[session[by+'Name']] = {
                    session[by_not+'Name']: switch(session)}

        return attendance

    def session_details(self, session_id: int) -> Dict:
        """Fetches session details for session matching session_id.

        Calls the sessionDetail endpoint to retrieve details about a session

        Args:
            session_id (int): takes an integer corresponding to a session_id

        Returns:
            dict: The session details for the session matching session_id
        """

        body = {'sessionId': session_id}
        session_detail_response = self.__call('sessionDetail', body)

        return session_detail_response['session']

    def session_closest(self, course_id=None) -> Dict:
        """Fetches sessions list and returns nearest class to now.

        Based on the courseId and enrollmentId, it will call the sessions
        endpoint, find the closest session['startTime'] to datetime.utcnow()
        and call the sessionDetail endpoint using session['id'] corresponding
        to that session['startTime']

        Args:
            enrollment_id (int): takes an integer for the enrollmentId to pass
            course_id (int): courseId for the session you'd like to retrieve.

        Returns:
            dict: The course details for soonest class before or after current time.

        """

        course_id, enrollment_id = self.__course_check(course_id)

        now = datetime.utcnow()
        session_list = self.sessions(
            course_id=course_id)

        def closest_date(session_list: list, now):
            return min(session_list, key=lambda x: abs(datetime.fromisoformat(x['startTime']) - now))

        closest_session_id = closest_date(session_list, now)['id']

        body = {'sessionId': closest_session_id}
        session_detail_response = self.__call('sessionDetail', body)

        return session_detail_response['session']['session']


class BCSError(Exception):
    """Base class for BCS Errors.

    Subclass of Exception built as a base class for various BCS Errors.
    Formatting of the error message is handled here using arguments passed down
    through it's subclasses.

    Args:
        msg (str): The body of the error message

    Returns:
        __str__ method to be passed to subclasses

    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class CourseError(BCSError):
    """Course choice not in your enrollments.

    Extension of the BCSError base class, existing primarily for the clear context
    an error name can give to a problem. In this case, it's a response to a bad courseId.

    Args:
        invalid_course (int): a bad courseId
        valid (dict): a dictionary with format {'msg': 'did you mean', 'valid_values': iterable}

    Raises:
        CourseError: msg
    """

    def __init__(self, msg):
        super().__init__(msg)


class EnrollmentError(BCSError):
    """Enrollment choice not in your enrollments.

    Extension of the BCSError base class, existing primarily for the clear context
    an error name can give to a problem. In this case, it's a response to a bad enrollmentId.

    Args:
        msg (str): A string representing the body of the error message.

    Raises:
        EnrollmentError: msg
    """

    def __init__(self, msg):
        super().__init__(msg)


if __name__ == "__main__":
    from colorama import init
    from termcolor import colored

    init()

    bcs = Bootcampspot(
        email=os.environ['BCS_USER'], password=os.environ['BCS_PASS'])
    bcs.course = 1158

    try:
        bcs.course = 1
    except CourseError:
        print(colored("CourseError", 'green'))
    try:
        bcs.enrollment = 1
    except EnrollmentError:
        print(colored('EnrollmentError', 'green'))
    try:
        assert bcs.enrollment == 249477
        print(colored('Auto Set Enrollment', 'green'))
    except AssertionError:
        print(colored('Auto Set Enrollment Failed', 'red'))
    try:
        assert type(list(bcs.grades().items())[0][0]) == str
        print(colored('grades()', 'green'))
    except AssertionError:
        print(colored('grades()', 'red'))
    try:
        type(list(bcs.attendance().items())[0][0]) == str
        print(colored('attendance()', 'green'))
    except AssertionError:
        print(colored('attendance()', 'red'))
