# System libraries
from google.appengine.ext.db import Query
# Local libraries.
import site_db

# TODO(Jeremy): Deprecate this once we move to server-side
# filter generation.
def SitesFromIds(comma_separated_ids, event):
  """Given a string of ids, like "1,2,3", returns corresponding Site objects.
  If comma_separated_ids is empty, returns all sites.
  """
  if not comma_separated_ids:
    return [site[0] for site in site_db.GetAllCached(event, "all")]
  else:
    try:
      ids = [int(id) for id in comma_separated_ids.split(',')]
    except:
      return None
    return [site[0] for site in site_db.GetAllCached(event, "all", ids)]
