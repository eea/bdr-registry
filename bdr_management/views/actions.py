from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views import generic

from braces import views
import django_settings
from django.contrib import messages

from bdr_management.base import Breadcrumb
from bdr_registry.models import ReportingYear, Company, ReportingStatus


class Actions(views.StaffuserRequiredMixin,
              generic.TemplateView):

    template_name = 'bdr_management/actions.html'
    raise_exception = True

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb('', _('Actions')),
        ]
        data = super(Actions, self).get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        curr_year = django_settings.get("Reporting year")
        last_year = curr_year - 1
        data['curr_year'] = curr_year
        data['last_year'] = last_year
        return data


class CopyReportingStatus(views.StaffuserRequiredMixin,
                          generic.View):

    raise_exception = True

    def get(self, request):
        copied = 0

        curr_year_int = django_settings.get('Reporting year')
        prev_year_int = curr_year_int - 1

        try:
                prev_year_obj = ReportingYear.objects.get(year=prev_year_int)
                curr_year_obj = ReportingYear.objects.get(year=curr_year_int)
        except ObjectDoesNotExist:
            messages.error(request,
                           _('Previous or current year data not found'))
            return HttpResponseRedirect(reverse('management:actions'))

        for company in Company.objects.all():

            reporting_stat, created = company.reporting_statuses.get_or_create(
                company=company,
                reporting_year=curr_year_obj
            )
            if reporting_stat.reported is None:
                prev_reporting_stat, created = ReportingStatus.objects.get_or_create(
                    company=company,
                    reporting_year=prev_year_obj
                )
                if prev_reporting_stat.reported is not None:
                    reporting_stat.reported = prev_reporting_stat.reported
                    reporting_stat.save()
                    copied += 1
        messages.success(request,
                         _('Data copied for %s companies.' % copied))

        return HttpResponseRedirect(reverse('management:actions'))
