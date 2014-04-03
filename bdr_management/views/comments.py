from django.core.urlresolvers import reverse
from django.views import generic
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin

from bdr_registry.models import Organisation, Comment
from braces.views import GroupRequiredMixin
from bdr_management.base import ModelTableEditMixin
from bdr_management.forms import CommentForm


class CommentCreate(GroupRequiredMixin,
                    ModelTableEditMixin,
                    SuccessMessageMixin,
                    generic.CreateView):

    template_name = 'comment_edit.html'
    form_class = CommentForm
    model = Comment
    group_required = 'BDR helpdesk'
    success_message = _("Comment added successfully")

    def dispatch(self, *args, **kwargs):
        self.organisation = get_object_or_404(Organisation, **self.kwargs)
        return super(CommentCreate, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('management:organisations_view', kwargs=self.kwargs)

    def get_form_kwargs(self, **kwargs):
        data = super(CommentCreate, self).get_form_kwargs(**kwargs)
        data['initial']['organisation'] = self.organisation
        return data

    def get_context_data(self, **kwargs):
        context = super(CommentCreate, self).get_context_data(**kwargs)
        context['title'] = 'Add a new comment'
        context['object'] = self.organisation
        return context


class CommentDelete(GroupRequiredMixin,
                    generic.DeleteView):

    group_required = 'BDR helpdesk'

    def dispatch(self, *args, **kwargs):
        self.organisation = get_object_or_404(
            Organisation,
            pk=self.kwargs['organisation_id'])
        return super(CommentDelete, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('management:organisations_view',
                       kwargs={'pk': self.kwargs['organisation_id']})

    def get_object(self):
        return get_object_or_404(Comment, pk=self.kwargs['pk'],
                                 organisation=self.organisation)

    def delete(self, request, *args, **kwargs):
        messages.success(request, _("Comment deleted"))
        return super(CommentDelete, self).delete(request, *args, **kwargs)
