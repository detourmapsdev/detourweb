import urlparse
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from localflavor.us.models import PhoneNumberField
from community.models import Community
from community.widgets import TextEditorWidget


class EditorField(models.TextField):
    def __init__(self, thumb=None, *args, **kwargs):
        self._thumb = thumb
        print self._thumb
        super(EditorField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs['widget'] = TextEditorWidget
        return super(EditorField, self).formfield(**kwargs)


class RegisterUser(models.Model):
    firstname = models.CharField(max_length=48, blank=True, null=True)
    lastname = models.CharField(max_length=48, blank=True, null=True)
    address = models.CharField(max_length=72, blank=True, null=True)
    city = models.CharField(max_length=36, blank=True, null=True)
    state = models.CharField(max_length=45, blank=True, null=True)
    zip_code = models.CharField(max_length=5, blank=True)
    phone = models.CharField(max_length=12, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    cell = models.CharField(max_length=12, blank=True)
    website = models.URLField(blank=True, null=True)
    active = models.BooleanField(default=False)
    suscribe = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Form Register User'
        verbose_name_plural = 'Form Register User'

    def __unicode__(self):
        return '%s %s' % (self.firstname, self.lastname)


class RegisterBusiness(models.Model):
    name = models.CharField(max_length=48)
    address = models.CharField(max_length=72)
    city = models.CharField(max_length=36)
    state = models.CharField(max_length=45, blank=True, null=True)
    owner = models.CharField(max_length=36)
    zip_code = models.CharField(max_length=5, blank=True)
    contact = models.CharField(max_length=36)
    phone = models.CharField(max_length=12)
    email = models.EmailField()
    cell = models.CharField(max_length=12, blank=True)
    website = models.URLField(blank=True)
    active = models.BooleanField(default=False)
    id_biz = models.IntegerField(max_length=12, blank=True)

    class Meta:
        verbose_name = 'Form Register Business'
        verbose_name_plural = 'Form Register Businesses'

    def __unicode__(self):
        return '%s' % self.name

    def urlbusines_admin(self):
        if self.id_biz:
            return u'<a href="/admin/community/business/%s/">/admin/community/business/%s/</a>' % (
                self.id_biz, self.id_biz)
        else:
            return u'<p>None Business</p>'

    urlbusines_admin.allow_tags = True
    urlbusines_admin.short_description = 'URL Business'


class CategoryRegisterBusiness(models.Model):
    id_cat = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=36, blank=True, null=True)
    register_business = models.ForeignKey(RegisterBusiness, blank=True, null=True)

    class Meta:
        verbose_name = 'Category for Register Business'
        verbose_name_plural = 'Category for Register Businesses'

    def __unicode__(self):
        return '%s' % self.name


class MarketingTypes(models.Model):
    name = models.CharField(max_length=45, blank=True, null=True)
    register_business = models.ForeignKey(RegisterBusiness, blank=True, null=True)

    class Meta:
        verbose_name = 'Marketing Types for Register Business'
        verbose_name_plural = 'Marketing for Register Businesses'

    def __unicode__(self):
        return '%s' % self.name


class MarketingTactics(models.Model):
    name = models.CharField(max_length=45, blank=True, null=True)
    register_business = models.ForeignKey(RegisterBusiness, blank=True, null=True)

    class Meta:
        verbose_name = 'Marketing Tactics for Register Business'
        verbose_name_plural = 'Marketing Tactics for Register Businesses'

    def __unicode__(self):
        return '%s' % self.name


class ConductMarketing(models.Model):
    name = models.CharField(max_length=45, blank=True, null=True)
    register_business = models.ForeignKey(RegisterBusiness, blank=True, null=True)

    class Meta:
        verbose_name = 'Conduct Marketing for Register Business'
        verbose_name_plural = 'Conduct Marketing for Register Businesses'

    def __unicode__(self):
        return '%s' % self.name


class FrecuencyMarketing(models.Model):
    name = models.CharField(max_length=45, blank=True, null=True)
    register_business = models.ForeignKey(RegisterBusiness, blank=True, null=True)

    class Meta:
        verbose_name = 'Frecuency Marketing for Register Business'
        verbose_name_plural = 'Frecuency Marketing for Register Businesses'

    def __unicode__(self):
        return '%s' % self.name


class MonthMarketing(models.Model):
    name = models.CharField(max_length=45, blank=True, null=True)
    register_business = models.ForeignKey(RegisterBusiness, blank=True, null=True)

    class Meta:
        verbose_name = 'Month Marketing for Register Business'
        verbose_name_plural = 'Month Marketing for Register Businesses'

    def __unicode__(self):
        return '%s' % self.name


class EmailUs(models.Model):
    CHOICES_INTERESTED = (
        ('FA', 'Free Advertising'),
        ('DA', 'DetourMaps Advertising'),
        ('SC', '$10 Savings Card'),
        ('GW', 'Graphic & Web'),
        ('MT', 'Mobile Text'),
        ('SM', 'Social Media'),
        ('EB', 'Email Blast'),
        ('CP', 'Create Promotions'),
        ('PV', 'Photo & Video'),
        ('SG', 'Suggestions')
    )
    interested = models.CharField(max_length=2, choices=CHOICES_INTERESTED)
    name_is = models.CharField(max_length=48)
    email_is = models.EmailField()
    phones_is = models.CharField(max_length=12)
    questions = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Form Email us'
        verbose_name_plural = 'Form Email us'

    def __unicode__(self):
        return '%s, %s' % (self.get_interested_display(), self.name_is)


class CouponRequestsForm(models.Model):
    name = models.CharField(max_length=60)
    cellphone = PhoneNumberField()
    email = models.EmailField()
    community = models.ForeignKey(Community, null=True)
    subscribe = models.BooleanField()

    def __unicode__(self):
        return '%s' % self.name

    class Meta:
        verbose_name = 'Form Coupon Request'
        verbose_name_plural = 'Form Coupon Request'


class Module(models.Model):
    CHOICES_TEMPLATES = (
        ('H', 'Home'),
        ('A', 'About Us'),
        ('C', 'Communities'),
        ('D', 'Deals'),
        ('R', 'Free Business listing'),
        ('P', 'Printed Maps'),
        ('I', 'Interactive Maps'),
        ('E', 'Contact'),
        ('K', 'Carrier'),
        ('L', 'Landing Pages'),
    )
    CHOICES_TYPE_MODULES = (
        ('B', 'BlockHome'),
        ('T', 'SimpleText'),
        ('C', 'ComplexText'),
        ('M', 'Testimonial'),
        ('H', 'Header'),
        ('D', 'Detail'),
        ('P', 'Purchase'),
        ('L', 'LandingText'),
        ('V', 'Video')
    )
    page = models.CharField(max_length=1, choices=CHOICES_TEMPLATES)
    type_module = models.CharField(max_length=1, choices=CHOICES_TYPE_MODULES, verbose_name='Module Type')
    quantum = models.IntegerField(max_length=1, blank=True)

    def __unicode__(self):
        return '%s, %s' % (self.get_type_module_display(), self.get_page_display())


class Page(models.Model):
    CHOICES_TEMPLATES = (
        ('H', 'Home'),
        ('A', 'About Us'),
        ('C', 'Communities'),
        ('D', 'Deals'),
        ('R', 'Free Business listing'),
        ('P', 'Printed Maps'),
        ('I', 'Interactive Maps'),
        ('E', 'Contact'),
        ('K', 'Carrier'),
        ('L', 'Landing Pages'),
    )
    name = models.CharField(max_length=24)
    url_name = models.SlugField(verbose_name='URL name', blank=True)
    is_a_root = models.BooleanField(default=False, help_text='Mark if a page is Page Home')
    published = models.BooleanField(default=False, help_text='Mark to publish')
    is_menu = models.BooleanField(default=False, verbose_name='Is a Menu?', help_text='Mark if is a principal menu')
    title = models.SlugField(blank=True)
    keywords = models.TextField(help_text='Insert words separated by commas', blank=True)
    description = models.TextField(help_text='Insert phrases that describe the page', blank=True)
    template = models.CharField(max_length=1, choices=CHOICES_TEMPLATES)

    def EditContent(self):
        link = "<a href='/admin/web/page/%s'>Edit Content</a>" % self.id
        return link

    EditContent.short_description = 'Add Content'
    EditContent.allow_tags = True

    def CMS(self):
        module_obejct = Module.objects.filter(page=self.template)
        linky = "<div>Modules"
        header = ""
        for i in module_obejct:
            linky += '<div><a href="/content/?idm=%s&idp=%s" id="%s" class="addLink" style="margin-left:8px;">Add %s</a></div>' % (
                i.type_module, self.pk, i.id, i.get_type_module_display())
        linky += "</div>"
        return linky

    CMS.short_description = 'Modules to add'
    CMS.allow_tags = True

    def HeaderBlock(self):
        header_object = Header.objects.filter(page__id=self.id)
        headers = ""
        if header_object:
            for i in header_object:
                headers += "<div><div>%s</div><div><img src='/media/%s'/></div></div>" % (i.title, i.image)
        else:
            headers = "<div>Template without Header</div>"
        return headers

    HeaderBlock.short_description = "Headers"
    HeaderBlock.allow_tags = True

    def TextBlock(self):
        block_object = BlockHome.objects.filter(page=self)
        blocker = ""
        if block_object:
            for i in block_object:
                if i.has_image:
                    blocker += "<div><div>Image</div><div><img src='/media/%s'/></div></div>" % (i.image)
                else:
                    blocker += '<div><div>%s</div><div><object width="300" height="200"><param name="movie" value="%s"/><param name="wmode" value="transparent"/><embed src="%s" type="application/x-shockwave-flash" wmode="transparent" width="300" height="200"/></object></div></div>' % (
                        'Video', i.video, i.video)
        else:
            blocker += "Template without Block Home"
        return blocker

    TextBlock.short_description = "Block Home"
    TextBlock.allow_tags = True

    def Text(self):
        text_object = SimpleText.objects.filter(page=self)
        texter = ""
        if text_object:
            for i in text_object:
                texter += "<div>%s</div>" % i.text
        else:
            texter += "Template without a Simple Text"
        return texter

    Text.short_description = "Simple text"
    Text.allow_tags = True

    def ComplexHome(self):
        complextext_objects = ComplexText.objects.filter(page=self)
        complexer = ""
        if complextext_objects:
            for i in complextext_objects:
                complexer += "<div><div>Title : %s</div><div>Text : %s</div></div>" % (i.title, i.text)
        else:
            complexer += "Template without a Complex Text"
        return complexer

    ComplexHome.short_description = "Complex Text Block"
    ComplexHome.allow_tags = True

    def TestimonialBlock(self):
        testimonial_object = Testimonial.objects.filter(page=self)
        testimonialer = ""
        if testimonial_object:
            for i in testimonial_object:
                testimonialer += "<div><div>Title : %s</div><div>Text : %s</div><div>Name : %s</div><div>Position : %s</div><div>Logo : <img src='/media/%s'/></div></div>" % (
                    i.title, i.text, i.name, i.position, i.logo)
        else:
            testimonialer += "Template without Testimonials"
        return testimonialer

    TestimonialBlock.short_description = 'Testimonials'
    TestimonialBlock.allow_tags = True


    def __unicode__(self):
        return '%s' % self.name


class SimpleText(models.Model):
    text = models.TextField()
    page = models.ForeignKey(Page, blank=True)

    class Meta:
        verbose_name = 'Simple Text'
        verbose_name_plural = 'Simple Texts'

    def __unicode__(self):
        return '%s' % self.text


class ComplexText(models.Model):
    title = models.CharField(max_length=90)
    text = models.TextField()
    page = models.ForeignKey(Page, blank=True)

    class Meta:
        verbose_name = 'Complex Text'
        verbose_name_plural = 'Complex Texts'

    def __unicode__(self):
        return '%s' % self.title


class Testimonial(models.Model):
    title = models.CharField(max_length=90, blank=True)
    text = models.TextField()
    name = models.CharField(max_length=24)
    position = models.CharField(max_length=24)
    logo = models.ImageField(upload_to='logoTestimonials')
    page = models.ForeignKey(Page, blank=True)

    def __unicode__(self):
        return '%s' % self.title


class BlockHome(models.Model):
    has_image = models.BooleanField(default=False, help_text='Mark if the block has a image')
    title = models.CharField(max_length=48, blank=True)
    image = models.ImageField(upload_to='imageBlock', blank=True)
    link = models.CharField(max_length=24, blank=True)
    has_video = models.BooleanField(default=False, help_text='Mark if the block has a video')
    video = models.URLField(blank=True)
    page = models.ForeignKey(Page, blank=True)

    def __unicode__(self):
        return '%s' % self.title


class LandingPage(models.Model):
    community = models.ForeignKey(Community)

    def __unicode__(self):
        return u'Landing page: %s' % self.community.name


class LandingSocial(models.Model):
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
    landing_page = models.ForeignKey(LandingPage)

    def __unicode__(self):
        return '%s, %s - %s' % (self.landing_page.community.name, self.get_type_social_display(), self.url)

    class Meta:
        verbose_name = 'Social for Landing'


class LandingText(models.Model):
    image = models.ImageField(upload_to='ImageLanding')
    title = models.CharField(max_length=45)
    text = models.TextField()
    landing_page = models.ForeignKey(LandingPage, blank=True)

    def __unicode__(self):
        return u'%s' % self.title


class Video(models.Model):
    url_video = models.URLField()
    text = models.TextField()
    landing_page = models.ForeignKey(LandingPage, blank=True)

    def __unicode__(self):
        return u'%s' % self.url_video

    def parseId(self):
        url_data = urlparse.urlparse(self.url_video)
        query = urlparse.parse_qs(url_data.query)
        video = query["v"][0]
        return video


class PhoneNumber(models.Model):
    text = models.TextField()
    landing_page = models.ForeignKey(LandingPage, blank=True)

    def __unicode__(self):
        return u'Numbers from: %s' % self.landing_page.community.name


class HeaderPage(models.Model):
    caption = models.TextField(blank=True)
    image = models.ImageField(upload_to='imageHeader')
    landing_page = models.ForeignKey(LandingPage, blank=True)

    def __unicode__(self):
        return '%s' % self.caption


class Header(models.Model):
    caption = models.TextField(blank=True)
    image = models.ImageField(upload_to='imageHeader')
    page = models.ForeignKey(Page, blank=True)

    def __unicode__(self):
        return '%s' % self.caption


class Detail(models.Model):
    image = models.ImageField(upload_to='detailDeal')
    text = models.TextField()
    page = models.ForeignKey(Page, blank=True)

    def __unicode__(self):
        return '%s' % self.text


class Purchase(models.Model):
    text = models.TextField()
    page = models.ForeignKey(Page, blank=True)

    def __unicode__(self):
        return '%s' % self.text


class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User)

    # Other fields here
    password_token = models.CharField(max_length=8)

    def __unicode__(self):
        return '%s' % self.password_token


class PrintMaps(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True, verbose_name='Title')
    description = models.TextField(blank=True, verbose_name='Description')
    maps_customize = models.TextField(blank=True, verbose_name='Customize HTML')
    CHOICES_IMG_SRC = (
        ('MC', 'Maps Customize'),
        ('MS', 'Maps Standard')
    )
    type_img_src = models.CharField(max_length=2, choices=CHOICES_IMG_SRC, default='MS')

    class Meta:
        verbose_name = 'Print Map'
        verbose_name_plural = 'Print Maps'

    def __unicode__(self):
        return u'%s' % self.title


class ImagesPrintMaps(models.Model):
    print_maps = models.ForeignKey(PrintMaps)
    img = models.ImageField(upload_to='printMaps')


class PostCategory(models.Model):
    name = models.CharField(max_length=45)
    url_name = models.SlugField()

    def __unicode__(self):
        return '%s' % self.name


class Post(models.Model):
    name = models.CharField(max_length=90)
    sub_title = models.CharField(max_length=120, blank=True, null=True)
    url_name = models.SlugField()
    principal_image = models.ImageField(upload_to='posts')
    category = models.ForeignKey(PostCategory)
    content = EditorField(verbose_name=u'Content', blank=True, null=True)
    date = models.DateField()
    user = models.ForeignKey(User)
    active = models.BooleanField(default=False)
    is_advertise = models.BooleanField(default=False)
    is_outstanding = models.BooleanField(default=False

    )
    reblog = models.BooleanField(default=False)

    def __unicode__(self):
        return '%s, %s' % (self.name, self.date)


class ImagenEditor(models.Model):
    imagen = models.ImageField(upload_to='editor')

    def __unicode__(self):
        return '%s' % self.imagen

    class Meta:
        verbose_name = 'Image of the editor'
        verbose_name_plural = 'Images of the editor'


class Newsletter(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __unicode__(self):
        return '%s' % self.email
