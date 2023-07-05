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
        by default the view render all componets: /eox-nelp/stats/tenant/

        filter components: eg dont show videos and courses.
        /eox-nelp/stats/tenant/?videos=false&courses=false

    The available options are:
        hideVideos
        hideCourses
        hideLearners
        hideInstructors
        hideProblems
    """

    context = {
        "hideCourses": "false",
        "hideVideos": "false",
        "hideProblems": "false",
        "hideLearners": "false",
        "hideInstructors": "false",
    }
    context.update(request.GET.dict())

    return render_to_response("tenant_stats.html", context)
