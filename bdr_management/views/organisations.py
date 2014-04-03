from datetime import date, timedelta

from bdr_management.forms.organisations import OrganisationForm
from braces.views import SuperuserRequiredMixin
from django.views import generic
from django.contrib.auth.views import redirect_to_login
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Q
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from braces import views
from braces.views._access import AccessMixin
from bdr_registry.models import Organisation
from bdr_management import base, forms


class OrganisationUserRequiredMixin(AccessMixin):

    group_required = 'BDR helpdesk'

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.organisation = get_object_or_404(Organisation, **self.kwargs)

        if not self._check_perm():
            return redirect_to_login(request.get_full_path(),
                                     self.get_login_url(),
                                     self.get_redirect_field_name())

        return super(OrganisationUserRequiredMixin, self) \
            .dispatch(request, *args, **kwargs)

    def _check_perm(self):
        if self.request.user.is_superuser:
            return True

        group = self.group_required
        if group in self.request.user.groups.values_list('name', flat=True):
            return True

        account = self.organisation.account
        if account == self.request.user.username:
            return True
        return False


class Organisations(views.StaffuserRequiredMixin,
                    generic.TemplateView):

    template_name = 'bdr_management/organisations.html'

    def get_context_data(self, **kwargs):
        context = super(Organisations, self).get_context_data(**kwargs)
        context['form'] = forms.OrganisationFilters()
        return context


class OrganisationsFilter(views.StaffuserRequiredMixin,
                          base.FilterView):

    def process_name(self, object, val):
        url = reverse('management:organisations_view',
                      kwargs={'pk': object.pk})
        return '<a href="%s">%s</a>' % (url, val)

    def process_date_registered(self, object, val):
        return val.strftime(settings.DATE_FORMAT)

    def get_queryset(self, opt):
        queryset = Organisation.objects.all()

        if 'order_by' in opt and opt['order_by']:
            queryset = queryset.order_by(opt['order_by'])

        if 'search' in opt and opt['search']:
            search_filters = (
                Q(name__icontains=opt['search']) |
                Q(account__uid__icontains=opt['search']) |
                Q(addr_postalcode__icontains=opt['search']) |
                Q(vat_number__icontains=opt['search']) |
                Q(eori__icontains=opt['search'])
            )
            queryset = queryset.filter(search_filters)

        filters = opt.get('filters', {})
        if 'country' in filters:
            queryset = queryset.filter(
                country__name=filters['country'])
        if 'obligation' in filters:
            queryset = queryset.filter(
                obligation__name=filters['obligation'])
        if 'account' in filters:
            if filters['account'] == forms.OrganisationFilters.WITHOUT_ACCOUNT:
                queryset = queryset.exclude(account__isnull=False)
            else:
                queryset = queryset.exclude(account__isnull=True)
        if 'date_registered' in filters:
            start_date = self._get_startdate(filters['date_registered'])
            queryset = queryset.exclude(date_registered__lt=start_date)

        if opt['count']:
            return queryset.count()

        return queryset[opt['offset']: opt['limit']]

    def _get_startdate(self, selected_option):
        today = date.today()
        if selected_option == forms.OrganisationFilters.TODAY:
            start_date = today
        elif selected_option == forms.OrganisationFilters.LAST_7_DAYS:
            start_date = today - timedelta(days=7)
        elif selected_option == forms.OrganisationFilters.THIS_MONTH:
            start_date = date(today.year, today.month, 1)
        else:
            start_date = date(today.year, 1, 1)
        return start_date


class OrganisationsBaseView(base.ModelTableViewMixin,
                            generic.DetailView):

    template_name = 'bdr_management/organisation_view.html'
    model = Organisation
    exclude = ('id', )

    def get_edit_url(self):
        return reverse('management:organisations_edit', kwargs=self.kwargs)

    def get_delete_url(self):
        return reverse('management:organisations_delete', kwargs=self.kwargs)


class OrganisationsManagementView(views.StaffuserRequiredMixin,
                                  OrganisationsBaseView):
    pass


class OrganisationsUpdateView(OrganisationUserRequiredMixin,
                              OrganisationsBaseView):
    pass


class OrganisationsEdit(views.GroupRequiredMixin,
                        base.ModelTableEditMixin,
                        SuccessMessageMixin,
                        generic.UpdateView):

    template_name = 'bdr_management/organisation_edit.html'
    group_required = 'BDR helpdesk'
    model = Organisation
    success_message = _('Organisation edited successfully')

    def get_success_url(self):
        return reverse('management:organisations_view', kwargs=self.kwargs)


class OrganisationDelete(views.GroupRequiredMixin,
                         base.ModelTableEditMixin,
                         generic.DeleteView):

    group_required = 'BDR helpdesk'
    model = Organisation
    success_url = reverse_lazy('management:organisations')

    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Organisation deleted'))
        return super(OrganisationDelete, self).delete(request, *args, **kwargs)


class OrganisationAdd(SuperuserRequiredMixin,
                      generic.CreateView):

    template_name = 'bdr_management/organisation_add.html'
    model = Organisation
    form_class = OrganisationForm
    success_message = _('Organisation created successfully')

    def get_success_url(self):
        return reverse('management:organisations')

    def get_context_data(self, **kwargs):
        context = super(OrganisationAdd, self).get_context_data(**kwargs)
        context['title'] = 'Add a new organisation'
        return context
