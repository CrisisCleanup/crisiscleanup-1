
from organization import Organization

def get_global_admins():
    " Pluralised to indicate this is a list, but there is only one. "
    global_admins = Organization.gql('WHERE name = :1', 'Admin')
    return list(global_admins)


def get_event_admins(event):
    global_admins = get_global_admins()
    local_admins = Organization.gql(
        'WHERE incidents = :1 AND is_admin = True AND name != :2',
        event.key(), 'Admin'
    )
    return global_admins + list(local_admins)
