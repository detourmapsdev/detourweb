# -*- coding: utf-8 -*-
import base64
import urlparse
import urllib
import simplejson
#from django.db import models
from django.contrib.formtools.tests.forms import HashTestBlankForm
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point, fromstr, GEOSGeometry
from localflavor.us.models import USPostalCodeField
from django.template.defaultfilters import slugify
from community.fields import ColorField
from community.widgets import TextEditorWidget
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from web.short_url import encode_url, decode_url


def parseSpecialChar(value):
    value_lower = value.lower()
    special = ['@', '#', '$', '%', '&', ' ', '/', "'"]
    special1 = [u'ñ', u'á', u'é', u'í', u'ó', u'ú']
    lista = ""
    for i in value_lower:
        if i in special:
            lista += "-"
        elif i in special1:
            if i == u"ñ":
                lista += "n"
            elif i == u"á":
                lista += "a"
            elif i == u"é":
                lista += "e"
            elif i == u"í":
                lista += "i"
            elif i == u"ó":
                lista += "o"
            else:
                lista += "u"
        else:
            lista += i
    return lista


class EditorField(models.TextField):
    def __init__(self, thumb=None, *args, **kwargs):
        self._thumb = thumb
        print self._thumb
        super(EditorField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs['widget'] = TextEditorWidget
        return super(EditorField, self).formfield(**kwargs)


class Usuario(models.Model):
    user = models.ForeignKey(User, null=True)
    tipo_usuario = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return '%s' % self.user

    class Meta:
        ordering = ('id',)


class TipoUsuario(models.Model):
    """
    tabla para el manejo de login y registro multiple
    """
    usuario = models.ForeignKey(Usuario, blank=True, null=True)
    access_token = models.CharField(max_length=255, unique=True)
    expires = models.IntegerField(null=True)
    userid = models.CharField(max_length=200, unique=True, null=True)
    session_key = models.CharField(max_length=255, blank=True, null=True)

    def query(self):
        """
        operacion para obtener uid and time expires
        """
        url = 'https://graph.facebook.com/me?access_token=%s' \
              % self.access_token
        response = simplejson.load(urllib.urlopen(url))
        return response


class Image(models.Model):
    name = models.CharField(max_length=60, blank=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return u'%s, %s' % (self.name, self.img)


class CommunityParent(models.Model):
    name = models.CharField(max_length=60)
    description = models.TextField(blank=True)
    keywords = models.CharField(max_length=150, blank=True, null=True)
    history = models.TextField(blank=True)

    class Meta:
        abstract = True


class City(CommunityParent):
    objects = models.GeoManager()

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        verbose_name_plural = u'cities'


class Community(CommunityParent):
    url_name = models.CharField(max_length=60, verbose_name='URL Name', blank=True)
    borders = models.MultiPolygonField()
    objects = models.GeoManager()
    zipcode = USPostalCodeField()
    active = models.BooleanField(default=False)
    #discover
    discover_html = models.TextField(blank=True)
    discover_css = models.TextField(blank=True, verbose_name='Discover CSS')
    has_css_file = models.BooleanField(default=False, verbose_name='Upload CSS file')
    css_file = models.FileField(upload_to='discover', blank=True, verbose_name='Discover CSS file')
    active_savings = models.BooleanField(default=False)
    printed_map = models.FileField(upload_to='printed', verbose_name='Printed Map', help_text='PDF format')
    img_printed_map = models.FileField(upload_to='img_printed', verbose_name='Image Printed Map', help_text='Image Format')

    def __unicode__(self):
        return u'%s' % self.name

    def get_absolute_url(self):
        if self.url_name:
            return '/communities/%s/map/' % (
                self.url_name)
        else:
            return ''

    class Meta:
        verbose_name_plural = 'communities'
        ordering = ['name', ]


class ImageCommunity(Image):
    img = models.ImageField(upload_to='community')
    community = models.ForeignKey(Community)


class CommunitySnapshot(models.Model):
    rich_text = EditorField()
    community = models.ForeignKey(Community)

    def __unicode__(self):
        return 'Ssnaphot for: %s' % self.community.name

    class Meta:
        verbose_name = 'Community Snapshot'
        verbose_name_plural = 'Communities Snapshot'


class NewDiscover(Image):
    caption = models.TextField(blank=True, null=True)
    img = models.ImageField(upload_to='community')
    community = models.ForeignKey(Community)


class PhoneNumber(models.Model):
    text = models.TextField()
    landing_page = models.ForeignKey(Community, blank=True)

    def __unicode__(self):
        return u'Numbers from: %s' % self.landing_page.name


class CommunitySocial(models.Model):
    CHOICES_TYPE = (
        ('F', 'Facebook'),
        ('T', 'Twitter'),
        ('Y', 'Youtube'),
        ('K', 'Flicker'),
        ('W', 'Web'),
        ('P', 'Pinterest'),
        ('U', 'Tumblr'),
        ('V', 'Vimeo'),
        ('I', 'Linkedin'),
        ('M', 'MySpace'),
        ('H', 'Yahoo'),
        ('G', 'Google+')
    )
    type_social = models.CharField(max_length=1, choices=CHOICES_TYPE, verbose_name='Social Network')
    url = models.URLField()
    community = models.ForeignKey(Community)

    def __unicode__(self):
        return '%s, %s - %s' % (self.community.name, self.get_type_social_display(), self.url)

    class Meta:
        verbose_name = 'Social for Community'


class CommunityText(models.Model):
    image = models.ImageField(upload_to='ImageLanding')
    title = models.CharField(max_length=45)
    text = models.TextField()
    community = models.ForeignKey(Community, blank=True)

    def __unicode__(self):
        return u'%s' % self.title


class Video(models.Model):
    url_video = models.URLField()
    text = models.TextField()
    community = models.ForeignKey(Community, blank=True)

    def __unicode__(self):
        return u'%s' % self.url_video

    def parseId(self):
        url_data = urlparse.urlparse(self.url_video)
        query = urlparse.parse_qs(url_data.query)
        video = query["v"][0]
        return video


class HeaderCommunity(models.Model):
    caption = models.TextField(blank=True)
    image = models.ImageField(upload_to='imageHeader')
    community = models.ForeignKey(Community, blank=True)

    def __unicode__(self):
        return '%s' % self.caption


class Service(models.Model):
    name = models.CharField(max_length=60)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to='serviceicons')
    color = ColorField(default='000000')
    subcat = models.BooleanField(default=False, help_text='Check if this will work as a subcategory')

    def __unicode__(self):
        n = u'%s'
        if self.subcat:
            n = u'[ %s ]'
        return n % self.name

    def serviceSlug(self):
        return slugify(self.name)

    class Meta:
        verbose_name = 'tag'
        verbose_name_plural = 'tags'
        ordering = ['name']


class Category(models.Model):
    name = models.CharField(max_length=60)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to='categoryicons')
    color = ColorField(default='000000')

    class Meta:
        verbose_name_plural = 'categories'

    def __unicode__(self):
        return u'%s' % self.name

    def urlCat(self):
        return u'%s' % base64.urlsafe_b64encode(str(self.id))

    def categorySlug(self):
        return slugify(self.name)


