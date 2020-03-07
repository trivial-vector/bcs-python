# BCS-Python

## Using the Wrapper

### Getting Started

```python
>>> from bcswrapper import Bootcampspot

>>> bcs = Bootcampspot(email='johnsmith42@email.com', password='%d-%m-%Y')

>>> print(bcs)
[{'courseName':'UT-MUNICH-UXUI-12-2042-U-C-MW','courseId':1234, 'enrollmentId': 123456},
{'courseName':'UT-MUNICH-UXUI-12-2042-U-C-TTH','courseId':2345, 'enrollmentId': 123456}]

>>> bcs.user
{'id': 42,
 'userName': 'johnsmith42@email.com',
 'firstName': 'John',
 'lastName': 'Smith',
 'email': 'johnsmith42@email.com',
 'githubUserName': 'MyPasswordIsMyBirthday',

>>> bcs.my_courses
[1234,2345]

>>> bcs.my_enrollments
[123456]

```

Setting the course will set your enrollment. Your `courseId` is the most specific identifier for a course so it's a good place to start.

```python
# Setting the course will set your enrollment
>>> bcs.course = 1234

>>> bcs.enrollment
123456
```

But how do I find out my courseId? _Well since you asked_:

```python
# After class construction, call bcs.courses at any time to get a list of records
# with courseId, enrollmentId and courseName

>>> bcs.class_details

[{'courseName':'UT-MUNICH-UXUI-12-2042-U-C-MW','courseId':1234, 'enrollmentId': 123456},
{'courseName':'UT-MUNICH-UXUI-12-2042-U-C-TTH','courseId':2345, 'enrollmentId': 234567}]
```

This is also tied, _temporarily_, to the `__repr__` function for the `Bootcampspot` class so printing your instance will give you the same functionality.

Don't worry about messing it up either! If, at any time, you enter an invalid `courseId` or `enrollmentId`, the accompanying error message will give you a list of valid ids to work with.

If you haven't set your course or you want to use a different course, each method that requires a property as a parameter will take the course/enrollment/name as a keyword argument.

```python
# Setting the course isn't permanent
>>> bcs.course = 1234

>>> bcs.grades(courseId=2345)
{'0: Prework':{
    'Abe Lincoln': 'A',
    'Clifford the Dog': 'Unsubmitted',
    'Jane Doe': 'Incomplete'},
'1: Hello, World':{
    'Abe Lincoln': 'A+',
    'Clifford the Dog': 'B',
    'Jane Doe': 'Incomplete'}}

# Without that kwarg the method will default to bcs.course
>>> bcs.grades()
{'0: Prework':{
    'Anya Novak': 'A',
    'Ken Burns': 'Unsubmitted',
    'Sterling Archer': 'Incomplete'},
'1: Hello, World':{
    'Anya Novak': 'A+',
    'Ken Burns': 'B',
    'Sterling Archer': 'Incomplete'}}
```

Attendance can be fetched by calling the attendance method. Like the grades method, it will use your set `courseId` as a default. The resulting data structure (as are all the outputs) is designed to be table friendly so it can be called directly into a DataFrame instance.

```python
>>> import pandas as pd

>>> df = pd.DataFrame(bcs.attendance())

# Insert table here
```

**@TODO**:

- sessions: all calendar sessions **prototyped**
- session_closest: closest session to right now **prototyped**
- session_details: info on a given session (Also all student info?!) **prototyped**
- students: info on students for a courseId
- weekly_feedback
- assignments
- tests: this was designed to be test driven but I got a little carried away last night

## Known Issues:

Both grades and attendance endpoints return all students from a given enrollment regardless of the chosen course. _However_, it doesn't appear as though the information from the route (letter grades or attendance values) are reported properly for students in the other courseId. This results in many false negatives for 'absent' and 'not submitted'.

I'm exploring a workaround that will call the session_closest endpoint and populate a list of students for a given courseId and then I'll mask the grades and attendance based on that. It's a hack and requires 3 total api calls instead of the 1 but it seems like the only reliable way to programmatically generate a list of students to filter against.
