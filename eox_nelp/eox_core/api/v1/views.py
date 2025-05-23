"""
Eox-nelp API v1 views to extender eox-core api v1 views.
"""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from eox_core.api.v1.views import EdxappUser as CoreEdxappUser
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .serializers import NelpUserReadOnlySerializer

User = get_user_model()

class NelpEdxappUser(CoreEdxappUser):
    """
    Handles the users' actions for the API-V1.
    This class inherits all functionality from eox-core's EdxappUser view.
    """
    def get(self, request, *args, **kwargs):
        """
        Retrieves information about an edxapp user,
        given an email or a username.

        The username prevails over the email when both are provided to get the user.

        **Example Requests**

            GET eox-nelp/eox-core/api/v1/user/?username=johndoe

            Query parameters: {
              "username": "johndoe",
            }

        **Response details**

        - `username (str)`: Username of the edxapp user
        - `is_active (str)`: Indicates if the user is active on the platform
        - `email (str)`: Email of the user
        - `gender (str)`: Gender of the user
        - `date_joined (str)`: Date for when the user was registered in the platform
        - `name (str)`: Fullname of the user
        - `country (str)`: Country of the user
        - `level_of_education (str)`: Level of education of the user
        - `year_of_birth (int)`: Year of birth of the user
        - `bio (str)`: Bio of the user
        - `goals (str)`: Goals of the user
        - `extended_profile (list)`: List of dictionaries that contains the user-profile meta fields
            - `field_name (str)`: Name of the extended profile field
            - `field_value (str)`: Value of the extended profile field
        - `mailing_address (str)`
        - `social_links (List)`: List that contains the social links of the user, if any.
        - `account_privacy (str)`: Indicates the account privacy type
        - `state (str)`: State (only for US)
        - `secondary_email (str)`: Secondary email of the user
        - `profile_image (dictionary)`:
            - `has_image (Bool)`: Indicates if user has profile image
            - `image_url_medium (str)`: Url of the profile image in medium size
            - `image_url_small (str)`: Url of the profile image in small size
            - `image_url_full (str)`: Url of the profile image in full size,
            - `image_url_large (str)`: Url of the profile image in large size
        - `secondary_email_enabled (Bool)`: Indicates if the secondary email is enable
        - `phone_number (str)`: Phone number of the user
        - `requires_parental_consent (Bool)`: Indicates whether parental consent is required for the user
        - `etrainfo (dictionary)`: Dictionary that contains the user extrainfo fields
            - `national_id (str)`: National ID of the user
            - `arabic_name (str)`: User type of the user
            ...

        **Returns**

        - 200: Success, user found.
        - 400: Bad request, missing either email or username
        - 401: Unauthorized user to make the request.
        - 404: User not found
        """
        user_query = self.get_user_query(request)
        user = get_object_or_404(User, **user_query)
        admin_fields = getattr(settings, "ACCOUNT_VISIBILITY_CONFIGURATION", {}).get(
            "admin_fields", {}
        )
        serialized_user = NelpUserReadOnlySerializer(
            user, custom_fields=admin_fields, context={"request": request}
        )
        response_data = serialized_user.data

        return Response(response_data)


    def get_user_query(self, request, query_params=None):
        """
        Utility to prepare the user query
        """
        if not query_params:
            query_params = self.get_query_params(request)

        username = query_params.get("username", None)
        email = query_params.get("email", None)
        national_id = query_params.get("national_id", None)


        if not email and not username and not national_id:
            raise ValidationError(detail="Email or username or national_id needed")

        user_query = {}
        # if hasattr(self, "site") and self.site: Not tenant aware
        #     user_query["site"] = self.site
        if username:
            user_query["username"] = username
        elif email:
            user_query["email"] = email
        elif national_id:
            user_query["extrainfo__national_id"] = national_id

        return user_query
