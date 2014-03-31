from bdr_registry.models import Comment
from braces.views import LoginRequiredMixin, StaffuserRequiredMixin
from django.core.urlresolvers import reverse
from django.views.generic import CreateView, DeleteView


class CommentCreate(LoginRequiredMixin,
                    StaffuserRequiredMixin,
                    CreateView):

    template_name = 'edit.html'
    fields = ['text']
    model = Comment

    def form_valid(self, form):
        form.instance.organisation_id = self.kwargs['pk']
        return super(CommentCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse('management:organisations_view', kwargs=self.kwargs)


class CommentDelete(LoginRequiredMixin,
                    StaffuserRequiredMixin,
                    DeleteView):
    model = Comment

    def get_success_url(self):
        return reverse('management:organisations_view',
                       kwargs={'pk': self.kwargs['organisation_id']})

