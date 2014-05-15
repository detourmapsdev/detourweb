# -*- coding: utf-8 -*-
__author__ = 'mauricio'

from django import forms
from django.contrib.gis.geos.geometry import GEOSGeometry
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import ugettext_lazy as _
#models
from community.models import ImageBusiness, Business, Partner


class FormBusiness(forms.ModelForm):
    #Delete this, nothing here is used
    def __init__(self, *args, **kwargs):
        super(FormBusiness, self).__init__(*args, **kwargs)
        self.fields['gallery'].queryset = ImageBusiness.objects.filter(business__pk=1)

    gallery = forms.ModelMultipleChoiceField(
        queryset=ImageBusiness.objects.all(),
        required=False,
        widget=forms.SelectMultiple()
    )

    class Meta:
        model = Business


class PartnerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PartnerForm, self).__init__(*args, **kwargs)
        if self.instance.community_id:
            wtf = Business.objects.filter(community__id=self.instance.community_id)
        else:
            wtf = Business.objects.all()
        w = self.fields['business'].widget
        choices = []
        for choice in wtf:
            choices.append((choice.id, choice.name))
        w.choices = choices
    
    