class Business(CommunityParent):
    url_name = models.SlugField(blank=True, null=True)
    community = models.ForeignKey(Community, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    belongs2community = models.BooleanField(default=False, verbose_name='Belongs to the community?')
    chamber_member = models.BooleanField(default=False, verbose_name='Member of the Chamber of Commerce?')
    full_version = models.BooleanField(default=False, verbose_name='Full Version')
    geo = models.PointField()
    address = models.CharField(max_length=120, help_text='Example:1600 Amphitheatre Parkway, Mountain View, CA',
                               blank=True)
    phones = models.CharField(max_length=60, blank=True, help_text='List of phones separated for commas')
    site = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    tag_service = models.ManyToManyField(Service, verbose_name='Tags', blank=True)
    enable_comments = models.BooleanField(default=True)
    date_end = models.DateField(verbose_name='End Date', auto_now=True)
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    #gplus = models.URLField(blank=True)
    video = models.URLField(blank=True)
    #video_embedded = models.TextField(max_length=1000, blank=True, help_text='Introduce the embedded code of video (size:220x195).')
    video_description = models.TextField(max_length=500, blank=True)
    logo = models.ImageField(verbose_name='Logo', upload_to='business', null=True, blank=True)
    objects = models.GeoManager()
    rate_interval = models.IntegerField(max_length=3, blank=False, null=False, default=15,
                                        verbose_name='Interval for business ratting.')
    auth_code = models.CharField(max_length=60, blank=True, null=True)
    #choices local deals
    CHOICES_DEALS = (
        ('N', 'None'),
        ('T', '$30 spend'),
        ('F', '$40 spend'),
        ('Q', '$50 spend')
    )
    local_deals = models.CharField(verbose_name='Local Deals', max_length=1, blank=True, choices=CHOICES_DEALS)
    ten_visits = models.BooleanField(default=False, verbose_name=u'Ten Visits')
    refer_friends = models.BooleanField(default=False, verbose_name=u'Refer Friends')

    def getRateInterval(self, business_id):
        return self.objects.get(id=business_id).rate_interval

    def parseId(self):
        if self.video:
            url_data = urlparse.urlparse(self.video)
            query = urlparse.parse_qs(url_data.query)
            video = query["v"][0]
            return video

    def EntryDetails(self):
        """
        obtener los detalles de un video con el gdata API para el manejo de datos de google
        """
        if self.video:
            url_data = urlparse.urlparse(self.video)
            query = urlparse.parse_qs(url_data.query)
            video_id = query["v"][0]
            import gdata.youtube
            import gdata.youtube.service

            yt_service = gdata.youtube.service.YouTubeService()
            entry = yt_service.GetYouTubeVideoEntry(video_id=video_id)
            return entry
        else:
            return False

    class Meta:
        verbose_name_plural = 'businesses'
        ordering = ['name']

    def __unicode__(self):
        return '%s' % self.name

    def urlBiz(self):
        url = parseSpecialChar(self.name) + "/" + base64.urlsafe_b64encode(str(self.id))
        return url

    def get_absolute_url(self):
        if self.url_name:
            if self.community:
                return '/communities/%s/map/business/?name=%s&auth_code=%s&tab=info' % (
                    self.community.url_name, self.url_name, encode_url(self.id, 8))
            else:
                return ''

    def getUniqueCode(self):
        return encode_url(self.id, 8)

    def serviceAll(self):
        attr = ""
        services = self.tag_service.all().filter(subcat=False)
        for x in range(services.count()):
            if x == services.count() - 1:
                attr += slugify(services[x].name)
            else:
                attr += slugify(services[x].name) + " "
        return attr


class Partner(CommunityParent):
    url_name = models.SlugField(blank=True, null=True)
    logo = models.ImageField(upload_to='logopartner', blank=True, null=True)
    community = models.ForeignKey(Community)
    geo = models.MultiLineStringField()
    objects = models.GeoManager()
    business = models.ManyToManyField(Business, blank=True, null=True, symmetrical=False)
    pop = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Partners'

    def __unicode__(self):
        return u'%s' % self.name

    def get_absolute_url(self):
        return '/communities/%s/partners/?name=%s' % (self.community.url_name, self.url_name)


class PartnerMobile(models.Model):
    principal_logo = models.ImageField(upload_to='m-principal')
    sponsor_logo = models.ImageField(upload_to='m-sponsor')
    communities = models.ManyToManyField(Community, blank=True, null=True)
    partner_parent = models.ForeignKey(Partner)


class LandingPartner(models.Model):
    partner_parent = models.ForeignKey(Partner)

    class Meta:
        verbose_name = 'Landing Partner'
        verbose_name_plural = 'Landing partners'

    def __unicode__(self):
        return self.partner_parent.name


class LandingSocialPartner(models.Model):
    CHOICES_TYPE = (
        ('F', 'Facebook'),
        ('T', 'Twitter'),
        ('Y', 'Youtube'),
        ('K', 'Flicker'),
        ('W', 'Web'),
        ('P', 'Pinterest'),
        ('U', 'Tumblr'),
        ('V', 'Vimeo'),
        ('I', 'Linkedin'),
        ('M', 'MySpace'),
        ('H', 'Yahoo'),
        ('G', 'Google+')
    )
    type_social = models.CharField(max_length=1, choices=CHOICES_TYPE, verbose_name='Social Network')
    url = models.URLField()
    landing_page = models.ForeignKey(LandingPartner)

    def __unicode__(self):
        return '%s, %s - %s' % (self.landing_page.partner_parent.name, self.get_type_social_display(), self.url)

    class Meta:
        verbose_name = 'Social for Landing'


class LandingTextPartner(models.Model):
    image = models.ImageField(upload_to='ImageLanding')
    title = models.CharField(max_length=45)
    text = EditorField()
    landing_page = models.ForeignKey(LandingPartner, blank=True)

    def __unicode__(self):
        return u'%s' % self.title


class VideoPartner(models.Model):
    url_video = models.URLField()
    text = models.TextField()
    landing_page = models.ForeignKey(LandingPartner, blank=True)

    def __unicode__(self):
        return u'%s' % self.url_video

    def parseId(self):
        url_data = urlparse.urlparse(self.url_video)
        query = urlparse.parse_qs(url_data.query)
        video = query["v"][0]
        return video


class HeaderPagePartner(models.Model):
    caption = models.TextField(blank=True)
    image = models.ImageField(upload_to='imageHeader')
    landing_page = models.ForeignKey(LandingPartner, blank=True)

    def __unicode__(self):
        return '%s' % self.caption


class HelpingShop(models.Model):
    text = models.TextField()
    name_coupon_book = models.CharField(max_length=45)
    coupon_book = models.FileField(upload_to='coupon_book', blank=True, null=True)
    name_print_map = models.CharField(max_length=45)
    print_map = models.FileField(upload_to='printed_map', blank=True, null=True)
    landing_page = models.ForeignKey(LandingPartner, blank=True)

    def __unicode__(self):
        return '%s' % self.text


class PromoPartner(models.Model):
    name = models.CharField(max_length=36)
    url_name = models.SlugField()
    description = models.TextField()
    image = models.ImageField(upload_to='promo')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    partner = models.ForeignKey(Partner)

    def __unicode__(self):
        return '%s' % self.name


class BusinessEvent(models.Model):
    business = models.ForeignKey(Business)
    geo = models.PointField(blank=True, null=True)
    address = models.CharField(max_length=120, help_text='Example:1600 Amphitheatre Parkway, Mountain View, CA',
                               blank=True)
    objects = models.GeoManager()

    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    google_plus = models.URLField(blank=True)

    title = models.CharField(max_length=150, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=120, blank=True, null=True)
    date_begin = models.DateField(auto_now=False, verbose_name='Begin date for the Event.', blank=True, null=True)
    date_end = models.DateField(auto_now=False, verbose_name='End date for the Event.', blank=True, null=True)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return '%s - (%s)' % (self.title, self.date_begin.strftime('%m-%d-%Y'))

    def get_absolute_url(self):
        return '/communities/%s/map/#!/event/%s' % (
            self.business.community.url_name, base64.urlsafe_b64encode(str(self.id)))

    def get_landing_event(self):
        return '/communities/get/event?auth_code=%s' % encode_url(self.id, min_length=8)

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ['-date_begin']


class BusinessEventPartner(models.Model):
    business = models.ForeignKey(Business, blank=True, null=True)
    partner = models.ForeignKey(Partner, blank=True, null=True)
    geo = models.PointField(blank=True, null=True)
    address = models.CharField(max_length=120, help_text='Example:1600 Amphitheatre Parkway, Mountain View, CA',
                               blank=True)
    objects = models.GeoManager()

    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    google_plus = models.URLField(blank=True)

    title = models.CharField(max_length=150, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=120, blank=True, null=True)
    date_begin = models.DateField(auto_now=False, verbose_name='Begin date for the Event.', blank=True, null=True)
    date_end = models.DateField(auto_now=False, verbose_name='End date for the Event.', blank=True, null=True)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return '%s - (%s)' % (self.title, self.date_begin.strftime('%m-%d-%Y'))

    def get_absolute_url(self):
        return '/communities/%s/map/#!/event/%s' % (
            self.business.community.url_name, base64.urlsafe_b64encode(str(self.id)))

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ['-date_begin']


class ImageBusinessEvents(Image):
    img = models.ImageField(upload_to='businessEvent')
    business_event = models.ForeignKey(BusinessEvent)


class LandingEvent(models.Model):
    business_event = models.ForeignKey(BusinessEvent)
    video = models.URLField()
    website = models.URLField()
    email = models.EmailField()

    def __unicode__(self):
        return '%s' % self.business_event.title


class ImageBusinessEventsPartner(Image):
    img = models.ImageField(upload_to='businessEvent')
    business_event = models.ForeignKey(BusinessEventPartner)


class CuponBusiness(Image):
    img = models.ImageField(upload_to='business')
    coupon = models.ImageField(upload_to='cupones')
    business = models.ForeignKey(Business)
    active = models.BooleanField(default=False)
    start_date = models.DateField()
    end_date = models.DateField()


class TenVisitsBusiness(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='ten_visits')
    business = models.ForeignKey(Business)
    active = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Ten Visits'
        verbose_name_plural = 'Ten Visits'


class ImageBusiness(Image):
    img = models.ImageField(upload_to='business')
    business = models.ForeignKey(Business)


class BusinessMenu(models.Model):
    menu = EditorField(verbose_name=u'Menu', blank=True, null=True)
    business = models.ForeignKey(Business)

    def __unicode__(self):
        return u'%s, %s' % (self.business, self.menu)

    class Meta:
        verbose_name_plural = 'Menu for Business'


class BusinessSchedule(models.Model):
    schedule = models.TextField()
    business = models.ForeignKey(Business)

    def __unicode__(self):
        return u'%s, %s' % (self.business, self.schedule)

    class Meta:
        verbose_name_plural = "Business's schedule"


class Subscription(models.Model):
    business = models.ForeignKey(Business)
    date_start = models.DateField(verbose_name='Start Date')
    date_end = models.DateField(verbose_name='End Date')
    auto_renew = models.BooleanField(default=False, verbose_name='Auto Renew?')
    autorenewed = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)

    def __unicode__(self):
        return u'Start:%s - End:%s' % (self.date_start, self.date_end)


