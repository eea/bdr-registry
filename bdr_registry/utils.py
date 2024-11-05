import json
import logging
import requests

from django.conf import settings
from django.contrib import messages

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def create_reporting_folder(company, request=None, *args, **kwargs):
    if not (settings.BDR_API_URL and settings.BDR_API_AUTH):
        logging.error("BDR_API_URL and BDR_API_AUTH not configured")
        if request:
            messages.error(
                request, "BDR_API_URL and BDR_API_AUTH not configured" % resp
            )
        return
    url = settings.BDR_API_URL + "/create_organisation_folder"
    form = {
        "country_code": company.country.code,
        "obligation_folder_name": company.obligation.reportek_slug,
        "account_uid": company.account.uid,
        "organisation_name": company.name,
    }
    resp = requests.post(url, data=form, auth=settings.BDR_API_AUTH)

    if resp.status_code != 200:
        logging.error("BDR API request failed: %s" % resp)
        if request:
            messages.error(request, "BDR API request failed: %s" % resp)
    elif "unauthorized" in bytes.decode(resp.content.lower()):
        logging.error("BDR API request failed: %s" % resp)
        if request:
            messages.error(request, "BDR API request failed: Unauthorized")
    else:
        rv = resp.json()
        success = rv["success"]
        if success:
            if rv["created"]:
                logging.info("Created: %s" % rv["path"])
                if request:
                    messages.success(request, "Created: %s" % rv["path"])
            else:
                logging.warning("Existing: %s" % rv["path"])
                if request:
                    messages.warning(request, "Existing: %s" % rv["path"])
        else:
            logging.error("Error: %s" % rv["error"])
            if request:
                messages.error(request, "Error: %s" % rv["error"])


def set_role_for_account(company, account_uid, action):
    if not (settings.BDR_API_URL and settings.BDR_API_AUTH):
        logging.error("BDR_API_URL and BDR_API_AUTH not configured")
        return

    errors = []
    url = settings.BDR_API_URL + "/manage_ownership"
    form = {
        "uid": account_uid,
        "obl_folder": company.obligation.reportek_slug,
        "country": company.country.code,
        "c_folder": company.account.uid,
        "action": action,
    }
    headers = {"Content-type": "application/json"}
    resp = requests.post(
        url,
        data=json.dumps(form),
        auth=settings.BDR_API_AUTH,
        headers=headers
    )
    if resp.status_code != 200:
        logging.error("BDR API request failed: %r", resp)
        errors.append(account_uid)
        return
    rv = resp.json()

    if rv["errors"]:
        msg = "%s, on person account %s role setting: %s" % (
            company.account.uid,
            account_uid,
            rv["errors"],
        )
        logging.error(msg)
    else:
        msg = "{} role for uid={} on folder {}".format(
            action, account_uid, company.account.uid
        )
        logging.info(msg)
    if errors:
        msg = "%d errors: %s" % (len(errors), ", ".join(errors))
        logging.error(msg)
