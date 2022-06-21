from django import forms
from .models import Publisher, Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        exclude = ('date_edited', 'book')
        
    rating = forms.IntegerField(min_value=0, max_value=5)


class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        exclude = ()
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "The publisher's name."})
        }
    
    email_on_save = forms.BooleanField(required=False, help_text="Send notification email on save")


class SearchForm(forms.Form):
    SEARCH_CHOICES = (("title", "Title"),
                ("contributor", "Contributor"),                
    )
    search = forms.CharField(required=False, min_length=3)
    search_in = forms.ChoiceField(required=False, choices=SEARCH_CHOICES)