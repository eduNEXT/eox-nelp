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
        renders just video card /eox-nelp/stats/tenant/?showVideos=true

        render multiple components
        /eox-nelp/stats/tenant/?showVideos=true&showCourses=true&showInstructors=true

    The available options are:
        showVideos
        showCourses
        showLearners
        showInstructors
        showProblems
    """

    context = {
        "showCourses": "false",
        "showVideos": "false",
        "showProblems": "false",
        "showLearners": "false",
        "showInstructors": "false",
    }
    context.update(request.GET.dict())

    return render_to_response("tenant_stats.html", context)
