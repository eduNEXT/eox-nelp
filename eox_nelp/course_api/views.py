"""
Course API Views
"""


from eox_nelp.edxapp_wrapper.course_api import CourseDetailView, CourseListView

from .serializers import NelpCourseDetailSerializer


class NelpCourseDetailView(CourseDetailView):
    """
    **Use Cases**

        Request details for a course

    **Example Requests**

        GET /api/courses/v1/courses/{course_key}/

    **Response Values**

        Body consists of the following fields:

        * effort: A textual description of the weekly hours of effort expected
            in the course.
        * end: Date the course ends, in ISO 8601 notation
        * enrollment_end: Date enrollment ends, in ISO 8601 notation
        * enrollment_start: Date enrollment begins, in ISO 8601 notation
        * id: A unique identifier of the course; a serialized representation
            of the opaque key identifying the course.
        * media: An object that contains named media items.  Included here:
            * course_image: An image to show for the course.  Represented
              as an object with the following fields:
                * uri: The location of the image
        * name: Name of the course
        * number: Catalog number of the course
        * org: Name of the organization that owns the course
        * overview: A possibly verbose HTML textual description of the course.
            Note: this field is only included in the Course Detail view, not
            the Course List view.
        * short_description: A textual description of the course
        * start: Date the course begins, in ISO 8601 notation
        * start_display: Readably formatted start of the course
        * start_type: Hint describing how `start_display` is set. One of:
            * `"string"`: manually set by the course author
            * `"timestamp"`: generated from the `start` timestamp
            * `"empty"`: no start date is specified
        * pacing: Course pacing. Possible values: instructor, self
        * course_about_url: about url to the course.
        * course_overview: raw html course overview from studio.
        * course_overview_object: parsed raw html course overview.

        Deprecated fields:

        * blocks_url: Used to fetch the course blocks
        * course_id: Course key (use 'id' instead)

    **Parameters:**

        username (optional):
            The username of the specified user for whom the course data
            is being accessed. The username is not only required if the API is
            requested by an Anonymous user.

    **Returns**

        * 200 on success with above fields.
        * 400 if an invalid parameter was sent or the username was not provided
          for an authenticated request.
        * 403 if a user who does not have permission to masquerade as
          another user specifies a username other than their own.
        * 404 if the course is not available or cannot be seen.

        Example response:

            {
                "blocks_url": "/api/courses/v1/blocks/?course_id=edX%2Fexample%2F2012_Fall",
                "media": {
                    "course_image": {
                        "uri": "/c4x/edX/example/asset/just_a_test.jpg",
                        "name": "Course Image"
                    }
                },
                "description": "An example course.",
                "end": "2015-09-19T18:00:00Z",
                "enrollment_end": "2015-07-15T00:00:00Z",
                "enrollment_start": "2015-06-15T00:00:00Z",
                "course_id": "edX/example/2012_Fall",
                "name": "Example Course",
                "number": "example",
                "org": "edX",
                "overview: "<p>A verbose description of the course.</p>"
                "start": "2015-07-17T12:00:00Z",
                "start_display": "July 17, 2015",
                "start_type": "timestamp",
                "pacing": "instructor",
                "course_about_url" "https://domain.course/about",
                "course_overview": "<h1>...</h1>",
                "overview_object": {
                    "about_description": [
                        {
                            "titles": [
                                "About This Course"
                            ],
                            "paragraphs": [
                                "Include your long course description here. Description should contain 150-400 words.",

                        }
                    ],
                    "staff": {
                        "titles": [
                            [
                                [
                                    "Course Staff"
                                ]
                            ]
                        ],
                        "teachers": [
                            {
                                "name": [
                                    "Staff Member #1"
                                ],
                                "bio": [
                                    "Biography of instructor/staff member #1"
                                ],
                                "image_url": [
                                    "http://lms.mango.edunext.link:8000/static/images/placeholder-faculty.png"
                                ]
                            }
                        ]
                    },
                    "prereqs": [
                        {
                            "titles": [
                                "Requirements"
                            ],
                            "paragraphs": [
                                "Add information about the skills and knowledge students need to take this course."
                            ]
                        }
                    ],
                    "faq": [
                        {
                            "h3_questions": [
                                "What web browser should I use?"
                            ],
                            "p_answers": [
                                "The Open edX platform works with Chrome, Edge, Firefox, Internet Explorer, or Safari.",
                                "See our list of supported browsers for the most up-to-date information."
                            ]
                        },
                    ]
                }
            }
    """

    serializer_class = NelpCourseDetailSerializer


