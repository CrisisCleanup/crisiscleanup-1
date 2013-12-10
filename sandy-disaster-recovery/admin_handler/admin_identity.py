
from organization import Organization

def get_event_admins(event):
    super_admins = Organization.gql('WHERE name = :1', 'Admin')
    local_admins = Organization.gql(
        'WHERE incidents = :1 AND is_admin = True AND name != :2',
        event.key(), 'Admin'
    )
    return list(super_admins) + list(local_admins)
