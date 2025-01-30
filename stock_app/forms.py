from django import forms
from src.services.yfinance_service import StockData

class StockForm(forms.Form):
    ticker = forms.CharField(
        label="Ticker Symbol",
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., AAPL',
            'pattern': '^[A-Za-z.]{1,10}$'
        })
    )
    
    period = forms.ChoiceField(
        label="Period",
        choices=[(period, period) for period in StockData.get_available_periods()],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    interval = forms.ChoiceField(
        label="Interval",
        choices=[],  # Initially empty; populated via AJAX
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        super(StockForm, self).__init__(*args, **kwargs)
        if 'period' in self.data:
            try:
                period = self.data.get('period')
                self.fields['interval'].choices = [
                    (interval, interval) for interval in StockData.get_available_intervals(period)
                ]
            except (ValueError, TypeError):
                self.fields['interval'].choices = []
        elif self.initial.get('period'):
            period = self.initial.get('period')
            self.fields['interval'].choices = [
                (interval, interval) for interval in StockData.get_available_intervals(period)
            ]
        else:
            self.fields['interval'].choices = []
    
    def clean_ticker(self):
        """Validate ticker format"""
        ticker = self.cleaned_data['ticker']
        if not ticker.replace('.', '').isalpha():
            raise forms.ValidationError("Invalid ticker format. Only letters and periods are allowed.")
        return ticker.upper()