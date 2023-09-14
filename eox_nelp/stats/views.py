"""Stats Views file.

Contains all the views for stats

classes:
    get_tenant_stats: function based view.
"""
from eox_nelp.templates_config import render_to_response

STATS_QUERY_PARAMS = [
    "show_courses",
    "show_videos",
    "show_problems",
    "show_learners",
    "show_instructors",
    "show_certificates",
]


def get_tenant_stats(request):
    """
    Simple function based view that renders the StatsContainer essential component.
    By default this will show all the available stats.

    Examples:
        renders all available stats /eox-nelp/stats/tenant/

        filters out videos, courses and instructors
        /eox-nelp/stats/tenant/?show_videos=false&show_courses=false&show_instructors=false

    The available options are:

        |       name       | default |         Description         |

        |    show_videos   |   true  |    Show the videos stats    |

        |   show_courses   |   true  |    Show the courses stats   |

        |   show_learners  |   true  |    Show the learner stats   |

        | show_instructors |   true  |  Show the instructors stats |

        |  show_problems   |   true  |   Show the problems stats   |

        | show_certificates|   true  | Show the certificates stats |
    """
    context = {query_param: "true" for query_param in STATS_QUERY_PARAMS}
    context.update(request.GET.dict())

    return render_to_response("tenant_stats.html", context)
