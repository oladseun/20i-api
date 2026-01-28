from django import forms

class TicketForm(forms.Form):
    PRIORITY_CHOICES = [
        ('low', 'Low - General Question'),
        ('normal', 'Normal - Service Issue'),
        ('high', 'High - Critical Outage'),
    ]
    
    subject = forms.CharField(
        max_length=200, 
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Brief summary of the issue'
        })
    )
    
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 5,
            'placeholder': 'Describe your issue in detail...'
        })
    )
