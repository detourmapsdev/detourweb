# -*- coding: utf-8 -*-
__author__ = 'mauricio'

from django.contrib.gis import admin
from django.conf import settings
#models
from community.models import Service, Category, Subscription, Community, Business, \
    ImageBusiness, ImageCommunity, CuponBusiness, Review, BusinessEvent, ImageBusinessEvents, \
    BusinessMenu, BusinessSchedule, ContactCard, Card, NewsletterSuscription, Usuario, \
    Partner, LandingPartner, LandingSocialPartner, LandingTextPartner, VideoPartner, \
    HeaderPagePartner, BusinessEventPartner, ImageBusinessEventsPartner, NewDiscover, \
    PhoneNumber, CommunitySocial, CommunityText, HeaderCommunity, Video, HelpingShop, PromoPartner, \
    LandingEvent, PartnerMobile, TenVisitsBusiness, FeedbackBusiness, Bookmark

#forms
from community.forms import FormBusiness, PartnerForm
#sites
from django.contrib.sites.models import Site
#csv
import csv
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
        writer.writerow([obj.email, obj.first_name, obj.last_name, obj.interested_in, obj.age, obj.gender, obj.address, obj.phone, obj.business.name])
    return response
export_as_csv.short_description = "Export to Excel Sheet"


class AdminImageCommunityInline(admin.TabularInline):
    model = ImageCommunity
    extra = 1


class AdminNumberCommunityInline(admin.TabularInline):
    model = PhoneNumber
    extra = 1


class AdminSocialCommunityInline(admin.TabularInline):
    model = CommunitySocial
    extra = 1


class AdminTextCommunityInline(admin.TabularInline):
    model = CommunityText
    extra = 1


class AdminHeaderCommunityInline(admin.TabularInline):
    model = HeaderCommunity
    extra = 1


class AdminVideoCommunityInline(admin.TabularInline):
    model = Video
    extra = 1


class AdminNewDiscover(admin.TabularInline):
    model = NewDiscover
    extra = 5


class AdminMenuBusiness(admin.TabularInline):
    model = BusinessMenu
    extra = 1

    class Media:
        js = (
            'https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js',
            '%sweb/editor/js/editor.js' % settings.STATIC_URL,
            '%sweb/js/collapsible.js' % settings.STATIC_URL,
        )
        css = {
            'all': (
                '%sweb/editor/css/editor.css' % settings.STATIC_URL,
                '%sweb/css/collapsible.css' % settings.STATIC_URL,
            )
        }


class AdminScheduleBusiness(admin.TabularInline):
    model = BusinessSchedule
    extra = 1

    class Media:
        js = (
            'https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js',
            '%sweb/editor/js/editor.js' % settings.STATIC_URL,
            '%sweb/js/collapsible.js' % settings.STATIC_URL,
        )
        css = {
            'all': (
                '%sweb/editor/css/editor.css' % settings.STATIC_URL,
                '%sweb/css/collapsible.css' % settings.STATIC_URL,
            )
        }


class AdminCommunity(admin.OSMGeoAdmin):
    extra_js = [
        'http://maps.google.com/maps/api/js?sensor=true&language=en',
    ]
    map_template = 'gis/admin/google.html'
    inlines = [
        AdminImageCommunityInline,
        AdminNewDiscover,
        AdminNumberCommunityInline,
        AdminSocialCommunityInline,
        AdminTextCommunityInline,
        AdminHeaderCommunityInline,
        AdminVideoCommunityInline
    ]
    fieldsets = (
        (
            None, {
                'fields': (
                    ('name', 'url_name', 'active',),
                    ('keywords',),
                    ('description', 'history',),
                    'borders', 'zipcode',
                )
            },
        ),
        (
            'Discover', {
                'fields': ( 'discover_html', 'discover_css', 'has_css_file', 'css_file',)
            }
        ),
        (
            'Printed Map', {
                'fields': ('printed_map', 'img_printed_map')
            }
        )
    )

    class Media:
        js = [
            'http://code.jquery.com/jquery-1.7.2.min.js',
            '%scommunity/js/urlizer.js' % settings.STATIC_URL,
            '%stinymce/jscripts/tiny_mce/tiny_mce.js' % settings.STATIC_URL,
            '%scommunity/js/cms.js' % settings.STATIC_URL,
            '%scommunity/js/collapsible.js' % settings.STATIC_URL,
            '%scommunity/js/tiny.js' % settings.STATIC_URL,
        ]
        css = {
            'all': (
                '%scommunity/css/collapsible.css' % settings.STATIC_URL,
            )
        }


class AdminMobilePartner(admin.TabularInline):

    model = PartnerMobile
    extra = 1


class AdminPartner(admin.OSMGeoAdmin):
    extra_js = [
        'http://maps.google.com/maps/api/js?sensor=true&language=en',
    ]
    map_template = 'gis/admin/google.html'
    prepopulated_fields = {'url_name': ('name', )}
    filter_horizontal = ('business', )
    form = PartnerForm
    inlines = [
        AdminMobilePartner,
    ]


