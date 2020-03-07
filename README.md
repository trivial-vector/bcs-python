# BCS-Python

## Using the Wrapper

### Getting Started

```python
>>> from bcswrapper import Bootcampspot

>>> bcs = Bootcampspot(email='johnsmith42@email.com', password='%d-%m-%Y')

>>> bcs.user
{'id': 42,
 'userName': 'johnsmith42@email.com',
 'firstName': 'John',
 'lastName': 'Smith',
 'email': 'johnsmith42@email.com',
 'githubUserName': 'MyPasswordIsStrfTime',

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

But how do I find out my courseId? _Well, since you asked_:

```python
# You have a few options:
# To get a nice view of your classes just print the instance

>>> print(bcs)
 |                     Class Name | courseID | enrollmentId |
 |----------------------------------------------------------|
0|  UT-MUNICH-UXUI-12-2042-U-C-MW |     1234 |       123456 |
1| UT-MUNICH-UXUI-12-2042-U-C-TTH |     2345 |       123456 |

# Or call bcs.class_details for a pandas friendly list of records

>>> bcs.class_details
[{'courseName':'UT-MUNICH-UXUI-12-2042-U-C-MW','courseId':1234, 'enrollmentId': 123456},
{'courseName':'UT-MUNICH-UXUI-12-2042-U-C-TTH','courseId':2345, 'enrollmentId': 234567}]
```

If you happen to enter an invalid course/enrollment id, the accompanying error message will give you a list of valid ids to work with.

Once you've set your `bcs.course`, both that course and it's accompanying `enrollmentId` will be used as the default parameters for all method calls. That doesn't mean you can't set your own when you call a method. If you want to make a call for a different course, just enter the corresponding parameter in the method. Your set course will stay set in the background until you manually change it.

**Note**: If you manually enter an `enrollmentId` parameter for a cohort with two classes, you will have to also enter a `courseId` parameter. The code isn't smart enough to know whether you want MW or TTH for a given cohort.

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
>>> df

                          Advanced Strings     Jiving with JavaScript      SQL is Old
Anya Novak                          present                   present          remote
Ken Burns                           present                   present         present
Sterling Archer                      remote                    absent          absent

# This allows you to do pandas things with your api responses
>>> df['Absences'] = df.isin(['absent']).sum(axis=1)
>>> df
                   Advanced Strings   Jiving with JavaScript   SQL is Old    Absences
Anya Novak                  present                  present       remote           0
Ken Burns                   present                  present      present           0
Sterling Archer              remote                   absent       absent           2

```

**@TODO**:

- students: info on students for a courseId
- weekly_feedback
- assignments

## Known Issues:

Both grades and attendance endpoints return all students from a given enrollment regardless of the chosen course. _However_, it doesn't appear as though the information from the route (letter grades or attendance values) are reported properly for students in the other courseId. This results in many false negatives for 'absent' and 'not submitted'.

I'm exploring a workaround that will call the session_closest endpoint and populate a list of students for a given courseId and then I'll mask the grades and attendance based on that. It's a hack and requires 3 total api calls instead of the 1 but it seems like the only reliable way to programmatically generate a list of students to filter against.
