"""
Course API Serializers.  Representing course catalog data
"""


from edx_django_utils import monitoring as monitoring_utils
import six.moves.urllib.error
import six.moves.urllib.parse
import six.moves.urllib.request
from django.urls import reverse
from rest_framework import serializers

from openedx.core.djangoapps.models.course_details import CourseDetails
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx.core.lib.api.fields import AbsoluteURLField
from bs4 import BeautifulSoup


class _MediaSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """
    Nested serializer to represent a media object.
    """

    def __init__(self, uri_attribute, *args, **kwargs):
        super(_MediaSerializer, self).__init__(*args, **kwargs)
        self.uri_attribute = uri_attribute

    uri = serializers.SerializerMethodField(source='*')

    def get_uri(self, course_overview):
        """
        Get the representation for the media resource's URI
        """
        return getattr(course_overview, self.uri_attribute)


class _AbsolutMediaSerializer(_MediaSerializer):  # pylint: disable=abstract-method
    """
    Nested serializer to represent a media object and its absolute path.
    """
    requires_context = True

    def __call__(self, serializer_field):
        self.context = serializer_field.context
        return super(self).__call__(serializer_field)

    uri_absolute = serializers.SerializerMethodField(source="*")

    def get_uri_absolute(self, course_overview):
        """
        Convert the media resource's URI to an absolute URI.
        """
        uri = getattr(course_overview, self.uri_attribute)

        if not uri:
            # Return empty string here, to keep the same
            # response type in case uri is empty as well.
            return ""

        cdn_applied_uri = course_overview.apply_cdn_to_url(uri)
        field = AbsoluteURLField()

        # In order to use the AbsoluteURLField to have the same
        # behaviour what ImageSerializer provides, we need to set
        # the request for the field
        field._context = {"request": self.context.get("request")}

        return field.to_representation(cdn_applied_uri)


class ImageSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """
    Collection of URLs pointing to images of various sizes.

    The URLs will be absolute URLs with the host set to the host of the current request. If the values to be
    serialized are already absolute URLs, they will be unchanged.
    """
    raw = AbsoluteURLField()
    small = AbsoluteURLField()
    large = AbsoluteURLField()


class _CourseApiMediaCollectionSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """
    Nested serializer to represent a collection of media objects
    """
    banner_image = _AbsolutMediaSerializer(source='*', uri_attribute='banner_image_url')
    course_image = _MediaSerializer(source='*', uri_attribute='course_image_url')
    course_video = _MediaSerializer(source='*', uri_attribute='course_video_url')
    image = ImageSerializer(source='image_urls')


class CourseSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """
    Serializer for Course objects providing minimal data about the course.
    Compare this with CourseDetailSerializer.
    """

    blocks_url = serializers.SerializerMethodField()
    effort = serializers.CharField()
    end = serializers.DateTimeField()
    enrollment_start = serializers.DateTimeField()
    enrollment_end = serializers.DateTimeField()
    id = serializers.CharField()  # pylint: disable=invalid-name
    media = _CourseApiMediaCollectionSerializer(source='*')
    name = serializers.CharField(source='display_name_with_default_escaped')
    number = serializers.CharField(source='display_number_with_default')
    org = serializers.CharField(source='display_org_with_default')
    short_description = serializers.CharField()
    start = serializers.DateTimeField()
    start_display = serializers.CharField()
    start_type = serializers.CharField()
    pacing = serializers.CharField()
    mobile_available = serializers.BooleanField()
    hidden = serializers.SerializerMethodField()
    invitation_only = serializers.BooleanField()

    # 'course_id' is a deprecated field, please use 'id' instead.
    course_id = serializers.CharField(source='id', read_only=True)

    def get_hidden(self, course_overview):
        """
        Get the representation for SerializerMethodField `hidden`
        Represents whether course is hidden in LMS
        """
        catalog_visibility = course_overview.catalog_visibility
        return catalog_visibility in ['about', 'none']

    def get_blocks_url(self, course_overview):
        """
        Get the representation for SerializerMethodField `blocks_url`
        """
        base_url = '?'.join([
            reverse('blocks_in_course'),
            six.moves.urllib.parse.urlencode({'course_id': course_overview.id}),
        ])
        return self.context['request'].build_absolute_uri(base_url)
    course_about_url = serializers.SerializerMethodField()
    def get_course_about_url(self, course_overview):
        """
        Get the representation for SerializerMethodField `course_about_url`
        """
        base_url = '/courses/' + str(course_overview.id) + '/about'
        return self.context['request'].build_absolute_uri(base_url)

