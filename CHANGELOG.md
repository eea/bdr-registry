Changelog
=========

1.2.dev0 - (unreleased)
-----------------------

1.1 - (2016-11-25)
-----------------------
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
