"""Functions that extend the edx-platform behavior based on Django
signals, to check with method is used, go to the apps.py file and
verify the connections.

Functions:
    send_futurex_progress: it will publish the user progress.
"""


def send_futurex_progress(**kwargs):  # pylint: disable=unused-argument
    """General function to handle completed units"""
