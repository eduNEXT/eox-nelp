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
2. Create ``RateCourse`` model with the following fields.

  * author => Foreign key to user model, the user who set their opinion.

  * status => String field with choices: Liked, disliked and not-set.

  * course_id => String field, course identifier to allow course rating.

3. Create ``RateSection`` model with the following fields.

  * author => Foreign key to user model, the user who set their opinion.

  * status => String field with choices: Liked, disliked and not-set.

  * item_id => String field, this is course subsection identifier.

4. Create ``ReportCourse`` model with the following fields.

  * author => Foreign key to user model, the user who set their opinion.

  * reason => String field with choices:

   - Sexual content

   - Graphic violence.

   - Hateful or abusive content.

   - Copycat or impersonation.

   - Other objection.

  * course_id => String field, course identifier to allow course rating.

5. Create ``ReportSection`` model with the following fields.

  * author => Foreign key to user model, the user who set their opinion.

  * reason => String field with choices:

   - Sexual content

   - Graphic violence.

   - Hateful or abusive content.

   - Copycat or impersonation.

   - Other objection.

  * item_id => String field, this is course subsection identifier.

6. Set model constrains, each model should be unique per sub-sections and user or course and user.
7. Create API views for each model.


API Examples for sub-sections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  GET request

  /eox-nelp/api/experience/v1/rate/sections/<usage-id>/

  Response

  .. code-block:: json

      {
        "data": {
         "type": "rate-section"
         "attributes": {
           "usage-id": "block-v1:edX+C102+2022-t3+type@vertical+block@437dedc792a648e0b90911b8349d769f",
           "status": "disliked"
         },
         "links": {
           "self": "/eox-nelp/api/experience/v1/rate/sections/block-v1:edX+C102+2022-t3+type@vertical+block@437dedc792a648e0b90911b8349d769f/"
         }
        }
      }

  PUT request

  /eox-nelp/api/experience/v1/rate/sections/<usage-id>/

  .. code-block:: json

      {
        "usage-id": "block-v1:edX+C102+2022-t3+type@vertical+block@437dedc792a648e0b90911b8349d769f",
        "status": "liked"
      }

  Response

  .. code-block:: json

      {
        "data": {
         "type": "rate-section"
         "attributes": {
           "usage-id": "block-v1:edX+C102+2022-t3+type@vertical+block@437dedc792a648e0b90911b8349d769f",
           "status": "liked"
         },
         "links": {
           "self": "/eox-nelp/api/experience/v1/rate/sections/block-v1:edX+C102+2022-t3+type@vertical+block@437dedc792a648e0b90911b8349d769f/"
         }
        }
      }

  GET request

  /eox-nelp/api/experience/v1/report/sections/<usage-id>/

  Response

  .. code-block:: json

      {
        "data": {
         "type": "report-section"
         "attributes": {
           "usage-id": "block-v1:edX+C102+2022-t3+type@vertical+block@437dedc792a648e0b90911b8349d769f",
           "reason": "sexual_content"
         },
         "links": {
           "self": "/eox-nelp/api/experience/v1/report/sections/block-v1:edX+C102+2022-t3+type@vertical+block@437dedc792a648e0b90911b8349d769f/"
         }
        }
      }

  PUT request

  /eox-nelp/api/experience/v1/report/sections/<usage-id>/

  .. code-block:: json

      {
        "usage-id": "block-v1:edX+C102+2022-t3+type@vertical+block@437dedc792a648e0b90911b8349d769f",
        "reason": "sexual_content"
      }

  Response

  .. code-block:: json

      {
        "data": {
         "type": "report-section"
         "attributes": {
           "usage-id": "block-v1:edX+C102+2022-t3+type@vertical+block@437dedc792a648e0b90911b8349d769f",
           "reason": "sexual_content"
         },
         "links": {
           "self": "/eox-nelp/api/experience/v1/report/sections/block-v1:edX+C102+2022-t3+type@vertical+block@437dedc792a648e0b90911b8349d769f/"
         }
        }
      }


API Examples for courses
~~~~~~~~~~~~~~~~~~~~~~~~

  GET request

  /eox-nelp/api/experience/v1/rate/courses/<course-id>/

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
           "self": "/eox-nelp/api/experience/v1/rate/courses/course-v1:test+CS501+2022_T4/"
         }
        }
      }

  PUT request

  /eox-nelp/api/experience/v1/rate/courses/<course-id>/

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
           "self": "/eox-nelp/api/experience/v1/rate/courses/course-v1:test+CS501+2022_T4/"
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

  PUT request

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
