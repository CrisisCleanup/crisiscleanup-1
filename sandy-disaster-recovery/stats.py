
import os
import datetime
import logging

from google.appengine.ext import db
from google.appengine.ext import deferred
from google.appengine.api import app_identity
import cloudstorage

import jinja2

import base
from site_db import Site, STATUSES
from event_db import Event
from db_utils import BatchingQuery
from cron_utils import AbstractCronHandler


# constants

SITES_BATCH_SIZE = 100

APP_ID = app_identity.get_application_id()
BUCKET_NAME = '/' + APP_ID


# jinja

csv_jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        os.path.join(
            os.path.dirname(__file__),
            'templates',
            'csv',
        )
    )

)
common_html_jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        os.path.join(
            os.path.dirname(__file__),
            'templates',
            'html',
            'common'
        )
    )
)


# functions

def crunch_incident_statistics(event):
    " To a dict. "

    # setup counters
    claimed_status_counts = {status: 0 for status in STATUSES}
    unclaimed_status_counts = {status: 0 for status in STATUSES}
    claimed_open_count = 0
    claimed_closed_count = 0
    unclaimed_open_count = 0
    unclaimed_closed_count = 0
    work_type_open_counts = {}
    work_type_closed_counts = {}
    county_open_counts = {}
    county_closed_counts = {}

    orgs = event.organizations
    org_claimed_counts = {org.key().id(): 0 for org in orgs}
    org_open_counts = {org.key().id(): 0 for org in orgs}
    org_closed_counts = {org.key().id(): 0 for org in orgs}
    org_reported_counts = {org.key().id(): 0 for org in orgs}

    now = datetime.datetime.utcnow()
    total_open_request_age = 0 # sec

    # create and batch query
    sites_query = db.Query(
        Site,
        projection=[
            'claimed_by',
            'reported_by',
            'request_date',
            'status',
            'work_type',
            'county',
            'state',
        ]
    ).filter('event', event.key())
    batched_sites = BatchingQuery(sites_query, SITES_BATCH_SIZE)

    # iterate to crunch
    for site in batched_sites:
        claiming_org = site.claimed_by
        claimed = bool(claiming_org)
        reporting_org = site.reported_by
        status = site.status
        work_type = site.work_type.strip() if site.work_type else None
        if not work_type:
            work_type = u'[Blank]'
        county = site.county_and_state  # use county + state in place of county
        open = status.startswith('Open')
        closed = status.startswith('Closed')

        if open:
            work_type_open_counts[work_type] = \
                work_type_open_counts.get(work_type, 0) + 1
            county_open_counts[county] = \
                county_open_counts.get(county, 0) + 1
            if site.request_date:
                total_open_request_age += (now - site.request_date).total_seconds()
        if closed:
            work_type_closed_counts[work_type] = \
                work_type_closed_counts.get(work_type, 0) + 1
            county_closed_counts[county] = \
                county_closed_counts.get(county, 0) + 1

        if claimed:
            claimed_status_counts[status] = \
                claimed_status_counts.get(status, 0) + 1
            org_claimed_counts[claiming_org.key().id()] += 1
            if open:
                org_open_counts[claiming_org.key().id()] += 1
                claimed_open_count += 1
            if closed:
                org_closed_counts[claiming_org.key().id()] += 1
                claimed_closed_count +=1
        else:  # unclaimed
            unclaimed_status_counts[status] = \
                unclaimed_status_counts.get(status, 0) + 1
            if open:
                unclaimed_open_count += 1
            if closed:
                unclaimed_closed_count += 1

        if reporting_org:
            org_reported_counts[reporting_org.key().id()] += 1

    # filter unverified and inactive orgs that have not participated
    def has_participated(org):
        org_id = org.key().id()
        return (
            org_claimed_counts[org_id] or
            org_open_counts[org_id] or
            org_closed_counts[org_id] or
            org_reported_counts[org_id]
        )
    orgs = filter(
        lambda org: (org.org_verified and org.is_active) or has_participated(org),
        orgs
    )

    # compute totals
    total_status_counts = {
        status: claimed_status_counts.get(status, 0) + \
                unclaimed_status_counts.get(status, 0)
        for status in STATUSES
    }
    claimed_status_total = sum(claimed_status_counts.values())
    unclaimed_status_total = sum(unclaimed_status_counts.values())
    total_open_total = claimed_open_count + unclaimed_open_count
    total_closed_total = claimed_closed_count + unclaimed_closed_count
    total_status_total = sum(total_status_counts.values())

    org_claimed_total = sum(org_claimed_counts.values())
    org_open_total = sum(org_open_counts.values())
    org_closed_total = sum(org_closed_counts.values())
    org_reported_total = sum(org_reported_counts.values())

    work_types = set(work_type_open_counts.keys() + work_type_closed_counts.keys())
    work_type_totals = {
        work_type: work_type_open_counts.get(work_type, 0) + \
                   work_type_closed_counts.get(work_type, 0)
        for work_type in work_types
    }

    counties = set(county_open_counts.keys() + county_closed_counts.keys())
    county_totals = {
        county: county_open_counts.get(county, 0) + \
                county_closed_counts.get(county, 0)
        for county in counties
    }

    # compute averages
    average_days_waiting_for_open_work_orders = (
        float(total_open_request_age) / total_open_total / 60 / 60 / 24
        if total_open_total else 0
    )

    return {
        'timestamp': now,
        'event_key': event.key(),
        'event': event,
        'orgs': orgs,
        'statuses': STATUSES,
        'work_types': work_types,
        'counties': counties,

        'claimed_status_counts': claimed_status_counts,
        'unclaimed_status_counts': unclaimed_status_counts,
        'total_status_counts': total_status_counts,
        'claimed_open_count': claimed_open_count,
        'claimed_closed_count': claimed_closed_count,
        'unclaimed_open_count': unclaimed_open_count,
        'unclaimed_closed_count': unclaimed_closed_count,
        'claimed_status_total': claimed_status_total,
        'unclaimed_status_total': unclaimed_status_total,
        'total_open_total': total_open_total,
        'total_closed_total': total_closed_total,
        'total_status_total': total_status_total,

        'org_claimed_counts': org_claimed_counts,
        'org_open_counts': org_open_counts,
        'org_closed_counts': org_closed_counts,
        'org_reported_counts': org_reported_counts,
        'org_claimed_total': org_claimed_total,
        'org_open_total': org_open_total,
        'org_closed_total': org_closed_total,
        'org_reported_total': org_reported_total,

        'work_type_open_counts': work_type_open_counts,
        'work_type_closed_counts': work_type_closed_counts,
        'work_type_totals': work_type_totals,

        'county_open_counts': county_open_counts,
        'county_closed_counts': county_closed_counts,
        'county_totals': county_totals,

        'average_days_waiting_for_open_work_orders': average_days_waiting_for_open_work_orders,
    }


