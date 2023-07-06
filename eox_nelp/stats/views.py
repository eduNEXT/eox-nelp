"""Stats Views file.

Contains all the views for stats

classes:
    get_tenant_stats: function based view.
"""

from eox_nelp.templates_config import render_to_response


def get_tenant_stats(request):
    """
    Simple function based view that renders the StatsContainer essential component.
    By default this show nothing since this requires the specific query para to show the content.

    Examples:
        renders just video card /eox-nelp/stats/tenant/?show_videos=true

        render multiple components
        /eox-nelp/stats/tenant/?show_videos=true&show_courses=true&show_instructors=true

    The available options are:
        show_videos
        show_courses
        show_learners
        show_instructors
        show_problems
    """

    context = {
        "show_courses": "false",
        "show_videos": "false",
        "show_problems": "false",
        "show_learners": "false",
        "show_instructors": "false",
    }
    context.update(request.GET.dict())

    return render_to_response("tenant_stats.html", context)
