import autocomplete_light
from gumbug.models import Station

class StationAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['^name']

    def choice_label(self, choice):
        return choice.name

autocomplete_light.register(Station, StationAutocomplete)
