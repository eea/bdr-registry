# Python script at /api/update_organisation_name
request = container.REQUEST

country_code = request.form['country_code']
obligation_code = request.form['obligation_folder_name']
account = request.form['account_uid']
org_name = request.form['organisation_name']

root = container.restrictedTraverse('/')
obligation = dict(root.objectItems()).get(obligation_code)
if obligation:
    country = dict(obligation.objectItems()).get(country_code)
    if country:
        collection = dict(country.objectItems()).get(account)
        if collection:
            collection.manage_changeCollection(title=org_name)
            updated = True

updated = False

return {"updated": updated}
