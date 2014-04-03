from django.forms import ModelForm
from bdr_registry.models import Comment



class CommentForm(ModelForm):

    class Meta():
        model = Comment
        fields = ('text',)

    def save(self, **kwargs):
        comment = super(CommentForm, self).save(commit=False)
        comment.organisation = self.initial['organisation']
        comment.save()
        return comment