class AdminVideo(admin.TabularInline):
    model = VideoPartner
    extra = 1


class AdminLandingText(admin.TabularInline):
    model = LandingTextPartner
    extra = 1


class AdminLandingSocial(admin.TabularInline):
    model = LandingSocialPartner


class AdminHeaderPage(admin.TabularInline):
    model = HeaderPagePartner
    extra = 5


class AdminHelpingPage(admin.TabularInline):
    model = HelpingShop
    extra = 1


class AdminLandingPage(admin.ModelAdmin):
    inlines = [
        AdminVideo,
        AdminLandingSocial,
        AdminLandingText,
        AdminHeaderPage,
        AdminHelpingPage
    ]


class AdminSubscriptionInline(admin.TabularInline):
    readonly_fields = ('autorenewed', )
    model = Subscription
    extra = 1


class AdminImageBusinessInline(admin.TabularInline):
    model = ImageBusiness
    extra = 1


class AdminImageBusinessEventInline(admin.TabularInline):
    model = ImageBusinessEvents
    extra = 1


class AdminCuponBusinessInline(admin.TabularInline):
    model = CuponBusiness
    extra = 1


class AdminTenVists(admin.TabularInline):
    model = TenVisitsBusiness
    extra = 1

    def has_add_permission(self, request):
        num_objects = self.model.objects.count()
        if num_objects >= 1:
          return False
        else:
          return True


class AdminService(admin.ModelAdmin):
    fieldsets = ((None, {'fields': ('name', 'description', 'icon', 'subcat')}), )


class AdminBusiness(admin.ModelAdmin):
    class Media:
        js = [
            'http://code.jquery.com/jquery-1.7.0.min.js',
            'http://maps.google.com/maps/api/js?sensor=true&language=en',
            '%scommunity/js/location.js' % settings.STATIC_URL,
        ]

    fieldsets = (
        (None, {
            'fields': (
                ('community', 'category', ),
                ('chamber_member', 'belongs2community', 'enable_comments', 'full_version'),
                'name', 'url_name',
                ('description', 'history'),
                'tag_service', 'site', 'facebook', 'twitter', 'email', 'phones',
                'geo', 'address', 'rate_interval', 'logo', 'video', 'video_description'
            )
        }),
        (
            'Local Deals', {
                'fields': (
                    'local_deals',
                    'ten_visits',
                    'refer_friends',
                )
            }
        )
    )
    filter_horizontal = ('tag_service', )
    list_select_related = True
    list_display = ('name', 'community', 'category', 'site', 'phones', 'local_deals')
    list_filter = ('community', 'category', 'tag_service', 'local_deals', 'ten_visits', 'refer_friends')
    search_fields = ['name', 'address', 'phones', ]
    inlines = [
        AdminSubscriptionInline,
        AdminImageBusinessInline,
        AdminCuponBusinessInline,
        AdminTenVists,
        AdminMenuBusiness,
        AdminScheduleBusiness
    ]
    prepopulated_fields = {'url_name': ('name', )}


class AdminPromo(admin.ModelAdmin):
    prepopulated_fields = {'url_name': ('name', )}


class AdminLandingEvent(admin.TabularInline):
    model = LandingEvent
    extra = 1


class AdminBusinessEvent(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('http://code.jquery.com/ui/1.9.1/themes/base/jquery-ui.css',)
        }

        js = (
            'http://code.jquery.com/jquery-1.8.2.js',
            'http://code.jquery.com/ui/1.9.1/jquery-ui.js',
            'http://maps.google.com/maps/api/js?sensor=true&language=en',
            '%scommunity/js/location.js' % settings.STATIC_URL,
        )

    fieldsets = (
        (None, {
            'fields': (
                ('business', 'active', ),
                ('title', 'date_begin', 'date_end'), 'geo', 'address', 'facebook', 'twitter', 'google_plus',
                'description', 'phone'
            )
        }),

    )

    inlines = [AdminImageBusinessEventInline, AdminLandingEvent]
    list_display = ('title', 'business', 'date_begin', 'date_end')
    list_filter = ('business__community',)


class AdminNewsletter(admin.ModelAdmin):
    actions = [export_as_csv]


admin.site.register(LandingPartner, AdminLandingPage)
admin.site.register(BusinessEvent, AdminBusinessEvent)
admin.site.register(Service, AdminService)
admin.site.register(Category)
admin.site.register(Community, AdminCommunity)
admin.site.register(Partner, AdminPartner)
admin.site.register(Business, AdminBusiness)
admin.site.register(Review)
admin.site.register(ContactCard)
admin.site.register(Card)
admin.site.register(NewsletterSuscription, AdminNewsletter)
admin.site.register(Usuario)
admin.site.register(FeedbackBusiness)
admin.site.register(Bookmark)
admin.site.register(PromoPartner, AdminPromo)
#unregister sites
#admin.site.unregister(Site)