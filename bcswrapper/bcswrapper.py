import json
import os
from datetime import datetime
from typing import Dict
import requests


class Bootcampspot:

    def __init__(self, email, password, student_ok=False):
        '''Get Auth and call `/me` endpoint for course info.'''

        _creds = {"email": email,
                  "password": password}

        self._bcs_root = "https://bootcampspot.com/api/instructor/v1"
        response = requests.post(
            f"{self._bcs_root}/login", json=_creds)
        self._auth = response.json()['authenticationInfo']['authToken']
        self._head = {
            'Content-Type': 'application/json',
            'authToken': self._auth
        }
        # Get relevent values
        me = requests.get(
            self._bcs_root + "/me", headers=self._head).json()
        self.user = me['userAccount']
        if student_ok:
            stu_check = None
        else:
            stu_check = 2
        self.courses = [{'courseName': enrollment['course']['name'], 'courseId': enrollment['courseId'], 'enrollmentId': enrollment['id']}
                        for enrollment in me['enrollments'] if enrollment['courseRoleId'] != stu_check]
        self._course = None
        self._enrollment = None

        self.course_list = [course['courseId']
                            for course in self.courses]

        self.enrollment_list = [course['enrollmentId']
                                for course in self.courses]

    def __repr__(self):
        '''Return list of course details on print'''
        return json.dumps(self.courses)

    @property
    def enrollment(self):
        return self._enrollment

    @enrollment.setter
    def enrollment(self, enrollmentId: int):
        if enrollmentId not in self.enrollment_list:
            msg = f'Invalid enrollmentId: {enrollmentId} not in your enrollments. Try one of these: {self.enrollment_list}'
            raise EnrollmentError(msg)
        elif not self._course == None:
            _enroll_match = [
                enrollment for enrollment in self.courses if course['courseId'] == self._course][0]
            if not enrollmentId == _enroll_match['enrollmentId']:
                msg = f"Invalid courseId: {enrollmentId} did not match enrollmentId for set courseId. Did you mean {_enroll_match['enrollmentId']}"
                raise EnrollmentError(msg)
        else:
            self.enrollment = enrollmentId

        '''
        if enrollmentId 

        '''

    @property
    def course(self):
        return self._course

    @course.setter
    def course(self, courseId=int):
        if courseId not in self.course_list:
            msg = f'Invalid courseId: {courseId} not in your courses. Try one of these: {self.course_list}'
            raise CourseError(msg)
        elif not self._enrollment == None:
            _course_match = [
                course for course in self.courses if course['enrollmentId'] == self._enrollment][0]
            if not courseId == _course_match['courseId']:
                msg = f"Invalid courseId: {courseId} did not match courseId for set enrollmentId. Did you mean {_course_match['courseId']}"
                raise CourseError(msg)
        else:
            self._course = courseId
            self._enrollment = [course['enrollmentId']
                                for course in self.courses if course['courseId'] == self._course][0]

    def _course_check(self, _course):
        # Set courseId if not set
        if not _course == None:
            if _course not in self.course_list:
                msg = f'Invalid courseId: {_course} not in your courses. Try one of these: {self.course_list}'
                raise CourseError(msg)
            else:
                return _course
        else:
            return self.course

    def _enrollment_check(self, _enrollment):
        # Set enrollmentId if not set
        if not _enrollment == None:
            if _enrollment not in self.enrollment_list:
                msg = f"Invalid enrollmentId: {_enrollment} not in your enrollments. Try one of these: {self.enrollment_list}"
                raise EnrollmentError(msg)
            else:
                return _enrollment
        else:
            return self.enrollment

    def _call(self, endpoint=str, body=dict):
        '''Grab response from endpoint'''
        response = requests.post(
            f"{self._bcs_root}/{endpoint}", headers=self._head, json=body)
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

        courseId = self._course_check(courseId)

        body = {'courseId': courseId}
        response = self._call('grades', body)
        _grades = {}

        def _value_check(grade):
            if type(grade) != str or grade == None:
                return "Not Submitted"
            else:
                return grade

        for assignment in response:
            if 'Milestone' in assignment['assignmentTitle'] and not milestones:
                pass
            else:
                try:
                    _grades[assignment['assignmentTitle']
                            ][assignment['studentName']] = _value_check(assignment['grade'])
                except:
                    _grades[assignment['assignmentTitle']] = {
                        assignment['studentName']: _value_check(assignment['grade'])}

        return _grades

    def sessions(self, courseId=None, enrollmentId=None, career_ok=False):
        '''Grabs All Sessions

        Response:
            {currentWeekSessions: {'session': {
                'name': 'Stuff', 'startTime': ISO8601,...}},
            calendarSessions: {'session':{
                'name':'Stuff','startTime':ISO8601,...}}
                }

        '''
        courseId = self._course_check(courseId)
        enrollmentId = self._enrollment_check(enrollmentId)

        body = {'enrollmentId': enrollmentId}

        # Perform API call
        sessions = self._call('sessions', body=body)

        sessions_list = []

        # Loop through current week sessions
        for session in sessions['calendarSessions']:

            session_info = session['session']
            session_type = session['context']['contextCode']

            # Filter on courseId and session code (to remove career entries)
            # Pull out session name, start time (ISO 8601 with UTC TZ removed)
            if session_info['courseId'] == courseId:
                if not career_ok and session_type == 'career':
                    pass
                else:
                    sessions_list.append({'id': session_info['id'],
                                          'name': session_info['name'],
                                          'shortDescription': session_info['shortDescription'],
                                          'longDescription': session_info['longDescription'],
                                          'startTime': session_info['startTime'][:-1],
                                          'chapter': session_info['chapter'],
                                          'type': session_type
                                          })

        return sessions_list

    def attendance(self, courseId=None, by='session'):
        '''Grab attendance

            Returns dict of {studentName: ('absences', 'pending', 'remote')}
        '''
        '''
        API Response Format:
        {
         'sessionName': str,
         'studentName': str,
         'pending': bool,
         'present': bool,
         'remote': bool,
         'excused': bool | |None
         }
        '''
        courseId = self._course_check(courseId)

        body = {'courseId': courseId}
        response = self._call(endpoint='attendance', body=body)

        def switch(session):
            if session['present'] == True and session['remote'] == False:
                return 'present'
            elif session['remote'] == True:
                return 'remote'
            elif session['excused'] == True and not session['excused'] == None:
                return 'excused'
            elif session['present'] == False and session['excused'] == False:
                return 'absent'

        _attendance = {}
        if by == 'session':
            by_not = 'student'
        else:
            by_not = 'session'

        for session in response:
            try:
                _attendance[session[by+'Name']][session[by_not+'Name']] = switch(
                    session)
            except:
                _attendance[session[by+'Name']] = {
                    session[by_not+'Name']: switch(session)}

        return _attendance

    def session_details(self, session_id: int) -> Dict:
        """Fetches session details for session matching session_id.

        Calls the sessionDetail endpoint to retrieve details about a session

        Args:
            session_id (int): takes an integer corresponding to a sessionId

        Returns:
            dict: The session details for the session matching session_id
        """

        body = {'sessionId': session_id}
        session_detail_response = self._call('sessionDetail', body)

        return session_detail_response['session']

    def session_closest(self, enrollmentId=None, courseId=None) -> Dict:
        """Fetches sessions list and returns nearest class to now.

        Based on the courseId and enrollmentId, it will call the sessions
        endpoint, find the closest session['startTime'] to datetime.utcnow()
        and call the sessionDetail endpoint using session['id'] corresponding
        to that session['startTime']

        Args:
            enrollmentId (int): takes an integer for the enrollmentId to pass
            courseId (int): courseId for the session you'd like to retrieve.

        Returns:
            dict: The course details for soonest class before or after current time.

        """

        courseId = self._course_check(courseId)
        enrollmentId = self._enrollment_check(enrollmentId)

        now = datetime.utcnow()
        session_list = self.sessions(
            enrollmentId=enrollmentId, courseId=courseId)

        def _closest_date(session_list: list, now):
            return min(session_list, key=lambda x: abs(datetime.fromisoformat(x['startTime']) - now))

        closest_session_id = _closest_date(session_list, now)['id']

        body = {'sessionId': closest_session_id}
        session_detail_response = self._call('sessionDetail', body)

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

    bcs = Bootcampspot()
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
