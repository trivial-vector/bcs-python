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
