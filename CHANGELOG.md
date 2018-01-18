Changelog
=========

1.3.9 - (2018-01-18)
--------------------
* Add management command to load companies directly from portal
  [dianaboiangiu]

1.3.8 - (2018-01-05)
--------------------
* Bug fix: fixed form rendering and string-bytes bugs
  [dianaboiangiu]

1.3.7 - (2018-01-03)
--------------------
* Bug fix: fixed python3 string-unicode bugs
  [dianaboiangiu]

1.3.6 - (2018-01-03)
--------------------
* Bug fix: fixed incorrect paths
  [nico4]

1.3.5 - (2017-12-12)
--------------------
* Bug fix: downgraded post-office package
  [dianaboiangiu]

1.3.4 - (2017-12-12)
--------------------
* Bug fix: convert nr_of_sorting_cols arg to int before comparison to int
  [dianaboiangiu]

1.3.3 - (2017-08-08)
--------------------
* Task: mitigate bot auto registration:
  - added honeypot to company self register
  [andreadima refs #87121]
  - added company batch delete support
  [andreadima refs #87109]

1.3.2 - (2017-06-28)
-----------------------
* BDR registry integration of invitations and reminders:
  middleware and email sending
  - added API method to export all persons in JSON format
  - added country_name for CompaniesJsonExport since only the
    country code did not suffice
  [chiridra refs #84119]

1.3.1 - (2017-04-03)
-----------------------
* Bug: reset password for company
  - use strip on person's email
  [chiridra refs #83867]

1.2 - (2017-01-17)
------------------
* Task: use logspout cu send logs to graylog
  - bumped factory-boy to 2.8.1
  - added extra parameters to gunicorn to route access/error log
    to stdout/stderr
  [chiridra refs #80762]

1.1 - (2016-11-25)
------------------
* Feature: Link to BDR-registry and back to the report questionnaire:
  - Since Django 1.7 select_for_update() requires a transaction:
    fixed generate_account_id accordingly.
  - defined 'home' as TemplateView and implemented 'get_user_company_details'
    method to retrieve info about current user's company (if the case)
  - moved 'has_reporting_folder' from view to model because we need to
    be able to call it from other views
  - added docs
  [chiridra refs #69698]

* Task: Docker deployment of BDR-Test
  - Used django-getenv to load some settings from env
  - No need to load localsettings from env (configure.py)
  [chiridra refs #78711]

* Task: Docker deployment of BDR-Test
  - use utf8 character set and utf8_general_ci collation when creating
    registry database
  [chiridra refs #78711]

1.0 - (2014-06-02)
------------------
* Initial release
  [nituacor]
