from django import forms
from .models import Venue

class VenueForm(forms.ModelForm):

    class Meta:
        model = Venue
        fields = [
            'name',
            'location',
            'capacity',
            'price',
            'image',
            'description'
        ]

        widgets = {

            'name': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'location': forms.Select(attrs={
                'class': 'form-select'
            }),

            'capacity': forms.NumberInput(attrs={
                'class': 'form-control'
            }),

            'price': forms.NumberInput(attrs={
                'class': 'form-control'
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),

            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }