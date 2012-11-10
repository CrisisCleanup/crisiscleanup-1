# System libraries.
import csv

# Local libraries.
import base
import site_db
import site_util

class ExportHandler(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org, event):
    sites = site_util.SitesFromIds(self.request.get('id'), event)

    filename = 'work_sites.csv'
    self.response.headers['Content-Type'] = 'text/csv'
    self.response.headers['Content-Disposition'] = (
        'attachment; filename="work_sites.csv"')

    writer = csv.writer(self.response.out)
    writer.writerow(site_db.Site.CSV_FIELDS)

    for site in sites:
      writer.writerow(site.ToCsvLine())
