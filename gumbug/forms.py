import logging
from django.forms.widgets import HiddenInput
from django import forms
from django.forms.models import modelformset_factory, BaseModelFormSet

from gumbug.models import Search, SearchUrl


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

    def save(self, *args, **kwargs):
        return super(SearchForm, self).save(*args, **kwargs)


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
                                        extra=8,
                                        exclude=['search'])