class NelpCourseListView(CourseListView):
    """
    **Use Cases**

        Request information on all courses visible to the specified user.

    **Example Requests**

        GET /api/courses/v1/courses/

    **Response Values**

        Body comprises a list of objects as returned by `CourseDetailView`.

    **Parameters**

        search_term (optional):
            Search term to filter courses (used by ElasticSearch).

        username (optional):
            The username of the specified user whose visible courses we
            want to see. The username is not required only if the API is
            requested by an Anonymous user.

        org (optional):
            If specified, visible `CourseOverview` objects are filtered
            such that only those belonging to the organization with the
            provided org code (e.g., "HarvardX") are returned.
            Case-insensitive.

    **Returns**

        * 200 on success, with a list of course discovery objects as returned
          by `CourseDetailView`.
        * 400 if an invalid parameter was sent or the username was not provided
          for an authenticated request.
        * 403 if a user who does not have permission to masquerade as
          another user specifies a username other than their own.
        * 404 if the specified user does not exist, or the requesting user does
          not have permission to view their courses.

        Example response:

            [
              {
                "blocks_url": "/api/courses/v1/blocks/?course_id=edX%2Fexample%2F2012_Fall",
                "media": {
                  "course_image": {
                    "uri": "/c4x/edX/example/asset/just_a_test.jpg",
                    "name": "Course Image"
                  }
                },
                "description": "An example course.",
                "end": "2015-09-19T18:00:00Z",
                "enrollment_end": "2015-07-15T00:00:00Z",
                "enrollment_start": "2015-06-15T00:00:00Z",
                "course_id": "edX/example/2012_Fall",
                "name": "Example Course",
                "number": "example",
                "org": "edX",
                "start": "2015-07-17T12:00:00Z",
                "start_display": "July 17, 2015",
                "start_type": "timestamp",
                "course_about_url" "https://domain.course/about",
                "course_overview": "<h1>...</h1>",
                "overview_object": {
                    "about_description": [
                        {
                            "titles": [
                                "About This Course"
                            ],
                            "paragraphs": [
                                "Include your long course description here. should contain 150-400 words.",

                        }
                    ],
                    "staff": {
                        "titles": [
                            [
                                [
                                    "Course Staff"
                                ]
                            ]
                        ],
                        "teachers": [
                            {
                                "name": [
                                    "Staff Member #1"
                                ],
                                "bio": [
                                    "Biography of instructor/staff member #1"
                                ],
                                "image_url": [
                                    "http://lms.mango.edunext.link:8000/static/images/placeholder-faculty.png"
                                ]
                            }
                        ]
                    },
                    "prereqs": [
                        {
                            "titles": [
                                "Requirements"
                            ],
                            "paragraphs": [
                                "Add information about the skills and knowledge students need to take this course."
                            ]
                        }
                    ],
                    "faq": [
                        {
                            "h3_questions": [
                                "What web browser should I use?"
                            ],
                            "p_answers": [
                                "The Open edX  works best with  Chrome, Edge, Firefox, Internet Explorer, or Safari.",
                                "See our list of supported browsers for the most up-to-date information."
                            ]
                        },
                    ]
                }
            }
            ]
    """

    serializer_class = NelpCourseDetailSerializer
