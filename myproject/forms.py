from django import forms

class CreatePodForm(forms.Form):
    name = forms.CharField(max_length=100)
    image = forms.CharField(max_length=100)
    namespace = forms.CharField(max_length=100)
    # Add more fields as needed

class CreateNamespaceForm(forms.Form):
    name = forms.CharField(max_length=100)
   