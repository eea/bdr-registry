import ldap


class LdapEditor(object):

    def __init__(self, server, bind_dn, bind_password):
        conn = ldap.initialize(server)
        conn.protocol_version = ldap.VERSION3
        conn.timeout = 5
        result = conn.simple_bind_s(bind_dn, bind_password)
        self.conn = conn


def create_ldap_editor():
    from django.conf import settings
    config = {
        'server': settings.LDAP_EDIT_SERVER,
        'bind_dn': settings.LDAP_EDIT_DN,
        'bind_password': settings.LDAP_EDIT_PASSWORD,
    }
    return LdapEditor(**config)
