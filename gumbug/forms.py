import logging
from django.forms.widgets import HiddenInput
from django import forms
from django.forms.models import modelformset_factory, BaseModelFormSet

from gumbug.models import Search, SearchUrl, StationFilter, Station
import autocomplete_light


class SearchForm(forms.ModelForm):

    refetch_listings = forms.BooleanField(required=False)

    class Meta:
        model = Search
        fields = ['parent', 'ignore_keywords', 'require_keywords',
                  'preserve_ignored', 'preserve_favorites', 'refetch_listings']
        widgets = {
            'parent': HiddenInput(),
            'ignore_keywords': forms.Textarea(attrs={'rows': 3, 'cols': 80}),
            'require_keywords': forms.Textarea(attrs={'rows': 3, 'cols': 80}),
        }


class SearchUrlForm(forms.ModelForm):

    class Meta:
        model = SearchUrl
        fields = ['url']
        widgets = {
            'url': forms.URLInput(attrs={'placeholder': 'http://www.gumtree.com/...'})
        }


SearchUrlFormSet = modelformset_factory(SearchUrl,
                                        form=SearchUrlForm,
                                        min_num=1,
                                        validate_min=True,
                                        extra=12,
                                        exclude=['search'])


class StationForm(forms.ModelForm):

    class Meta:
        model = StationFilter
        fields = ['station', 'min_dist', 'max_dist']

    station = autocomplete_light.ChoiceField('StationAutocomplete')
    min_dist = forms.FloatField(label="Minimum distance (miles)",
                                required=False,
                                widget=forms.NumberInput(attrs={"step": "0.1"}))
    max_dist = forms.FloatField(label="Maximum distance (miles)",
                                required=False,
                                widget=forms.NumberInput(attrs={"step": "0.1"}))

    def clean_station(self):
        return Station.objects.get(pk=self.cleaned_data['station'])

StationFormSet = modelformset_factory(StationFilter,
                                      form=StationForm,
                                      extra=12,
                                      exclude=['search'])
