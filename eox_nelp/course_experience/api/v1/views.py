"""The generic views for course-experience API. Nelp flavour.
Classes:
- BaseJsonAPIView: General config of rest json api
    - ExperienceView: Config of experience views
        - UnitExperienceView: config for unit-exp views
            - LikeDislikeUnitExperienceView: class-view(`/eox-nelp/api/experience/v1/like/units/`)
            - ReportUnitExperienceView: class-view(`/eox-nelp/api/experience/v1/report/units/`)
        - CourseExperienceView: config for course-exp views
            - LikeDislikeCourseExperienceView: class-view(`/eox-nelp/api/experience/v1/like/courses/`)
            - ReportCourseExperienceView: class-view(`/eox-nelp/api/experience/v1/report/courses/`)
"""
from django.conf import settings
from django.http import Http404
from django.http.request import QueryDict
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from edx_rest_framework_extensions.auth.session.authentication import SessionAuthenticationAllowInactiveUser
from opaque_keys import InvalidKeyError
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework_json_api.django_filters import DjangoFilterBackend
from rest_framework_json_api.filters import OrderingFilter, QueryParameterValidationFilter
from rest_framework_json_api.metadata import JSONAPIMetadata
from rest_framework_json_api.pagination import JsonApiPageNumberPagination
from rest_framework_json_api.parsers import JSONParser
from rest_framework_json_api.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework_json_api.schemas.openapi import AutoSchema  # pylint: disable=no-name-in-module,syntax-error
from rest_framework_json_api.views import ModelViewSet

from eox_nelp.course_experience.models import LikeDislikeCourse, LikeDislikeUnit, ReportCourse, ReportUnit

from .serializers import (
    LikeDislikeCourseExperienceSerializer,
    LikeDislikeUnitExperienceSerializer,
    ReportCourseExperienceSerializer,
    ReportUnitExperienceSerializer,
)

INVALID_KEY_ERROR = {
    "error": "bad opaque key(item_id or course_id) `InvalidKeyError`"
}


class BaseJsonAPIView(ModelViewSet):
    """class to configure base json api parameter

    Ancestors:
        ModelViewSet : Django rest json api ModelViewSet
    """
    allowed_methods = ["POST", "GET", "PATCH"]

    authentication_classes = (JwtAuthentication, SessionAuthenticationAllowInactiveUser)
    permission_classes = (IsAuthenticated,)

    pagination_class = JsonApiPageNumberPagination
    parses_clasess = [
        JSONParser,
        FormParser,
        MultiPartParser,
    ]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer] if getattr(settings, 'DEBUG', None) else [JSONRenderer]

    metadata_class = JSONAPIMetadata
    schema_class = AutoSchema
    filter_backends = [
        QueryParameterValidationFilter,
        OrderingFilter,
        DjangoFilterBackend,
        SearchFilter,
    ]
    search_param = "filter[search]"


class ExperienceView(BaseJsonAPIView):
    """Class to set functionality of an ExperienceView.

    Ancestors:
        BaseJsonAPIView: Inherited for the rest json api config.
    """
    def get_queryset(self, *args, **kwargs):
        """Filter the queryset before being used.

        Returns:
            Queryset: queysyset using the super method, but filtered.
        """
        return super().get_queryset(*args, **kwargs).filter(author_id=self.request.user.id).order_by('id')

    def get_object(self):
        try:
            return super().get_object()
        except InvalidKeyError as exc:
            raise Http404 from exc

    def create(self, request, *args, **kwargs):
        """Perform processing for the request before use the base create method.
        Args:
            request: the request that arrives for create options.

        Returns:
            The return of ancestor create method with the request after processing.
        """
        request = self.change_author_data_2_request_user(request)
        try:
            return super().create(request, *args, **kwargs)
        except InvalidKeyError as exc:
            raise ValidationError(INVALID_KEY_ERROR) from exc

    def update(self, request, *args, **kwargs):
        """Perform processing for the request before use the base update method.
        Args:
            request: the request that arrives for create options.

        Returns:
            The return of ancestor update method with the request after processing.
        """
        request = self.change_author_data_2_request_user(request)
        try:
            return super().update(request, *args, **kwargs)
        except InvalidKeyError as exc:
            raise ValidationError(INVALID_KEY_ERROR) from exc

    def change_author_data_2_request_user(self, request):
        """Set the author object based in the request user.

        Args:
            request: The request to set the user.

        Returns:
            request: request with author updated.
        """
        if isinstance(request.data, QueryDict):
            request.data._mutable = True  # pylint: disable=protected-access
            request.data["author"] = f'{{"type": "User", "id": "{request.user.id}"}}'
            request.data._mutable = False  # pylint: disable=protected-access
        else:
            request.data["author"] = f'{{"type": "User", "id": "{request.user.id}"}}'
        return request


