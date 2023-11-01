"""
CMS API v1 Nelp Version permissions
"""
from rest_framework.permissions import IsAuthenticated

from eox_nelp.edxapp_wrapper.student import roles


class NelpCourseRunPermission(IsAuthenticated):
    """
    Class to define Course Run Permissions.
    This permission is based on the premise that the get, list, update forms
    are already verified by the following methods.
    https://github.com/eduNEXT/edunext-platform/blob/ednx-release/mango.master.nelp/common/djangoapps/student/auth.py#L128
    https://github.com/eduNEXT/edunext-platform/blob/ednx-release/mango.master.nelp/common/djangoapps/student/auth.py#L75
    So this permission is always True except for create form.
    For the POST method there is some extra logic for the management.
    Only Global staff(admin_user) or OrgInstructorRole for the suggested org of the data could create.

    """

    def has_permission(self, request, view):
        """
        Define custom permission of Nelp case.
        """
        if request.method == "POST":
            org = request.data.get("org", None)
            return bool(
                roles.GlobalStaff().has_user(request.user) or roles.OrgInstructorRole(org=org).has_user(request.user)
            )

        return super().has_permission(request, view)
