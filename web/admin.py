# -*- coding: utf-8 -*-

__author__ = 'mauricio'
import csv
from django.contrib import admin
from django.conf import settings
from django.db.models.loading import get_model
from django.db import models
from django import forms
#models
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from web.models import RegisterBusiness, EmailUs, Page, Module, \
    Header, SimpleText, ComplexText, BlockHome, Testimonial, \
    CouponRequestsForm, UserProfile, ImagesPrintMaps, PrintMaps, LandingPage, \
    LandingText, HeaderPage, Video, LandingSocial, PhoneNumber, RegisterUser, CategoryRegisterBusiness, \
    MarketingTypes, MarketingTactics, ConductMarketing, FrecuencyMarketing, MonthMarketing, Post, \
    PostCategory, Newsletter
from community.models import Business
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse


def export_as_csv(modeladmin, request, queryset):
    """
    Vista para manejar la exportación de datos a Excel
    """
    if not request.user.is_staff:
        raise PermissionDenied
    opts = modeladmin.model._meta
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % unicode(opts).replace('.', '_')
    writer = csv.writer(response)
    # Write data rows
    for obj in queryset:
        writer.writerow([obj.email, obj.name])
    return response
export_as_csv.short_description = "Export to Excel Sheet"


def CustomTabularAdmin(modelo, max):
    class AdminCustom(admin.TabularInline):
        model = get_model("web", modelo)
        max_num = max

        def formfield_for_dbfield(self, db_field, **kwargs):
            if isinstance(db_field, models.TextField):
                return forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'cols': 20, 'class': 'vLargeTextField'}),
                                       required=False)
            return super(AdminCustom, self).formfield_for_dbfield(db_field, **kwargs)

    return AdminCustom


class AdminPage(admin.ModelAdmin):
    def __init__(self, *args, **kwargs):
        self.inline_instances = []
        self.inlines = []
        super(AdminPage, self).__init__(*args, **kwargs)

    def add_view(self, request):
        self.inlines = []
        self.inline_instances = []
        return super(AdminPage, self).add_view(request)

    def change_view(self, request, object_id, extra_context=None):
        page_object = Page.objects.get(pk=object_id)
        lista = []
        if page_object:
            module_objects = Module.objects.filter(page=page_object.template)
            for module in module_objects:
                tabular = CustomTabularAdmin(module.get_type_module_display(), module.quantum)
                lista.append(tabular)
            self.inlines = lista
            self.inline_instances = []
            for inlines in self.inlines:
                inline_instance = inlines(self.model, self.admin_site)
                self.inline_instances.append(inline_instance)
        else:
            self.inlines = []
            self.inline_instances = []
        return super(AdminPage, self).change_view(request, object_id, extra_context=None)

    prepopulated_fields = {
        "url_name": ('name',),
        "title": ('name',)
    }

    fieldsets = (
        (
            None, {
                'fields': ('name', 'is_a_root', 'url_name', 'published', 'is_menu', 'template')
            }),
        (
            'Seo Fields', {
                'classes': ('collapse',),
                'fields': ('title', 'keywords', 'description')
            }
        )
    )

    class Media:
        js = (
            '%sweb/tinymce/jscripts/tiny_mce/tiny_mce.js' % settings.STATIC_URL,
            'https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js',
            '%sweb/markitup/jquery.markitup.js' % settings.STATIC_URL,
            '%sweb/markitup/sets/default/set.js' % settings.STATIC_URL,
            '%sweb/js/textareas.js' % settings.STATIC_URL,
            '%sweb/js/cms.js' % settings.STATIC_URL,
            '%sweb/js/collapsible.js' % settings.STATIC_URL,
        )
        css = {
            'all': (
                '%sweb/markitup/skins/simple/style.css' % settings.STATIC_URL,
                '%sweb/markitup/sets/default/style.css' % settings.STATIC_URL,
                '%sweb/css/collapsible.css' % settings.STATIC_URL,
            )
        }

    list_display = ('name', 'template', 'is_a_root', 'published', 'is_menu', 'EditContent')


class AdminModule(admin.ModelAdmin):
    list_display = ('page', 'type_module', 'quantum',)


