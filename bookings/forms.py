from django import forms

from .models import CustomerData, BillingData, InventoryData, StayData


class CustomerInfoForm(forms.ModelForm):

    class Meta:
        model = CustomerData
        fields = '__all__'
        exclude=[ 'timeCreated', 'account', 'user', 'account_index']  # Exclude account and user from the form
        
        widgets = {
          'customer_notes': forms.Textarea(attrs={'rows':2, 'cols':18}),
          'customer_name': forms.TextInput(attrs={'size':40}),
        }

    def clean_customer_name(self):
        return self.cleaned_data['customer_name'].capitalize()

    def save(self, commit=True, user=None):
        instance = super().save(commit=False)
        if user:
            # Automatically set the account to the first group of the user
            instance.account = user.groups.first()  # Assumes the user belongs to at least one group
            instance.user = user  # Set the user
        if commit:
            instance.save()
        return instance


class BillForm(forms.ModelForm):
    class Meta:
        model = BillingData
        fields = '__all__'
        exclude=['discount','bill_date','note','status']

class InventoryForm(forms.ModelForm):
    class Meta:
        model=InventoryData
        fields = '__all__'
        exclude=['nitem', 'item_type','hsn']


class StayDataForm(forms.ModelForm):
    class Meta:
        model=StayData
        fields = '__all__'