class UnitExperienceView(ExperienceView):
    """Class with  Experience view for units.

    Ancestors:
        ExperienceView: Inherited to set experience views config.

    """
    lookup_field = "item_id"
    lookup_url_kwarg = "item_id"
    lookup_value_regex = r"block[\w\W]*"


class CourseExperienceView(ExperienceView):
    """Class with  Experience view for courses.

    Args:
        ExperienceView: Inherited to set experience views config.

    """
    lookup_field = "course_id"
    lookup_url_kwarg = "course_id"
    lookup_value_regex = r"course[\w\W]*"


class LikeDislikeUnitExperienceView(UnitExperienceView):
    """Class view for LikeDislike unit experiences.
    Ancestors:
        UnitExperienceView: Inherited for units views config.

    ## Usage

    ### **GET** /eox-nelp/api/experience/v1/like/units/

    **GET Response Values**

    ``` json
    {
        "links": {
            "first": "https://lms-exmple.com/eox-nelp/api/experience/v1/like/units/?page%5Bnumber%5D=1",
            "last": "https://lms-exmple.com/eox-nelp/api/experience/v1/like/units/?page%5Bnumber%5D=1",
            "next": null,
            "prev": null
        },
        "data": [
            {
                "type": "LikeDislikeUnit",
                "id": "1",
                "attributes": {
                    "username": "michael",
                    "status": true,
                    "item_id": "block-v1:edX+test+t1+type@vertical+block@new_item"
                },
                "relationships": {
                    "author": {
                        "data": {
                            "type": "User",
                            "id": "7"
                        }
                    },
                    "course_id": {
                        "data": {
                            "type": "CourseOverview",
                            "id": "course-v1:edX+213+2121"
                        }
                    }
                }
            },
            {
                "type": "LikeDislikeUnit",
                "id": "2",
                "attributes": {
                    "username": "michael",
                    "status": true,
                    "item_id": "block-v1:edX+test+t1+type@vertical+block@new_item2"
                },
                "relationships": {
                    "author": {
                        "data": {
                            "type": "User",
                            "id": "7"
                        }
                    },
                    "course_id": {
                        "data": {
                            "type": "CourseOverview",
                            "id": "course-v1:edX+213+2121"
                        }
                    }
                }
            }
        ],
        "meta": {
            "pagination": {
                "page": 1,
                "pages": 1,
                "count": 2
            }
        }
    }
    ```

    ### **POST** /eox-nelp/api/experience/v1/like/units/

    request example data:
    ``` json
    {
        "status": false,
        "item_id": "block-v1:edX+test+t1+type@vertical+block@new_item2",
        "course_id": {
            "type": "CourseOverview",
            "id": "course-v1:edX+213+2121"
        }
    }
    ```

    ###  **GET-SPECIFIC** /eox-nelp/api/experience/v1/like/units/block-v1:edX+test+t1+type@vertical+block@new_item34/

    ###  **PATCH** /eox-nelp/api/experience/v1/like/units/block-v1:edX+test+t1+type@vertical+block@new_item34/

    request example data:
    ``` json
    {
        "status": false,
    }
    ```

    **POST, GET-ESPECIFIC,  PATCH  Response Values**
    ``` json
        {
        "data": {
            "type": "LikeDislikeUnit",
            "id": "4",
            "attributes": {
                "username": "michael",
                "status": true,
                "item_id": "block-v1:edX+test+t1+type@vertical+block@new_item345"
            },
            "relationships": {
                "author": {
                    "data": {
                        "type": "User",
                        "id": "7"
                    }
                },
                "course_id": {
                    "data": {
                        "type": "CourseOverview",
                        "id": "course-v1:edX+2323+232"
                    }
                }
            }
        }
    }
    ```
    """
    queryset = LikeDislikeUnit.objects.all()  # pylint: disable=no-member
    serializer_class = LikeDislikeUnitExperienceSerializer
    resource_name = "LikeDislikeUnit"


