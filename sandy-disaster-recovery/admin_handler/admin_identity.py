
from organization import Organization

def get_global_admins():
    " Pluralised to indicate this is a list, but there is only one. "
    global_admins = Organization.gql('WHERE name = :1', 'Admin')
    return list(global_admins)


def get_local_admins(event):
    return list(Organization.gql(
        'WHERE incidents = :1 AND is_admin = True AND name != :2',
        event.key(), 'Admin'
    ))


def get_event_admins(event):
    " Global and local admins. "
    global_admins = get_global_admins()
    local_admins = get_local_admins(event)
    return global_admins + local_admins