class AdminCoupon(admin.ModelAdmin):
    list_display = ('name', 'cellphone', 'email', 'community', 'subscribe')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class AdminRegisterBusiness(admin.ModelAdmin):
    actions = ['publish_register_business', ]
    list_filter = ('active',)
    list_display = (
        'name', 'address', 'city', 'owner', 'zip_code', 'contact', 'phone', 'email', 'cell', 'website', 'active',
        'urlbusines_admin')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def publish_register_business(self, request, queryset):
        from googlemaps import GoogleMaps
        from django.conf import settings

        for new_business in queryset:
            gmaps = GoogleMaps(settings.GOOGLE_MAPS_API_KEY)
            lat, lng = gmaps.address_to_latlng(new_business.address)
            address = 'Point(' + str(lng) + ' ' + str(lat) + ')'
            business_object = Business(
                name=new_business.name,
                geo=address,
                address=new_business.address,
                phones=new_business.phone,
                site=new_business.website,
                email=new_business.email
            )
            business_object.save()
            new_business.id_biz = business_object.pk
            new_business.save()
        queryset.update(active=True)
        self.message_user(request, '%s new business' % len(queryset))

    publish_register_business.short_description = 'Publish Register Business'


class AdminEmailUs(admin.ModelAdmin):
    list_display = ('name_is', 'email_is', 'phones_is', 'interested', 'questions')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

# class UserProfileInline(admin.StackedInline):
#     model = UserProfile
#     can_delete = False
#     verbose_name_plural = 'profile'
#
# # Define a new User admin
# class UserAdmin(UserAdmin):
#     inlines = (UserProfileInline, )

class AdminImagePrintMapsInline(admin.TabularInline):
    model = ImagesPrintMaps
    extra = 1


class AdminVideo(admin.TabularInline):
    model = Video
    extra = 1


class AdminLandingText(admin.TabularInline):
    model = LandingText
    extra = 1


class AdminLandingSocial(admin.TabularInline):
    model = LandingSocial


class AdminHeaderPage(admin.TabularInline):
    model = HeaderPage
    extra = 5


class AdminPhone(admin.TabularInline):
    model = PhoneNumber
    extra = 1


class AdminLandingPage(admin.ModelAdmin):
    inlines = [
        AdminVideo,
        AdminLandingSocial,
        AdminLandingText,
        AdminHeaderPage,
        AdminPhone
    ]


class AdminPrintMaps(admin.ModelAdmin):
    extra_js = ['http://maps.google.com/maps/api/js?sensor=true&language=en']
    inlines = [AdminImagePrintMapsInline]
    fieldsets = (
        (
            None, {
                'fields': ('title', 'description', 'type_img_src', 'maps_customize')
            },
        ),
        #(
        #    'Customize Images',{
        #        'fields':('maps_customize')
        #    }
        #),
    )

    class Media:
        js = [
            'http://ajax.googleapis.com/ajax/libs/jquery/1.8.0/jquery.min.js',
            '%stinymce/jscripts/tiny_mce/tiny_mce.js' % settings.STATIC_URL,
            '/detour/js/tiny.js?textarea_id=id_maps_customize',
        ]
        css = {
            'all': (
                '%scommunity/css/collapsible.css' % settings.STATIC_URL,
            )
        }


class AdminPost(admin.ModelAdmin):
    prepopulated_fields = {
        'url_name': ('name',)
    }


class AdminPostCategory(admin.ModelAdmin):
    prepopulated_fields = {
        'url_name': ('name',)
    }


class AdminNewsletter(admin.ModelAdmin):
    actions = [export_as_csv]


admin.site.register(PrintMaps, AdminPrintMaps)
admin.site.register(RegisterUser)
admin.site.register(CategoryRegisterBusiness)
admin.site.register(MarketingTypes)
admin.site.register(MarketingTactics)
admin.site.register(ConductMarketing)
admin.site.register(FrecuencyMarketing)
admin.site.register(MonthMarketing)
admin.site.register(CouponRequestsForm, AdminCoupon)
admin.site.register(RegisterBusiness, AdminRegisterBusiness)
admin.site.register(EmailUs, AdminEmailUs)
admin.site.register(Page, AdminPage)
admin.site.register(Module, AdminModule)
admin.site.register(LandingPage, AdminLandingPage)
admin.site.register(Post, AdminPost)
admin.site.register(PostCategory, AdminPostCategory)
admin.site.register(Newsletter, AdminNewsletter)