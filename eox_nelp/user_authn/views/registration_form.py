"""Registration form module for  nelp business case"
classes:
    NelpRegistrationFormFactory: Form factory that add extended_profile_fields feature.

"""
from django.utils.translation import gettext_lazy as _

from eox_nelp.edxapp_wrapper.site_configuration import configuration_helpers
from eox_nelp.edxapp_wrapper.user_api import accounts
from eox_nelp.edxapp_wrapper.user_authn import RegistrationFormFactory


class NelpRegistrationFormFactory(RegistrationFormFactory):
    """This class will extend the registration form factory of openedx with extra fields
    based on the tenant setting "extended_profile_fields", therefore the new values will be
    settable from the register form in /register, from /account/settings and finally from
    SAML IDP response.

    Configuration example, add the following in your tenant config:

        extended_profile_fields = [
            "hobby",
            "sport",
            "movie"
        ]

        # if you add this in general setting the default values will be deleted
        REGISTRATION_EXTRA_FIELDS = {
            'hobby': 'required',
            'sport': 'required',
            'movie': 'optional'
        }

        # if you want to add specific options to the  new fields

        EXTRA_FIELD_OPTIONS = {
            'sport': ['soccer', 'football', 'tennis'],
            'movie': ['Harry Potter', 'Karate kid']
        }

        # if you want to add translations

        extended_profile_fields_translations = {
            "ar": {
                'hobby': 'هواية',
            },
            "es": {
                'sport': 'Deporte',
                'movie': 'Pelicula'
            }
        }
    """

    def get_registration_form(self, request):
        """This method add the `extended_profile_fields` before the base-normal method is executed.
        Also translations keep working and the extended_profile_fields are appended at the end of the fields order.
        """
        extended_profile_fields = configuration_helpers.get_value('extended_profile_fields', [])
        extended_profile_fields_translations = configuration_helpers.get_value(
            'extended_profile_fields_translations',
            {},
        )
        translations = extended_profile_fields_translations.get(request.LANGUAGE_CODE, {})
        extended_profile_fields = list(set(extended_profile_fields) - set(self.EXTRA_FIELDS))

        for field_name in extended_profile_fields:
            setattr(
                NelpRegistrationFormFactory,
                f'_add_{field_name}_field',
                self._generate_handler(field_name, translations.get(field_name, field_name)),
            )
            # Set attributes in accounts since those fields are required by
            # "add_field_with_configurable_select_option" method.
            setattr(
                accounts,
                f'REQUIRED_FIELD_{field_name.upper()}_SELECT_MSG',
                f"{_('Select your')} {translations.get(field_name, field_name)}",
            )
            setattr(
                accounts,
                f'REQUIRED_FIELD_{field_name.upper()}_TEXT_MSG',
                f"{_('Enter your')} {translations.get(field_name, field_name)}",
            )

            handler = getattr(self, f"_add_{field_name}_field")
            self.field_handlers[field_name] = handler

        self.field_order = self.field_order + sorted(extended_profile_fields)

        return super().get_registration_form(request)

    def _generate_handler(self, field, label):
        """Every field will require a handler method, check the logic here
        https://github.com/eduNEXT/edunext-platform/blob/ednx-release/mango.master.nelp/
        openedx/core/djangoapps/user_authn/views/registration_form.py#L360,
        this method generates a specific handler for each new field with its specific label.

        Args:
            field: String
            label: String
        Returns:
            func: Handler method
        """
        label = label.capitalize()

        def handler(form_instance, form_desc, required=True):
            """Wrapper of https://github.com/eduNEXT/edunext-platform/blob/ednx-release/
            mango.master.nelp/openedx/core/djangoapps/user_authn/views/registration_form.py#L657
            """
            # pylint: disable=protected-access
            form_instance._add_field_with_configurable_select_options(field, label, form_desc, required=required)
        return handler
