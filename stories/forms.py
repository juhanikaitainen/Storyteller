from .models import Story
from django import forms

class StoryApprovalForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = [ 'rating', 'approved' ]