class ContactCard(models.Model):
    user = models.ForeignKey(Usuario)
    business = models.ForeignKey(Business)

    def __unicode__(self):
        return '%s' % self.user.user.email


class Card(models.Model):
    CHOICES_MODE = (
        ('D', 'Download'),
        ('E', 'Email'),
        ('P', 'Print')
    )
    contact_card = models.ForeignKey(ContactCard)
    name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    date = models.DateField(auto_now=True)
    until_date = models.DateTimeField(default=datetime.now() + timedelta(days=30))
    used = models.BooleanField(default=False)
    mode = models.CharField(max_length=1, choices=CHOICES_MODE)

    def __unicode__(self):
        return '%s, %s' % (self.contact_card.user.user.email, self.used)

    def getCode(self):
        return '%s' % encode_url(self.id)


class Review(models.Model):
    user = models.ForeignKey(User, editable=False)
    business = models.ForeignKey(Business, editable=False)
    date = models.DateField(auto_now=True)
    comment = models.TextField(blank=True, null=True)
    stars = models.IntegerField(null=False, blank=False)
    enable = models.BooleanField(default=True)

    class Meta:
        ordering = ['date', 'business']

    def getLastRate(self, business_id=None, user=None):
        if business_id is not None and user is not None:
            business = Business.objects.get(id=business_id)
            return self.objects.order_by('date').filter(business=business, user=user)[0].date
        else:
            return None

    def __unicode__(self):
        return u'%s' % self.business


