# -*- coding: utf-8 -*-
__author__ = 'mauricio'

from django import forms
#localflavors
from localflavor.us.forms import USPhoneNumberField, USZipCodeField, USStateSelect
from localflavor.us.us_states import STATE_CHOICES
from models import CouponRequestsForm, SimpleText, ComplexText, Testimonial, BlockHome, Header

class FormRegister(forms.Form):
    name = forms.CharField(max_length=48, label='Name of Business', help_text='e.g. Google')
    address = forms.CharField(max_length=72, label='Address',
        help_text='e.g. 1600 Amphitheatre Parkway, Mountain View, CA')
    city = forms.CharField(max_length=36, label='City / State', help_text='e.g. Mountain View')
    owner = forms.CharField(max_length=36, label='Owner', help_text='e.g. John Doe')
    zip_code = USZipCodeField(label='Zip Code', help_text='e.g. 90001', required=False)
    contact = forms.CharField(max_length=36, label='Contact', help_text='e.g. Jane Doe')
    phone = USPhoneNumberField(label='Phone', help_text='e.g. 999-999-9999')
    email = forms.EmailField(label='Email')
    cell = forms.CharField(max_length=36, label='Cell', required=False)
    website = forms.URLField(label='Website', required=False)

    def __init__(self,*args,**kwargs):
        super(FormRegister,self).__init__(*args,**kwargs)
        for f in self.fields:
            self.fields[f].widget.attrs['placeholder'] = self.fields[f].help_text
            #if self.fields[f].help_text:
            #    self.fields[f].widget.attrs['placeholder'] += ' : ' + self.fields[f].help_text
            if self.fields[f].required:
                self.fields[f].widget.attrs['placeholder'] += ' *'



class FormContactUs(forms.Form):
    CHOICES_INTERESTED = (
        ('FA','Free Advertising'),
        ('DA','DetourMaps Advertising'),
        ('SC','$10 Savings Card'),
        ('GW','Graphic & Web'),
        ('MT','Mobile Text'),
        ('SM','Social Media'),
        ('EB','Email Blast'),
        ('CP','Create Promotions'),
        ('PV','Photo & Video'),
        ('SG','Suggestions')
    )
    interested = forms.CharField(widget=forms.Select(choices=CHOICES_INTERESTED), label="I'm interested in :" )
    name_is = forms.CharField(label='My Name is :')
    email_is = forms.EmailField(label='My Email is :')
    phones_is = USPhoneNumberField(label='My Phone is :')
    questions = forms.CharField(widget=forms.Textarea,label='Questions or Comments :', required = False)

class FormCouponsRequest(forms.ModelForm):
    class Meta:
        model = CouponRequestsForm

class FormApply(forms.Form):
    choices = (
        ('SalesRepresentative', 'Sales Representative'),
        ('InsideSales', 'Inside Sales'),
        ('TechnologyProgram', 'Technology Program'),
        ('DigitalMarketingNDesignCoordinator', 'Digital Marketing & Design Coordinator'),
        ('AssistantDirectorOfMediaNCommunications', 'Assistant Director Of Media & Communications'),
        ('Internship', 'Internship'),
    )
    interested = forms.CharField(widget=forms.Select(choices=choices), label="I'm interested in :" )
    name = forms.CharField(label='Name')
    email = forms.EmailField(label='Email')
    phones = USPhoneNumberField(label='Phone')
    resume = forms.FileField(label='Your Resume')

##############    model forms for the CMS #####################################################################################################3


class FormSimpleText(forms.ModelForm):

    class Meta:
        model = SimpleText
        exclude = ('page',)

class FormComplexText(forms.ModelForm):

    class Meta:
        model = ComplexText
        exclude = ('page',)

class FormTestimonial(forms.ModelForm):

    class Meta:
        model = Testimonial
        exclude = ('page',)

class FormBlockHome(forms.ModelForm):

    class Meta:
        model = BlockHome
        exclude = ('page',)

class FormHeader(forms.ModelForm):

    class Meta:
        model = Header
        exclude = ('page',)
