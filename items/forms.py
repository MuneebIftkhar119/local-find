from django import forms
from .models import Item, Claim, FoundResponse


class ItemForm(forms.ModelForm):
    date_of_incident = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model  = Item
        fields = ('item_type', 'title', 'category', 'description', 'location', 'date_of_incident', 'image')
        widgets = {
            'item_type':   forms.Select(attrs={'class': 'form-select'}),
            'title':       forms.TextInput(attrs={'placeholder': 'e.g. Black leather wallet'}),
            'category':    forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe the item in detail...'}),
            'location':    forms.TextInput(attrs={'placeholder': 'e.g. Library, Block C'}),
        }


class ClaimForm(forms.ModelForm):
    class Meta:
        model  = Claim
        fields = ('proof_description', 'contact_details')
        widgets = {
            'proof_description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe how you can prove this is yours...'}),
            'contact_details':   forms.TextInput(attrs={'placeholder': 'Phone number or email'}),
        }


class SearchForm(forms.Form):
    query    = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Search items...'}))
    category = forms.ChoiceField(required=False, choices=[('', 'All Categories')] + Item.CATEGORY_CHOICES)
    item_type = forms.ChoiceField(required=False, choices=[('', 'Lost & Found'), ('lost', 'Lost'), ('found', 'Found')])
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    date_to   = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))


class FoundResponseForm(forms.ModelForm):
    class Meta:
        model = FoundResponse
        fields = ('message', 'contact_details')
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 4,
                 'placeholder': 'e.g. I found this wallet near the library on Monday. It is safe with me and I can return it at your convenience.'
            }),
            'contact_details': forms.TextInput(attrs={
                'placeholder': 'Your phone number or email address'
            }),
        }
        labels = {
            'message': 'Your Message',
            'contact_details': 'Contact details',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'