class NewsletterSuscription(models.Model):
    CHOICES_GENDER = (
        ('M', 'Male'),
        ('F', 'Female')
    )
    email = models.EmailField()
    first_name = models.CharField(max_length=90, blank=True, null=True)
    last_name = models.CharField(max_length=90, blank=True, null=True)
    interested_in = models.CharField(max_length=120, blank=True, null=True)
    age = models.DateField(auto_now=False, blank=True, null=True)
    gender = models.CharField(max_length=1, blank=True, null=True, choices=CHOICES_GENDER)
    address = models.CharField(max_length=160, blank=True, null=True)
    phone = models.CharField(max_length=160, blank=True, null=True)
    business = models.ForeignKey(Business)

    def __unicode__(self):
        return '%s' % self.email

    class Meta:
        verbose_name = 'Suscritpion to Newsletter'
        verbose_name = 'Suscriptions to Newsletter'


class Bookmark(models.Model):
    biz = models.ForeignKey(Business, blank=True, null=True)
    user = models.ForeignKey(Usuario, blank=True, null=True)
    tab = models.CharField(max_length=12, blank=True, null=True)
    subtab = models.CharField(max_length=12, blank=True, null=True)
    datetime = models.DateTimeField(auto_now=True)
    coupon = models.ForeignKey(CuponBusiness, blank=True, null=True)

    def __unicode__(self):
        if self.biz:
            return '%s' % self.biz.name
        if self.coupon:
            return '%s' % self.coupon.business.name