def incident_statistics_csv(incident_statistics_dict):
    stats_csv_template = csv_jinja_environment.get_template("incident_statistics.csv")
    return stats_csv_template.render(incident_statistics_dict)


def incident_statistics_html(incident_statistics_dict):
    stats_html_template = common_html_jinja_environment.get_template('_incident_statistics_tables.html')
    return stats_html_template.render(incident_statistics_dict)


def incident_statistics_csv_filename(event):
    return u"%s.stats.csv" % event.short_name


def incident_statistics_html_filename(event):
    return u"%s.stats.html" % event.short_name


class CrunchAllStatisticsHandler(AbstractCronHandler):

    @classmethod
    def _crunch_and_save(cls, event_key):
        event = Event.get(event_key)

        # crunch
        stats_d = crunch_incident_statistics(event)
        csv_content = incident_statistics_csv(stats_d)
        html_content = incident_statistics_html(stats_d)

        # save csv & html
        csv_gcs_fd = cloudstorage.open(
            BUCKET_NAME + '/' + incident_statistics_csv_filename(event),
            'w',
            content_type='text/csv'
        )
        csv_gcs_fd.write(csv_content.encode('utf-8'))
        csv_gcs_fd.close()

        html_gcs_fd = cloudstorage.open(
            BUCKET_NAME + '/' + incident_statistics_html_filename(event),
            'w',
            content_type='text/html'
        )
        html_gcs_fd.write(html_content.encode('utf-8'))
        html_gcs_fd.close()

    def get(self):
        # defer crunch and save for each event
        for event in Event.all():
            if event.logged_in_to_recently:
                logging.info(u"Crunching statistics for %s" % event.short_name)
                deferred.defer(
                    self._crunch_and_save,
                    str(event.key()),
                    _queue='crunch-statistics',
                )
            else:
                logging.info(u"Crunching statistics: skipping %s" % event.short_name)


class IncidentStatisticsHandler(base.FrontEndAuthenticatedHandler):

    template_name = "incident_statistics.html"

    def AuthenticatedGet(self, org, event):
        html_filename = BUCKET_NAME + '/' + incident_statistics_html_filename(event)

        try:
            cloudstorage.stat(html_filename)
            file_exists = True
        except cloudstorage.errors.NotFoundError:
            file_exists = False

        if file_exists:
            tables_html = cloudstorage.open(html_filename).read().decode('utf-8')
            csv_filename = incident_statistics_csv_filename(event)
        else:
            tables_html = u"<p>Statistics not yet generated for this incident.</p>"
            csv_filename = None

        return self.render(
            incident_statistics_tables=tables_html,
            csv_filename=csv_filename
        )


class IncidentStatisticsCSVHandler(base.AuthenticatedHandler):

    def AuthenticatedGet(self, org, event):
        self.response.headers['Content-Type'] = 'test/csv'
        self.response.out.write(incident_statistics_csv(event))