class ReportUnitExperienceView(UnitExperienceView):
    """Class view for Report unit experiences.
    Ancestors:
        UnitExperienceView: Inherited for units views config.

    ## Usage

    ### **GET** /eox-nelp/api/experience/v1/report/units/

    **GET Response Values**
    ``` json
    {
        "links": {
            "first": "https://lms-exmple.com/eox-nelp/api/experience/v1/report/units/?page%5Bnumber%5D=1",
            "last": "https://lms-exmple.com/eox-nelp/api/experience/v1/report/units/?page%5Bnumber%5D=1",
            "next": null,
            "prev": null
        },
        "data": [
            {
                "type": "ReportUnit",
                "id": "1",
                "attributes": {
                    "username": "michael",
                    "reason": "OO",
                    "item_id": "block-v1:edX+test+t1+type@vertical+block@new_item"
                },
                "relationships": {
                    "author": {
                        "data": {
                            "type": "User",
                            "id": "7"
                        }
                    },
                    "course_id": {
                        "data": {
                            "type": "CourseOverview",
                            "id": "course-v1:edX+213+2121"
                        }
                    }
                }
            },
            {
                "type": "ReportUnit",
                "id": "2",
                "attributes": {
                    "username": "michael",
                    "reason": "OO",
                    "item_id": "block-v1:edX+test+t1+type@vertical+block@new_item2"
                },
                "relationships": {
                    "author": {
                        "data": {
                            "type": "User",
                            "id": "7"
                        }
                    },
                    "course_id": {
                        "data": {
                            "type": "CourseOverview",
                            "id": "course-v1:edX+213+2121"
                        }
                    }
                }
            }
        ],
        "meta": {
            "pagination": {
                "page": 1,
                "pages": 1,
                "count": 2
            }
        }
    }
    ```

    ### **POST** /eox-nelp/api/experience/v1/report/units/

    request example data:
    ``` json
    {
        "reason": "SC",
        "item_id": "block-v1:edX+test+t1+type@vertical+block@new_item2",
        "course_id": {
            "type": "CourseOverview",
            "id": "course-v1:edX+213+2121"
        }
    }
    ```
    ###  **GET-SPECIFIC** /eox-nelp/api/experience/v1/report/units/block-v1:edX+test+t1+type@vertical+block@new_item34/

    ###  **PATCH** /eox-nelp/api/experience/v1/report/units/block-v1:edX+test+t1+type@vertical+block@new_item34/

    request example data:
    ``` json
    {
        "reason": "SC",
    }
    ```

    **POST, GET-ESPECIFIC,  PATCH  Response Values**
    ``` json
        {
        "data": {
            "type": "ReportUnit",
            "id": "4",
            "attributes": {
                "username": "michael",
                "reason": "SC",
                "item_id": "block-v1:edX+test+t1+type@vertical+block@new_item345"
            },
            "relationships": {
                "author": {
                    "data": {
                        "type": "User",
                        "id": "7"
                    }
                },
                "course_id": {
                    "data": {
                        "type": "CourseOverview",
                        "id": "course-v1:edX+2323+232"
                    }
                }
            }
        }
    }
    ```
    """
    queryset = ReportUnit.objects.all()  # pylint: disable=no-member
    serializer_class = ReportUnitExperienceSerializer
    resource_name = "ReportUnit"