class FeedbackBusiness(models.Model):
    CHOICES_DEAL = (
        ('T', '$10 Off'),
        ('S', 'Smart Buys'),
        ('V', 'Ten Visits'),
        ('R', 'Refer Friends')
    )
    business = models.ForeignKey(Business)
    user = models.ForeignKey(Usuario)
    deal = models.CharField(max_length=1, choices=CHOICES_DEAL)
    date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '%s, %s - %s' % (self.business, self.user.user.username, self.get_deal_display())


class TenVisitsRecord(models.Model):
    user = models.ForeignKey(User)
    business = models.ForeignKey(Business)
    state = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s - %s' % (self.user, self.business)

    class Meta:
        order_with_respect_to = 'user'


class TenVisitsManage(models.Model):
    ten = models.ForeignKey(TenVisitsRecord)
    receipt_number = models.CharField(max_length=16)
    date = models.DateField()
    employee = models.CharField(max_length=200, blank=True, null=True)
    number = models.IntegerField()

    class Meta:
        order_with_respect_to = 'ten'

    def __unicode__(self):
        return u'%s - %s' % (self.ten, self.number)


class ReferFriendsRecord(models.Model):
    user = models.ForeignKey(User)
    business = models.ForeignKey(Business)
    state = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s - %s' % (self.user, self.business)

    class Meta:
        order_with_respect_to = 'user'


class ReferFriendsManage(models.Model):
    refer = models.ForeignKey(ReferFriendsRecord)
    email_friend = models.EmailField()
    date = models.DateField()
    message = models.TextField(blank=True, null=True)
    number = models.IntegerField()

    class Meta:
        order_with_respect_to = 'refer'

    def __unicode__(self):
        return u'%s - %s' % (self.refer, self.number)


class ImagenEditor(models.Model):
    imagen = models.ImageField(upload_to='editor')

    def __unicode__(self):
        return '%s' % self.imagen

    class Meta:
        verbose_name = 'Menu Image'
        verbose_name_plural = u'Menu Images'

