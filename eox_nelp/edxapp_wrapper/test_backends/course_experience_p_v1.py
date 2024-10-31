"""Test backend for course_experience module."""


def get_course_home_url():
    """Return test function.
    Returns:
        string for testing basic home url
    """
    return lambda course_key: f"http://testserver/learning/course/{course_key}/home"