class CourseDetailSerializer(CourseSerializer):  # pylint: disable=abstract-method
    """
    Serializer for Course objects providing additional details about the
    course.

    This serializer makes additional database accesses (to the modulestore) and
    returns more data (including 'overview' text). Therefore, for performance
    and bandwidth reasons, it is expected that this serializer is used only
    when serializing a single course, and not for serializing a list of
    courses.
    """

    overview = serializers.SerializerMethodField()

    def get_overview(self, course_overview):
        """
        Get the representation for SerializerMethodField `overview`
        """
        # Note: This makes a call to the modulestore, unlike the other
        # fields from CourseSerializer, which get their data
        # from the CourseOverview object in SQL.
        self.raw_overview = CourseDetails.fetch_about_attribute(course_overview.id, 'overview')
        return self.raw_overview
    overview_object = serializers.SerializerMethodField()
    def get_overview_object(self, course_overview):
        """Get an object that parse the html information and extract
        `about_description`,`staff`, `prereqs` and `faqs` of course_overview.
         https://edx.readthedocs.io/projects/edx-open-learning-xml/en/latest/about/overview.html
        """

        html_str = self.raw_overview
        def decompose_str_p(p_tag):
            """Join all str in a paragraph tag in one string."""
            generator = p_tag.strings
            string_list = [string for string in generator]
            return ''.join(string_list)

        def get_titles_and_paragraphs(tag, title_tag_atr, p_tag_atr, title_name="titles", p_name="paragraphs"):
            """Get an object represetantion after searching by desired titles and paragraphs tags"""
            try:
                return {
                title_name:  [title.string for title in tag.find_all(title_tag_atr) ],
                p_name: [decompose_str_p(p_tag) for p_tag in tag.find_all(p_tag_atr) ]
                }

            except:
                return {
                    title_name: [],
                    p_name: [],
                }

        def get_source_images(tag, image_name="image_url"):
            try:
                return {
                image_name: [self.context['request'].build_absolute_uri(title.get('src')) for title in tag.find_all('img') ]
                }
            except:
                return {
                    image_name: []
                }
        soup = BeautifulSoup(html_str, 'html.parser')

        about_tag = soup.find_all("section", class_="about")
        abouts = [get_titles_and_paragraphs(about, "h2","p", title_name="titles", p_name="paragraphs") for about in about_tag]

        prereq_tag = soup.find_all("section", class_="prerequisites")
        prereqs = [get_titles_and_paragraphs(prereq, "h2","p", title_name="titles", p_name="paragraphs") for prereq in prereq_tag]

        staff_tag = soup.find_all("section", class_="course-staff")
        staff = {}
        if staff_tag:
            staff["titles"] = [h2.contents for h2 in staff_tag[0].find_all("h2") ],

        teachers =  soup.find_all("article", class_="teacher")
        teacher_list = [{**get_titles_and_paragraphs(teacher, "h3","p", title_name="name", p_name="bio"),
                         **get_source_images(teacher) } for teacher in teachers]
        staff ['teachers'] = teacher_list

        faq_responses = soup.find_all("article", class_="response")
        responses = [get_titles_and_paragraphs(response, "h3","p", title_name="h3_questions", p_name="p_answers") for response in faq_responses]

        return {
            "about_description": abouts,
            "staff": staff,
            "prereqs": prereqs,
            "faq": responses,
        }



class CourseKeySerializer(serializers.BaseSerializer):  # pylint:disable=abstract-method
    """
    Serializer that takes a CourseKey and serializes it to a string course_id.
    """

    @monitoring_utils.function_trace('course_key_serializer_to_representation')
    def to_representation(self, instance):
        # The function trace should be counting calls to this function, but I
        # couldn't find it when I looked in any of the NR transaction traces,
        # so I'm manually counting them using a custom metric:
        monitoring_utils.increment('course_key_serializer_to_representation_call_count')

        return str(instance)
