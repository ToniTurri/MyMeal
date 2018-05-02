from django import forms

class BarcodeForm(forms.Form):
    barcode = forms.CharField(label='Barcode Number', max_length=13)