class LikeDislikeCourseExperienceView(CourseExperienceView):
    """Class view for LikeDislike course experiences.
    Ancestors:
        UnitExperienceView: Inherited for courses views config.

    ## Usage

    ### **GET** /eox-nelp/api/experience/v1/like/courses/

    **GET Response Values**

    ``` json
    {
    "links": {
        "first": "https://lms-example.com/eox-nelp/api/experience/v1/like/courses/?page%5Bnumber%5D=1",
        "last": "https://lms-example.com/eox-nelp/api/experience/v1/like/courses/?page%5Bnumber%5D=1",
        "next": null,
        "prev": null
    },
    "data": [
        {
            "type": "LikeDislikeCourse",
            "id": "1",
            "attributes": {
                "username": "michael",
                "status": false
            },
            "relationships": {
                "author": {
                    "data": {
                        "type": "User",
                        "id": "7"
                    }
                },
                "course_id": {
                    "data": {
                        "type": "CourseOverview",
                        "id": "course-v1:edX+213+2121"
                    }
                }
            }
        },
        {
            "type": "LikeDislikeCourse",
            "id": "2",
            "attributes": {
                "username": "michael",
                "status": false
            },
            "relationships": {
                "author": {
                    "data": {
                        "type": "User",
                        "id": "7"
                    }
                },
                "course_id": {
                    "data": {
                        "type": "CourseOverview",
                        "id": "course-v1:bragi+cd101+2023y1"
                    }
                }
            }
        },
        ],
        "meta": {
            "pagination": {
                "page": 1,
                "pages": 1,
                "count": 2
            }
        }
    }
    ```

    ### **POST** /eox-nelp/api/experience/v1/like/courses/

    request example data:
    ``` json
    {
        "status": true,
        "course_id": {
            "type": "CourseOverview",
            "id": "course-v1:edX+213+2121"
        }
    }
    ```

    ###  **GET-SPECIFIC** /eox-nelp/api/experience/v1/like/courses/course-v1:edX+test+2023/

    ###  **PATCH** /eox-nelp/api/experience/v1/like/courses/course-v1:edX+test+2023/

    request example data:
    ``` json
    {
        "status": false,
    }
    ```

    **POST, GET-ESPECIFIC,  PATCH  Response Values**

    ``` json
    {
        "data": {
            "type": "LikeDislikeCourse",
            "id": "6",
            "attributes": {
                "username": "michael",
                "status": true
            },
            "relationships": {
                "author": {
                    "data": {
                        "type": "User",
                        "id": "7"
                    }
                },
                "course_id": {
                    "data": {
                        "type": "CourseOverview",
                        "id": "course-v1:edX+test+2023"
                    }
                }
            }
        }
    }
    ```
    """
    queryset = LikeDislikeCourse.objects.all()  # pylint: disable=no-member
    serializer_class = LikeDislikeCourseExperienceSerializer
    resource_name = "LikeDislikeCourse"


class ReportCourseExperienceView(CourseExperienceView):
    """Class view for Report course experiences.
    Ancestors:
        UnitExperienceView: Inherited for courses views config.

    ## Usage

    ### **GET** /eox-nelp/api/experience/v1/report/courses/

    **GET Response Values**

    ``` json
    {
    "links": {
        "first": "https://lms-example.com/eox-nelp/api/experience/v1/report/courses/?page%5Bnumber%5D=1",
        "last": "https://lms-example.com/eox-nelp/api/experience/v1/report/courses/?page%5Bnumber%5D=1",
        "next": null,
        "prev": null
    },
    "data": [
        {
            "type": "ReportCourse",
            "id": "1",
            "attributes": {
                "username": "michael",
                "reason": "OO"
            },
            "relationships": {
                "author": {
                    "data": {
                        "type": "User",
                        "id": "7"
                    }
                },
                "course_id": {
                    "data": {
                        "type": "CourseOverview",
                        "id": "course-v1:edX+213+2121"
                    }
                }
            }
        },
        {
            "type": "ReportCourse",
            "id": "2",
            "attributes": {
                "username": "michael",
                "reason": "OO"
            },
            "relationships": {
                "author": {
                    "data": {
                        "type": "User",
                        "id": "7"
                    }
                },
                "course_id": {
                    "data": {
                        "type": "CourseOverview",
                        "id": "course-v1:bragi+cd101+2023y1"
                    }
                }
            }
        },
        ],
        "meta": {
            "pagination": {
                "page": 1,
                "pages": 1,
                "count": 2
            }
        }
    }
    ```

    ### **POST** /eox-nelp/api/experience/v1/report/courses/

    request example data:
    ``` json
    {
        "report": "SC",
        "course_id": {
            "type": "CourseOverview",
            "id": "course-v1:edX+213+2121"
        }
    }
    ```

    ###  **GET-SPECIFIC** /eox-nelp/api/experience/v1/report/courses/course-v1:edX+test+2023/

    ###  **PATCH** /eox-nelp/api/experience/v1/report/courses/course-v1:edX+test+2023/

    request example data:
    ``` json
    {
        "reason": "SC",
    }
    ```

    **POST, GET-ESPECIFIC,  PATCH  Response Values**
    ``` json
    {
        "data": {
            "type": "ReportCourse",
            "id": "6",
            "attributes": {
                "username": "michael",
                "reason": "SC"
            },
            "relationships": {
                "author": {
                    "data": {
                        "type": "User",
                        "id": "7"
                    }
                },
                "course_id": {
                    "data": {
                        "type": "CourseOverview",
                        "id": "course-v1:edX+test+2023"
                    }
                }
            }
        }
    }
    ```
    """
    queryset = ReportCourse.objects.all()  # pylint: disable=no-member
    serializer_class = ReportCourseExperienceSerializer
    resource_name = "ReportCourse"
