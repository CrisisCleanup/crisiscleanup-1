# Local libraries.
import site_db

# TODO(Jeremy): Deprecate this once we move to server-side
# filter generation.
def SitesFromIds(comma_separated_ids, event):
  """Given a string of ids, like "1,2,3", returns corresponding Site objects.
  If comma_separated_ids is empty, returns all sites.
  """
  if not comma_separated_ids:
    q = Query(model_class = Site)
    q.filter("event =", event)
    return [site for site in q]
  else:
    try:
      ids = [int(id) for id in comma_separated_ids.split(',')]
    except:
      return None
    return [site for site in site_db.Site.get_by_id(ids)]
