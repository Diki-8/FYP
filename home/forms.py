from django import forms
from home.models import Booking, TimeSlot, Dog
from django.utils import timezone

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['service', 'dog', 'date', 'time_slot', 'status', 'special_requests']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        is_admin = kwargs.pop('is_admin', False)
        super().__init__(*args, **kwargs)

        # Restrict dog queryset to user's dogs if not admin
        if user and not is_admin:
            self.fields['dog'].queryset = Dog.objects.filter(owner=user)
        else:
            self.fields['dog'].queryset = Dog.objects.all()

        # Make dog and user read-only for admins
        if is_admin:
            self.fields['dog'].disabled = True
            self.fields['user'] = forms.CharField(
                initial=self.instance.user.username if self.instance else '',
                disabled=True,
                required=False,
                widget=forms.TextInput(attrs={'class': 'form-control'})
            )
            # Add read-only health_notes field from Dog.special_notes
            self.fields['health_notes'] = forms.CharField(
                initial=self.instance.dog.special_notes if self.instance and self.instance.dog else '',
                disabled=True,
                required=False,
                widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
            )
            # Add read-only size field from Dog.size
            self.fields['dog_size'] = forms.CharField(
                initial=self.instance.dog.get_size_display if self.instance and self.instance.dog and self.instance.dog.size else 'Not specified',
                disabled=True,
                required=False,
                widget=forms.TextInput(attrs={'class': 'form-control'})
            )

        # Dynamically set time_slot queryset based on service
        if self.instance and self.instance.service:
            if self.instance.service in ['daycare', 'boarding']:
                self.fields['time_slot'].required = False
                self.fields['time_slot'].queryset = TimeSlot.objects.none()
            else:  # grooming
                self.fields['time_slot'].queryset = TimeSlot.objects.filter(service_type='grooming')
        else:
            self.fields['time_slot'].queryset = TimeSlot.objects.none()

        # Field widgets and attributes
        self.fields['service'] = forms.ChoiceField(
            choices=Booking._meta.get_field('service').choices,
            widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
        )
        self.fields['dog'] = forms.ModelChoiceField(
            queryset=self.fields['dog'].queryset,
            widget=forms.Select(attrs={'class': 'form-select'})
        )
        self.fields['date'] = forms.DateField(
            widget=forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'min': timezone.now().date()
                }
            )
        )
        self.fields['time_slot'] = forms.ModelChoiceField(
            queryset=self.fields['time_slot'].queryset,
            widget=forms.RadioSelect(attrs={'class': 'btn-check'}),
            required=False  # Make optional for daycare/boarding
        )
        self.fields['status'] = forms.ChoiceField(
            choices=Booking._meta.get_field('status').choices,
            widget=forms.Select(attrs={'class': 'form-select'})
        )
        self.fields['special_requests'] = forms.CharField(
            required=False,
            widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        )

    def clean(self):
        cleaned_data = super().clean()
        service = cleaned_data.get('service')
        time_slot = cleaned_data.get('time_slot')
        date = cleaned_data.get('date')
        # Validate date
        if date and date < timezone.now().date():
            self.add_error('date', 'Booking date cannot be in the past.')

        # Validate time_slot based on service
        if service in ['daycare', 'boarding']:
            cleaned_data['time_slot'] = None  # Force None for daycare/boarding
        elif service == 'grooming' and not time_slot:
            self.add_error('time_slot', 'Time slot is required for grooming.')

        return cleaned_data

        
