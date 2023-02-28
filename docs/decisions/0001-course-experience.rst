Courses units in LMS
--------------

Status
======

Accepted

Context
=======

NELP business case requires multiples features that are not part
of open-edx platform core, and it's necessary a new implementation
that allows users to report and share their opinions about the
course content and experience during the course.

Decisions
=========

1. Create a course experience module.
2. Create ``LikeDislikeCourse`` model with the following fields.

  * author => Foreign key to user model, the user who set their opinion.

  * status => Boolean field with choices: 1=Liked, 0=disliked and None=not-set.

  * course_id => Foreign key to course overview model, course identifier.

3. Create ``LikeDislikeUnit`` model with the following fields.

  * author => Foreign key to user model, the user who set their opinion.

  * status => Boolean field with choices: 1=Liked, 0=disliked and None=not-set.

  * item_id => UsageKeyField, this is course unit identifier.

  * course_id => Foreign key to course overview model, course identifier.

4. Create ``ReportCourse`` model with the following fields.

  * author => Foreign key to user model, the user who set their opinion.

  * reason => String field with choices:

   - Sexual content

   - Graphic violence.

   - Hateful or abusive content.

   - Copycat or impersonation.

   - Other objection.

  * course_id => Foreign key to course overview model, course identifier.

5. Create ``ReportUnit`` model with the following fields.

  * author => Foreign key to user model, the user who set their opinion.

  * reason => String field with choices:

   - Sexual content

   - Graphic violence.

   - Hateful or abusive content.

   - Copycat or impersonation.

   - Other objection.

  * item_id => UsageKeyField, this is course unit identifier.

  * course_id => Foreign key to course overview model, course identifier.

6. Set model constrains, each model should be unique per units and user or course and user.
7. Create API views for each model.


API Examples for units
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  GET request

  /eox-nelp/api/experience/v1/like/units/<usage-id>/

  Response

  .. code-block:: json

      {
        "data": {
         "type": "like-unit"
         "attributes": {
           "usage-id": "block-v1:edX+C102+2022-t3+type@vertical+block@437dedc792a648e0b90911b8349d769f",
           "status": "disliked"
         },
         "links": {
           "self": "/eox-nelp/api/experience/v1/like/units/block-v1:edX+C102+2022-t3+type@vertical+block@437dedc792a648e0b90911b8349d769f/"
         }
        }
      }

  POST request

  /eox-nelp/api/experience/v1/like/units/<usage-id>/

  .. code-block:: json

      {
        "usage-id": "block-v1:edX+C102+2022-t3+type@vertical+block@437dedc792a648e0b90911b8349d769f",
        "status": "liked"
      }

  Response

  .. code-block:: json

      {
        "data": {
         "type": "like-unit"
         "attributes": {
           "usage-id": "block-v1:edX+C102+2022-t3+type@vertical+block@437dedc792a648e0b90911b8349d769f",
           "status": "liked"
         },
         "links": {
           "self": "/eox-nelp/api/experience/v1/like/units/block-v1:edX+C102+2022-t3+type@vertical+block@437dedc792a648e0b90911b8349d769f/"
         }
        }
      }

  GET request

  /eox-nelp/api/experience/v1/report/units/<usage-id>/

  Response

  .. code-block:: json

      {
        "data": {
         "type": "report-unit"
         "attributes": {
           "usage-id": "block-v1:edX+C102+2022-t3+type@vertical+block@437dedc792a648e0b90911b8349d769f",
           "reason": "sexual_content"
         },
         "links": {
           "self": "/eox-nelp/api/experience/v1/report/units/block-v1:edX+C102+2022-t3+type@vertical+block@437dedc792a648e0b90911b8349d769f/"
         }
        }
      }

  POST request

  /eox-nelp/api/experience/v1/report/units/<usage-id>/

  .. code-block:: json

      {
        "usage-id": "block-v1:edX+C102+2022-t3+type@vertical+block@437dedc792a648e0b90911b8349d769f",
        "reason": "sexual_content"
      }

  Response

  .. code-block:: json

      {
        "data": {
         "type": "report-unit"
         "attributes": {
           "usage-id": "block-v1:edX+C102+2022-t3+type@vertical+block@437dedc792a648e0b90911b8349d769f",
           "reason": "sexual_content"
         },
         "links": {
           "self": "/eox-nelp/api/experience/v1/report/units/block-v1:edX+C102+2022-t3+type@vertical+block@437dedc792a648e0b90911b8349d769f/"
         }
        }
      }


API Examples for courses
~~~~~~~~~~~~~~~~~~~~~~~~

  GET request

  /eox-nelp/api/experience/v1/like/courses/<course-id>/

  Response

  .. code-block:: json

      {
        "data": {
         "type": "rate-course"
         "attributes": {
           "course-id": "course-v1:test+CS501+2022_T4",
           "status": "disliked"
         },
         "links": {
           "self": "/eox-nelp/api/experience/v1/like/courses/course-v1:test+CS501+2022_T4/"
         }
        }
      }

  POST request

  /eox-nelp/api/experience/v1/like/courses/<course-id>/

  .. code-block:: json

      {
        "course-id": "course-v1:test+CS501+2022_T4",
        "status": "liked"
      }

  Response

  .. code-block:: json

      {
        "data": {
         "type": "rate-course"
         "attributes": {
           "course-id": "course-v1:test+CS501+2022_T4",
           "status": "liked"
         },
         "links": {
           "self": "/eox-nelp/api/experience/v1/like/courses/course-v1:test+CS501+2022_T4/"
         }
        }
      }

  GET request

  /eox-nelp/api/experience/v1/report/courses/<course-id>/

  Response

  .. code-block:: json

      {
        "data": {
         "type": "report-course"
         "attributes": {
           "course-id": "course-v1:test+CS501+2022_T4",
           "reason": "sexual_content"
         },
         "links": {
           "self": "/eox-nelp/api/experience/v1/report/courses/course-v1:test+CS501+2022_T4/"
         }
        }
      }

  POST request

  /eox-nelp/api/experience/v1/report/courses/<course-id>/

  .. code-block:: json

      {
        "course-id": "course-v1:test+CS501+2022_T4",
        "reason": "sexual_content"
      }

  Response

  .. code-block:: json

      {
        "data": {
         "type": "report-course"
         "attributes": {
           "course-id": "course-v1:test+CS501+2022_T4",
           "reason": "sexual_content"
         },
         "links": {
           "self": "/eox-nelp/api/experience/v1/report/courses/course-v1:test+CS501+2022_T4/"
         }
        }
      }

Consequences
============

1. This won't modify or alter the current platform behavior.
2. This doesn't cover the client experience, this just covers the backend requirements, therefore its frontend implementation must be done later in the right place.
