# BCS-Python

## Using the Wrapper

### Installation

The pre-alpha release is available on [test.pypi.org](test.pypi.org/project/Bootcampspot-python/0.0.1/). It can be installed just like any other pypi package. I will migrate the release to pypi when it's closer to finished.

_To install_

```
pip install -i https://test.pypi.org/simple/ Bootcampspot-python==0.0.1
```

### Getting Started

After import, pass in your login email and password to the Bootcampspot constructor.

**Note**: If you intend to publish anything using this online, _anywhere_, I would strongly suggest you do not pass the login values into the constructor as shown below. Use a hidden file or, better yet, environmental variables.

```
>>> from bcs.bootcampspot import Bootcampspot

>>> bcs = Bootcampspot(email='johnsmith42@email.com', password='%d-%m-%Y')

>>> bcs.user
{'id': 42,
 'userName': 'johnsmith42@email.com',
 'firstName': 'John',
 'lastName': 'Smith',
 'email': 'johnsmith42@email.com',
 'githubUserName': 'MyPasswordIsStrfTime',
```

Use `bcs.my_courses` for a simple list of Course IDs

```
>>> bcs.my_courses
[1234,2345]
```

Use `bcs.my_enrollments` for the Enrollment IDs

```
>>> bcs.my_enrollments
[123456]
```

### To get more information about your cohorts, you have a few options:

Simply printing the instance will give you a pretty view (non-interactive consoles)

```
>>> print(bcs)
 |                     Class Name | courseID | enrollmentId |
 |----------------------------------------------------------|
0|  UT-MUNICH-UXUI-12-2042-U-C-MW |     1234 |       123456 |
1| UT-MUNICH-UXUI-12-2042-U-C-TTH |     2345 |       123456 |
```

Or call `bcs.class_details` for a pandas friendly list of records

```
>>> bcs.class_details
[{'courseName':'UT-MUNICH-UXUI-12-2042-U-C-MW','courseId':1234, 'enrollmentId': 123456},
{'courseName':'UT-MUNICH-UXUI-12-2042-U-C-TTH','courseId':2345, 'enrollmentId': 234567}]
```

This is also, temporarily, the output of printing the instance in an interactive terminal, _e.g. jupyter notebook_

Setting the course will set your enrollment. Your `course_id` is the most specific identifier for a course so it's a good place to start. By setting the course, you also set the enrollment for your instance.

```
>>> bcs.course = 1234

>>> bcs.enrollment
123456
```

If you happen to enter an invalid course/enrollment id, the accompanying error message will give you a list of valid ids to work with. The same is true for setting enrollments.

```
>>> bcs.course = 1
Traceback (most recent call last):
  File "bcswrapper.py", line 399, in <module>
    bcs.course = 1
  File "bcswrapper.py", line 110, in course
    raise CourseError(msg)
CourseError: Invalid courseId '1' not in your courses. Try one of these: [1234, 2345]
```

Once you've set your `bcs.course`, both that course and it's accompanying `enrollmentId` will be used as the default parameters for all method calls. That doesn't mean you can't set your own when you call a method. If you want to make a call for a different course, just enter the corresponding parameter in the method. Your set course will stay set in the background until you manually change it.

**Note**: If you manually enter an `enrollmentId` parameter for a cohort with two classes, you will have to also enter a `courseId` parameter. The code isn't smart enough to know whether you want MW or TTH for a given cohort.

```
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
```

Without that argument the method will default to bcs.course

```
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

```
>>> import pandas as pd

>>> df = pd.DataFrame(bcs.attendance())
>>> df

                          Advanced Strings     Jiving with JavaScript      SQL is Old
Anya Novak                          present                   present          remote
Ken Burns                           present                   present         present
Sterling Archer                      remote                    absent          absent

```

This allows you to do pandas things with your api responses

```
>>> df['Absences'] = df.isin(['absent']).sum(axis=1)
>>> df
                   Advanced Strings   Jiving with JavaScript   SQL is Old    Absences
Anya Novak                  present                  present       remote           0
Ken Burns                   present                  present      present           0
Sterling Archer              remote                   absent       absent           2

```

The method itself sets the boolean values of the API response into categories for a given class to flatten the response. There is some logic applied by the wrapper to decode whatever logic is applied server side before the API call to get more consistent results. I will adjust the code as I understand more about what's going on server side. Just know what the wrapper returns is true so long as your student is actually in that courseId.

**@TODO**:

- [ ] students: info on students for a courseId
- [ ] weekly_feedback
- [ ] assignments
- [ ] finish docstrings for sphinx
- [ ] setup.py/Manifest.in
- [ ] swap over to environment.yml (use this to build requirements-dev.txt)

## Known Issues:

Both grades and attendance endpoints return all students from a given enrollment regardless of the chosen course. _However_, it doesn't appear as though the information from the route (letter grades or attendance values) are reported properly for students in the other courseId. This results in many false negatives for 'absent' and 'not submitted'.

I'm exploring a workaround that will call the session_details uri using the session_closest and populate a list of students for a given courseId and then I'll use the return as a mask for the grades and attendance based on that. It's a hack and requires 3 total api calls instead of the 1 but it seems like the only reliable way to generate a list of students to filter against for as many situations as possible.
