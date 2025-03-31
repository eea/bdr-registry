import base64
import logging
import ldap
import hashlib
from .audit import log as audit_log

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def encrypt_password(password):
    password = password.encode("utf-8")
    return "{SHA}" + bytes.decode(base64.b64encode(hashlib.sha1(password).digest()))


class LdapEditor(object):

    encoding = "utf-8"
    users_dn = "ou=Business Reporters,o=EIONET,l=Europe"

    def __init__(self, server, bind_dn, bind_password):
        conn = ldap.initialize(server)
        conn.protocol_version = ldap.VERSION3
        conn.timeout = 5
        conn.simple_bind_s(bind_dn, bind_password)
        self.conn = conn

    def _account_dn(self, uid):
        return "uid=" + uid + "," + self.users_dn

    def search_account(self, uid):
        from django.conf import settings

        search_filter = f"(uid={uid})"
        result = self.conn.search_s(self.users_dn, ldap.SCOPE_SUBTREE, search_filter)
        return result

    def create_account(self, uid, org_name, country_name, password):
        name = "%s / %s" % (org_name, country_name)
        attrs = [
            ("uid", [str.encode(uid)]),
            ("cn", [str.encode(name)]),
            (
                "objectClass",
                [b"top", b"organizationalRole", b"simpleSecurityObject", b"uidObject"],
            ),
            ("userPassword", [str.encode(encrypt_password(password))]),
        ]

        try:
            log.debug("conn.add_s(%r, %r)", self._account_dn(uid), attrs)
            audit_log("Creatig LDAP account for uid=%s", uid)
            result = self.conn.add_s(self._account_dn(uid), attrs)

        except ldap.ALREADY_EXISTS:
            log.debug("Account uid=%s already exists.", uid)
            return False

        else:
            assert result == (ldap.RES_ADD, [], 2, [])
            log.info("Created account uid=%s.", uid)
            return True

    def reset_password(self, uid, password):
        attrs = [
            (
                ldap.MOD_REPLACE,
                "userPassword",
                [str.encode(encrypt_password(password))],
            ),
        ]
        log.debug("conn.modify_s(%r, %r)", self._account_dn(uid), attrs)
        audit_log("Resetting LDAP password for uid=%s", uid)
        result = self.conn.modify_s(self._account_dn(uid), attrs)
        assert result == (ldap.RES_MODIFY, [], 3, [])
        log.info("Password reset for uid=%s.", uid)

    def reset_password_assert_2(self, uid, password):
        attrs = [
            (
                ldap.MOD_REPLACE,
                "userPassword",
                [str.encode(encrypt_password(password))],
            ),
        ]
        log.debug("conn.modify_s(%r, %r)", self._account_dn(uid), attrs)
        audit_log("Resetting LDAP password for uid=%s", uid)
        result = self.conn.modify_s(self._account_dn(uid), attrs)
        assert result == (ldap.RES_MODIFY, [], 2, [])
        log.info("Password reset for uid=%s.", uid)


def create_ldap_editor():
    from django.conf import settings

    config = {
        "server": settings.LDAP_EDIT_SERVER,
        "bind_dn": settings.LDAP_EDIT_DN,
        "bind_password": settings.LDAP_EDIT_PASSWORD,
    }
    return LdapEditor(**config)
