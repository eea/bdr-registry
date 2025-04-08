Changelog
=========

1.9.2 - (2025-04-08)
--------------------
* Upgrade eea.frame package
  [dianaboiangiu]

1.9.1 - (2025-04-02)
--------------------
* Upgrade eea.frame package
  [dianaboiangiu]

1.9.0 - (2025-03-31)
--------------------
* Upgrade packages to the latest version
  [dianaboiangiu]

1.8.11 - (2025-02-11)
---------------------
* Upgrade django-simple-captcha package
  [dianaboiangiu]

1.8.10 - (2025-01-22)
---------------------
* Add method to check if user exists in LDAP
  [dianaboiangiu]

1.8.9 - (2024-11-05)
--------------------
* Add script for checking HDV accounts' roles
* Fix set_role call on enable/disable accounts
  [dianaboiangiu]

1.8.8 - (2023-06-20)
--------------------
* Block HDV/HDV resim editing from env
* Fix docker image
  [dianboiangiu]

1.8.7 - (2023-06-19)
--------------------
* Retry docker builder
  [dianaboiangiu]

1.8.6 - (2023-06-16)
--------------------
* Retry docker build
  [dianaboiangiu]

1.8.5 - (2023-06-16)
--------------------
* Fix password functionality
  [dianaboiangiu]

1.8.4 - (2023-06-14)
--------------------
* Add dropdown for filtering by obligation on export
  [dianaboiangiu]

1.8.3 - (2023-06-07)
--------------------
* Stop migrations auto run in entrypoint
  [dianaboiangiu]

1.8.2 - (2023-06-02)
--------------------
* Fixes after switching to multiple companies/persons related to one account
  [dianaboiangiu]

1.8.1 - (2023-06-01)
--------------------
* Modify account companies/persons for relation count change
  [dianaboiangiu]

1.8.0 - (2023-06-01)
--------------------
* Add new obligation for HDV resimulation
  [dianaboiangiu]

1.7.5 - (2021-07-12)
--------------------
* Fix SMTPServerDisconnected
  [dianaboiangiu]

1.7.4 - (2021-07-09)
--------------------
* Set priority back on post office
  [dianaboiangiu]

1.7.3 - (2021-07-08)
--------------------
* Fix SMTPServerDisconnected
  [dianaboiangiu]

1.7.2 - (2021-07-08)
--------------------
* Fix SMTPServerDisconnected
  [dianaboiangiu]

1.7.1 - (2021-07-07)
--------------------
* Fix company delete
  [dianaboiangiu]

1.7.0 - (2021-06-18)
--------------------
* Upgrade python 3.8
* Upgrade to Django 3.2
* Upgrade all packages
* Add black and flake8 for code formatting
  [dianaboiangiu]

1.6.8 - (2021-05-21)
--------------------
* Update packages
  [dianaboiangiu]

1.6.7 - (2021-05-05)
--------------------
* Update packages
  [dianaboiangiu]

1.6.6 - (2021-03-26)
--------------------
* Change text for excel companies action
  [dianaboiangiu]

1.6.5 - (2021-03-25)
--------------------
* Add persons to excel companies download
  [dianaboiangiu]

1.6.4 - (2020-08-27)
--------------------
* Translate non-ASCII characters from account uid
  [dianaboiangiu]

1.6.3 - (2020-08-26)
--------------------
* Use zope login/logout
  [dianaboiangiu]

1.6.2 - (2020-08-21)
--------------------
* Implement auth/token for API endpoints access
  [dianaboiangiu]

1.6.1 - (2020-08-13)
--------------------
* Update emailtemplates fixtures
* Fix postoffice in admin
* Allow owner company accounts password reset
* Fix login cache
  [dianaboiangiu]

1.6.0 - (2020-08-10)
--------------------
* Add support for multiple reporters for a company
* Add company owner
* Implement set password functionality
* Send reset password mail after company owner is changed
* Add endpoint for showing one account's companies
* Allow functionality for HDV only
* Custom email depeding on users
  [dianaboiangiu]

1.5.5 - (2020-04-22)
--------------------
* Set HDV mailing for OTRS
  [dianaboiangiu]

1.5.4 - (2020-04-22)
--------------------
* Set headers for HDV mails
  [dianaboiangiu]

1.5.3 - (2020-04-22)
--------------------
* Set different sending address for HDV
  [dianaboiangiu]

1.5.2 - (2020-04-09)
--------------------
* Add to mail for HDV
  [dianaboiangiu]

1.5.1 - (2020-04-08)
--------------------
* Set different sending address for HDV
  [dianaboiangiu]

1.5.0 - (2020-04-07)
--------------------
* Update self register done page for HDV
  [dianaboiangiu]

1.4.13 - (2020-04-06)
---------------------
* Implement small HDV fixes
  [dianaboiangiu]

1.4.12 - (2020-04-06)
---------------------
* Set HDV sender e-mail address
  [dianaboiangiu]

1.4.11 - (2020-04-03)
--------------------
* Update self registry hdv text
  [dianaboiangiu]

1.4.10 - (2020-04-03)
--------------------
* Upgrade security packages
  [dianaboiangiu]

1.4.9 - (2020-04-03)
--------------------
* Allow null values for HDV countries
  [dianaboiangiu]

1.4.8 - (2020-04-02)
--------------------
* Add new HDV obligation
  [dianaboiangiu]

1.4.7 - (2020-02-07)
--------------------
* Add captcha on self registration page
  [dianaboiangiu]

1.4.6 - (2019-08-22)
--------------------
* Grab sidemenu from BDR
  [dianaboiangiu]

1.4.5 - (2018-03-12)
--------------------
* Update text on self registration
* Remove obligations from self registration
  [dianaboiangiu]

1.4.4 - (2018-03-07)
--------------------
* Fix bytes error in create account
  [dianaboiangiu]

1.4.3 - (2018-03-07)
-------------------
* Fix bytes error in create account
  [dianaboiangiu]

1.4.2 - (2018-03-07)
--------------------
* Fix create accont, password reset
  [dianaboiangiu]

1.4.1 - (2018-02-20)
--------------------
* Fix typo
  [nico4]

1.4.0 - (2018-02-20)
--------------------
* Aaa EORI column
  [nico4]

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
