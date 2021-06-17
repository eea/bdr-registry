# Python script at /api/update_organisation_name
request = container.REQUEST

updated = False
COUNTRY_TO_FOLDER = {"uk": "gb", "el": "gr"}
country_code = request.form["country_code"]
country_folder = COUNTRY_TO_FOLDER.get(country_code, country_code)
obligation_code = request.form["obligation_folder_name"]
account = request.form["account_uid"]
org_name = request.form["organisation_name"]
if isinstance(org_name, unicode):
    org_name = org_name.encode("utf-8")

oldcompany_account = request.form.get("oldcompany_account")
if oldcompany_account:
    account = oldcompany_account

search_path = str("/".join([obligation_code, country_folder, account]))
root = container.restrictedTraverse("/")
collection = root.restrictedTraverse(search_path, None)

if collection:
    if collection.title != org_name:
        collection.manage_changeCollection(title=org_name)
        updated = True

return {"updated": updated}
