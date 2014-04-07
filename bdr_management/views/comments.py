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


class CommentManagementCreate(CommentCreateBase,
                              GroupRequiredMixin):

    group_required = 'BDR helpdesk'


class CommentCreate(CommentCreateBase,
                    base.OrganisationUserRequiredMixin):

    pass


class CommentDeleteBase(generic.DeleteView):

    def dispatch(self, *args, **kwargs):
        self.organisation = get_object_or_404(
            Organisation,
            pk=self.kwargs['organisation_id'])
        return super(CommentDeleteBase, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('management:organisations_view',
                       kwargs={'pk': self.kwargs['organisation_id']})

    def get_object(self):
        return get_object_or_404(Comment, pk=self.kwargs['pk'],
                                 organisation=self.organisation)

    def delete(self, request, *args, **kwargs):
        messages.success(request, _("Comment deleted"))
        return super(CommentDeleteBase, self).delete(request, *args, **kwargs)


class CommentManagementDelete(CommentDeleteBase, GroupRequiredMixin):

        group_required = 'BDR helpdesk'


class CommentDelete(CommentDeleteBase, base.OrganisationUserRequiredMixin):

    pass