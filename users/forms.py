from django import forms
from .models import Customuser, Application
from datetime import date

class DateInput(forms.DateInput):
    input_type = 'date'

class CustomuserCreationForm(forms.ModelForm):
    class Meta:
        model = Customuser
        fields = ['name', 'dob']
        widgets = {
            'dob': DateInput()
        }
        labels = {
            'dob': 'Date of Birth'
        }
    
    def clean_dob(self):
        data = self.cleaned_data['dob']
        if data >= date.today():
            raise forms.ValidationError("Date of birth cannot be in the future")
        return data

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['totype', 'req']
        widgets = {
            'req': forms.Textarea()
        }
        labels = {
            'totype': 'Promote To',
            'req': 'Message'
        }