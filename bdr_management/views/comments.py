from bdr_management.base import Breadcrumb
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.views import generic

from braces.views import GroupRequiredMixin

from bdr_management import base, forms
from bdr_registry.models import Organisation, Comment


class CommentCreateBase(SuccessMessageMixin,
                        generic.CreateView):

    template_name = 'bdr_management/comment_edit.html'
    form_class = forms.CommentForm
    model = Comment
    success_message = _("Comment added successfully")

    def dispatch(self, *args, **kwargs):
        self.organisation = get_object_or_404(Organisation, **self.kwargs)
        return super(CommentCreateBase, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('management:organisations_view', kwargs=self.kwargs)

    def get_form_kwargs(self, **kwargs):
        data = super(CommentCreateBase, self).get_form_kwargs(**kwargs)
        data['initial']['organisation'] = self.organisation
        return data

    def get_context_data(self, **kwargs):
        context = super(CommentCreateBase, self).get_context_data(**kwargs)
        context['title'] = 'Add a new comment'
        context['object'] = self.organisation
        return context


class CommentManagementCreate(GroupRequiredMixin,
                              CommentCreateBase):

    group_required = 'BDR helpdesk'

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb(reverse('management:organisations'), _('Organisations')),
            Breadcrumb(reverse('management:organisations_view',
                               kwargs=self.kwargs),
                       self.organisation),
            Breadcrumb('', _('Add comment'))
        ]
        data = super(CommentManagementCreate, self).get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        return data


class CommentCreate(base.OrganisationUserRequiredMixin,
                    CommentCreateBase):

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb(reverse('organisation', kwargs=self.kwargs),
                       self.organisation),
            Breadcrumb('', _('Add comment'))
        ]
        data = super(CommentCreate, self).get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        return data


class CommentDeleteBase(generic.DeleteView):

    pk_url_kwarg = 'comment_pk'
    model = Comment

    def dispatch(self, request, *args, **kwargs):
        self.organisation = get_object_or_404(Organisation,
                                              pk=self.kwargs['pk'])
        return super(CommentDeleteBase, self).dispatch(request, *args,
                                                       **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(request, _("Comment deleted"))
        return super(CommentDeleteBase, self).delete(request, *args, **kwargs)


class CommentManagementDelete(GroupRequiredMixin,
                              CommentDeleteBase):

    group_required = 'BDR helpdesk'

    def get_success_url(self):
        return reverse('management:organisations_view',
                       kwargs={'pk': self.organisation.pk})


class CommentDelete(base.OrganisationUserRequiredMixin,
                    CommentDeleteBase):

    def get_success_url(self):
        return reverse('organisation', kwargs={'pk': self.organisation.pk})
