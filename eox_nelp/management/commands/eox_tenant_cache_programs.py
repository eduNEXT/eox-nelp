""""Management command to add program info to the cache using eox-tenant."""


import logging
import sys

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.cache import cache
from eox_tenant.models import Route
from eox_tenant.signals import _update_settings
from eox_tenant.tenant_wise.proxies import TenantSiteConfigProxy
from openedx.core.djangoapps.catalog.cache import SITE_PATHWAY_IDS_CACHE_KEY_TPL, SITE_PROGRAM_UUIDS_CACHE_KEY_TPL
from openedx.core.djangoapps.catalog.management.commands.cache_programs import Command as BaseCacheProgramCommand
from openedx.core.djangoapps.catalog.models import CatalogIntegration
from openedx.core.djangoapps.catalog.utils import create_catalog_api_client

logger = logging.getLogger(__name__)
User = get_user_model()  # pylint: disable=invalid-name


class Command(BaseCacheProgramCommand):
    """Management command used to cache program data.
    This command requests every available program from the discovery
    service, writing each to its own cache entry with an indefinite expiration.
    It is meant to be run on a scheduled basis and should be the only code
    updating these cache entries. Run:`./manage.py lms eox_tenant_cache_programs`
    """
    help = "Rebuild the LMS' cache of program data using eox-tenant."

    # lint-amnesty, pylint: disable=bad-option-value, unicode-format-string
    def handle(self, *args, **options):  # lint-amnesty, pylint: disable=too-many-statements
        failure = False
        logger.info('populate-multitenant-programs switch is ON')

        catalog_integration = CatalogIntegration.current()
        username = catalog_integration.service_username

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            logger.exception(
                f'Failed to create API client. Service user {username} does not exist.'
            )
            raise

        programs = {}
        pathways = {}
        courses = {}
        catalog_courses = {}
        programs_by_type = {}
        programs_by_type_slug = {}
        organizations = {}
        for route in Route.objects.all():
            domain = route.domain
            logger.info(f'Using eox-tenant route: {domain} for site.')
            _update_settings(domain)
            site = Site.objects.get_current()
            site.domain = domain
            site.configuration = TenantSiteConfigProxy()
            site_config = getattr(site, 'configuration', None)
            if site_config is None or not site_config.get_value('COURSE_CATALOG_API_URL'):
                logger.info(f'Skipping site {site.domain}. No configuration.')
                cache.set(SITE_PROGRAM_UUIDS_CACHE_KEY_TPL.format(domain=site.domain), [], None)
                cache.set(SITE_PATHWAY_IDS_CACHE_KEY_TPL.format(domain=site.domain), [], None)
                continue

            client = create_catalog_api_client(user, site=site)
            uuids, program_uuids_failed = self.get_site_program_uuids(client, site)
            new_programs, program_details_failed = self.fetch_program_details(client, uuids)
            new_pathways, pathways_failed = self.get_pathways(client, site)
            new_pathways, new_programs, pathway_processing_failed = self.process_pathways(
                site, new_pathways, new_programs
            )

            failure = any([
                program_uuids_failed,
                program_details_failed,
                pathways_failed,
                pathway_processing_failed,
            ])

            programs.update(new_programs)
            pathways.update(new_pathways)
            courses.update(self.get_courses(new_programs))
            catalog_courses.update(self.get_catalog_courses(new_programs))
            programs_by_type.update(self.get_programs_by_type(site, new_programs))
            programs_by_type_slug.update(self.get_programs_by_type_slug(site, new_programs))
            organizations.update(self.get_programs_by_organization(new_programs))

            logger.info('Caching UUIDs for {total} programs for site {site_name}.'.format(
                total=len(uuids),
                site_name=site.domain,
            ))
            cache.set(SITE_PROGRAM_UUIDS_CACHE_KEY_TPL.format(domain=site.domain), uuids, None)

            pathway_ids = list(new_pathways.keys())
            logger.info('Caching ids for {total} pathways for site {site_name}.'.format(
                total=len(pathway_ids),
                site_name=site.domain,
            ))
            cache.set(SITE_PATHWAY_IDS_CACHE_KEY_TPL.format(domain=site.domain), pathway_ids, None)

        logger.info(f'Caching details for {len(programs)} programs.')
        cache.set_many(programs, None)

        logger.info(f'Caching details for {len(pathways)} pathways.')
        cache.set_many(pathways, None)

        logger.info(f'Caching programs uuids for {len(courses)} courses.')
        cache.set_many(courses, None)

        logger.info(f'Caching programs uuids for {len(catalog_courses)} catalog courses.')
        cache.set_many(catalog_courses, None)

        logger.info(str(f'Caching program UUIDs by {len(programs_by_type)} program types.'))
        cache.set_many(programs_by_type, None)

        logger.info(str(f'Caching program UUIDs by {len(programs_by_type_slug)} program type slugs.'))
        cache.set_many(programs_by_type_slug, None)

        logger.info(f'Caching programs uuids for {len(organizations)} organizations')
        cache.set_many(organizations, None)

        if failure:
            sys.exit(1)
