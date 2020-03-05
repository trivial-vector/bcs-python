# BCS-Python

## Getting started:

Your credentials for login are pulled from the environment variables `BCS_USER` (your email) and `BCS_PASS` (your password). You'll need to set them in your workspace.

In bash/zsh:

```bash
export BCS_USER="my.email@email.com"
export BCS_PASS="mypassword123"
```

In Windows Command Prompt:

```cmd
set BCS_USER="my.email@email.com"
set BCS_PASS="january1st1970"
```

## Using the Wrapper:

### Basic Usage

With your environment variables set, your code will look something like this:

```python
>>> from bcswrapper import Bootcampspot

>>> bcs = Bootcampspot()

>>> print(bcs)
[{'courseName':'UT-MUNICH-UXUI-12-2042-U-C-FT','courseId':1234, 'enrollmentId': 123456}]

>>> bcs.user
{'id': 42,
 'userName': 'my.email@email.com',
 'firstName': 'John',
 'lastName': 'Doe',
 'email': 'my.email@email.com',
 'githubUserName': 'MyPasswordIsMyBirthday',
...
```

### Getting Fancier

Setting the course will set your enrollment. Your `courseId` is the most specific identifier for a course so it's a good place to start.

```python
# Setting the course will set your enrollment
>>> bcs.course = 1234

>>> bcs.enrollment
123456
```

If you haven't set your course or you to use a different course, each method that requires a property as a parameter will take the course/enrollment/name as a keyword argument.

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

To get attendance
