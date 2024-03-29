"""CourseCreators admin file.
Contains all the nelped admin models for course_creators.
classes:
    NelpCourseCreatorAdmin: EoxNelp CourseCreators admin class.
"""
from eox_nelp.admin.register_admin_model import register_admin_model as register
from eox_nelp.edxapp_wrapper.course_creators import CourseCreator, CourseCreatorAdmin


class NelpCourseCreatorAdmin(CourseCreatorAdmin):
    """Nelp CourseCreatorAdmin class.
    This adds searching fields and shows the organization name instead of the organization id.
    """
    # pylint: disable=unused-argument
    raw_id_fields = ['user']
    readonly_fields = ['state_changed']
    # Controls the order on the edit form (without this, read-only fields appear at the end).
    fieldsets = ()
    add_fieldsets = (
        (None, {
            'fields': ['username', 'state', 'state_changed', 'note', 'all_organizations', 'organizations']
        }),
    )

    def has_add_permission(self, request):
        """Give add permission for everyone"""
        return True

    def has_delete_permission(self, request, obj=None):
        """Give delete permission for everyone"""
        return True


register(CourseCreator, NelpCourseCreatorAdmin)
