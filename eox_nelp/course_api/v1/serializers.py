"""
Course API Serializers.  Representing course catalog data
"""
from bs4 import BeautifulSoup
from django.urls import NoReverseMatch, reverse
from rest_framework import serializers

from eox_nelp.edxapp_wrapper.course_api import CourseDetailSerializer


class NelpCourseDetailSerializer(CourseDetailSerializer):  # pylint: disable=abstract-method
    """
    Serializer for Course objects providing additional details about the
    course.

    This serializer makes additional database accesses (to the modulestore) and
    returns more data (including 'overview' text). Therefore, for performance
    and bandwidth reasons, it is expected that this serializer is used only
    when serializing a single course, and not for serializing a list of
    courses.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.raw_overview = ""

    course_about_url = serializers.SerializerMethodField()

    def get_course_about_url(self, course_overview):
        """
        Get the representation for SerializerMethodField `course_about_url`
        """
        try:
            about_course_path = reverse("about_course", args=[course_overview.id])
        except NoReverseMatch:
            about_course_path = f"/courses/{course_overview.id}/about"

        return self.context["request"].build_absolute_uri(about_course_path)

    overview = serializers.SerializerMethodField()

    def get_overview(self, course_overview):
        """
        Get the representation for SerializerMethodField `overview`
        """
        # Note: This makes a call to the modulestore, unlike the other
        # fields from CourseSerializer, which get their data
        # from the CourseOverview object in SQL.
        raw_overview = super().get_overview(course_overview)
        self.raw_overview = "" if raw_overview is None else raw_overview

        return self.raw_overview

    overview_object = serializers.SerializerMethodField()

    def get_overview_object(self, course_overview):  # pylint: disable=unused-argument
        """Get an object that parse the html information and extract
        `about_description`,`staff`, `prereqs` and `faqs` of course_overview.
         https://edx.readthedocs.io/projects/edx-open-learning-xml/en/latest/about/overview.html
        """

        def decompose_str_p(p_tag):
            """Join all str in a paragraph tag in one string."""
            return "".join(p_tag.strings)

        def get_titles_and_paragraphs(tag, title_tag_name, p_tag_name, title_name="titles", p_name="paragraphs"):
            """Get an object represetantion after searching by desired titles and paragraphs tags by tag name."""
            return {
                title_name: [title.string for title in tag.find_all(title_tag_name) if title],
                p_name: [decompose_str_p(p_tag) for p_tag in tag.find_all(p_tag_name) if p_tag],
            }

        def get_source_images(tag):
            """Get src images from tag"""
            return {
                "image_url": [
                    self.context["request"].build_absolute_uri(title.get("src"))
                    for title in tag.find_all("img") if title.get("src")
                ]
            }

        soup = BeautifulSoup(self.raw_overview, "html.parser")

        abouts = [
            get_titles_and_paragraphs(about, "h2", "p", title_name="titles", p_name="paragraphs")
            for about in soup.find_all("section", class_="about")
        ]

        prereqs = [
            get_titles_and_paragraphs(prereq, "h2", "p", title_name="titles", p_name="paragraphs")
            for prereq in soup.find_all("section", class_="prerequisites")
        ]

        staff_tags = soup.find_all("section", class_="course-staff")
        staff = {}
        if staff_tags:
            staff["titles"] = ([h2.contents for h2 in staff_tags[0].find_all("h2")],)
        staff["teachers"] = [
            {
                **get_titles_and_paragraphs(teacher, "h3", "p", title_name="name", p_name="bio"),
                **get_source_images(teacher),
            }
            for teacher in soup.find_all("article", class_="teacher")
        ]

        responses = [
            get_titles_and_paragraphs(response, "h3", "p", title_name="h3_questions", p_name="p_answers")
            for response in soup.find_all("article", class_="response")
        ]

        return {"about_description": abouts, "staff": staff, "prereqs": prereqs, "faq": responses}
