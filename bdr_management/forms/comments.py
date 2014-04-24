from django.forms import ModelForm
from bdr_registry.models import Comment


class CommentForm(ModelForm):

    class Meta():
        model = Comment
        fields = ('text',)

    def save(self, **kwargs):
        comment = super(CommentForm, self).save(commit=False)
        comment.company = self.initial['company']
        comment.save()
        return comment
