from django import forms

class BarcodeForm(forms.Form):
    number = forms.CharField(label='Barcode Number', max_length=13)