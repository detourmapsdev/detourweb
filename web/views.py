import Image, ImageDraw, ImageFont, time, hashlib, re
import datetime
from os import chdir, path

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.db.models.loading import get_model
from django.shortcuts import HttpResponse, render_to_response, get_object_or_404, redirect
from django.http import HttpResponseBadRequest
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth import authenticate, login, logout
from django.utils.encoding import force_unicode

from easy_thumbnails.files import get_thumbnailer
from community.models import Business, Community, Review, Category, Usuario, TipoUsuario, Partner, BusinessEvent, LandingPartner
from web.forms import FormRegister, FormContactUs, FormBlockHome, FormComplexText, FormHeader, FormSimpleText, FormTestimonial, FormCouponsRequest, FormApply
from web.models import RegisterBusiness, EmailUs, Page, Module, Header, SimpleText, ComplexText, Testimonial, BlockHome, CouponRequestsForm, \
    Detail, Purchase, UserProfile, RegisterUser, CategoryRegisterBusiness, MarketingTypes, MarketingTactics, ConductMarketing, \
    FrecuencyMarketing, MonthMarketing, ImagenEditor, Post
from web.short_url import encode_url, decode_url
import random
import simplejson

form_email_us = FormContactUs()


def getPasswordRandom(length=6):
    pswd = ''
    caracteres = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's', 'd',
                  'f', 'g', 'h', 'j', 'k', 'l', 'z', 'x', 'c', 'v', 'b', 'n', 'm',
                  'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', 'A', 'S', 'D',
                  'F', 'G', 'H', 'J', 'K', 'L', 'Z', 'X', 'C', 'V', 'B', 'N', 'M',
                  '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    arr_pswd = random.sample(caracteres, length)
    for i in arr_pswd:
        pswd += i
    return pswd


@csrf_protect
def renderPages(request, url_name=None):
    if not url_name:
        try:
            page_object = Page.objects.get(is_a_root=True)
        except Page.DoesNotExist:
            page_object = ""
        try:
            header_objects = Header.objects.filter(page=page_object).order_by('id')
        except Header.DoesNotExist:
            header_objects = ""
        try:
            text_objects = SimpleText.objects.filter(page=page_object)
        except SimpleText.DoesNotExist:
            text_objects = ""
        try:
            block_objects = BlockHome.objects.filter(page=page_object).order_by('-has_image')
        except BlockHome.DoesNotExist:
            block_objects = ""
        form = FormCouponsRequest()
        return render_to_response('home.html', {'email_us': form_email_us, 'coupons_form': form, 'text': text_objects,
                                                'headers': header_objects, 'blocks': block_objects},
                                  context_instance=RequestContext(request))
    else:
        page_object = Page.objects.get(url_name=url_name)
        template = ""
        if page_object.template == "A":
            template = "about.html"
            try:
                header_objects = Header.objects.filter(page=page_object)
            except Header.DoesNotExist:
                header_objects = ""
            try:
                text_objects = SimpleText.objects.filter(page=page_object)[0]
            except SimpleText.DoesNotExist:
                text_objects = ""
            try:
                testimonial_objects = Testimonial.objects.filter(page=page_object).order_by('id')
            except BlockHome.DoesNotExist:
                testimonial_objects = ""
            try:
                complex_objects = ComplexText.objects.filter(page=page_object).order_by('id')
            except BlockHome.DoesNotExist:
                complex_objects = ""
            return render_to_response(template, {'communities': Community.objects.all(), 'page': page_object,
                                                 'header': header_objects, 'text': text_objects,
                                                 'testimonials': testimonial_objects, 'complexes': complex_objects},
                                      context_instance=RequestContext(request))
        elif page_object.template == "P":
            template = "printedMaps.html"
            try:
                header_objects = Header.objects.filter(page=page_object)
            except Header.DoesNotExist:
                header_objects = ""
            try:
                text_objects = SimpleText.objects.filter(page=page_object)[0]
            except SimpleText.DoesNotExist:
                text_objects = ""
            return render_to_response(template, {'page': page_object, 'header': header_objects, 'text': text_objects},
                                      context_instance=RequestContext(request))
        elif page_object.template == "R":
            if request.method == "POST":
                template = "register.html"
                form_register = FormRegister(request.POST)
                if form_register.is_valid():
                    data = form_register.cleaned_data
                    register_object = RegisterBusiness(
                        name=data['name'],
                        address=data['address'],
                        city=data['city'],
                        owner=data['owner'],
                        contact=data['contact'],
                        phone=data['phone'],
                        email=data['email'],
                        cell=data['cell'],
                        website=data['website']
                    )
                    register_object.save()

                    subject = '[Web detourMaps] New business registration'
                    body = '<div><h3>New Business %s</h3>' % data['name']
                    for i in data.items():
                        body += '<p>%s: <b>%s</b>' % i
                    body += '</div>'
                    email = EmailMessage(
                        subject,
                        body,
                        'Register business <register@detourmaps.com>',
                        ['detourcommunitymaps@gmail.com'],
                    )
                    email.content_subtype = 'html'
                    email.send()
                    try:
                        text_objects = SimpleText.objects.filter(page=page_object)[0]
                    except SimpleText.DoesNotExist:
                        text_objects = ""
                    return render_to_response(
                        template, {
                            'form': form_register,
                            'page': page_object, 'text': text_objects,
                            'msg': "Thanks, Your Business was saved. We'll call you as soon as our staff reviews your application",
                        },
                        context_instance=RequestContext(request)
                    )
            else:
                template = "register.html"
                try:
                    text_objects = SimpleText.objects.filter(page=page_object)[0]
                except SimpleText.DoesNotExist:
                    text_objects = ""
                return render_to_response(template, {'communities': Community.objects.all(), 'page': page_object,
                                                     'text': text_objects},
                                          context_instance=RequestContext(request))
        elif page_object.template == "E":
            msg = ''
            if request.method == "POST":
                form = FormContactUs(request.POST)
                if form.is_valid():
                    interested = form.cleaned_data["interested"]
                    name_is = form.cleaned_data["name_is"]
                    email_is = form.cleaned_data["email_is"]
                    phones_is = form.cleaned_data["phones_is"]
                    questions = form.cleaned_data["questions"]
                    #Internal notification
                    email_us_objects = EmailUs(
                        interested=interested,
                        name_is=name_is,
                        email_is=email_is,
                        phones_is=phones_is,
                        questions=questions
                    )
                    email_us_objects.save()
                    subject_message_admin = "Contact from Email us form"
                    #ugly!! replace with template
                    body_subject_admin = "<div>" \
                                         "<p><b>Name :</b>%s</p>" \
                                         "<p><b>Email :</b>%s</p>" \
                                         "<p><b>Phone :</b>%s</p>" \
                                         "<p><b>Question :</b>%s</p>" \
                                         "<p><b>Interested :</b>%s</p>" \
                                         "</div>" % (name_is, email_is, phones_is, questions,
                                                     email_us_objects.get_interested_display())
                    email_message_admin = EmailMessage(
                        subject_message_admin,
                        body_subject_admin,
                        "Email Us <info@detourmaps.com>",
                        ['detourcommunitymaps@gmail.com']
                    )
                    email_message_admin.content_subtype = "html"
                    email_message_admin.send()
                    #Auto-response
                    subject_message_user = "Thanks for your comunication"
                    body_message_user = "<div>" \
                                        "<h1>DetourMaps</h1>" \
                                        "<p>Thanks for your comunication %s</p>" \
                                        "</div>" % name_is
                    email_message_user = EmailMessage(subject_message_user, body_message_user,
                                                      "Email Us<info@detourmaps.com>", [email_is])
                    email_message_user.content_subtype = "html"
                    email_message_user.send()
                    msg = "Your Information was sent"
                    return HttpResponse(msg)
            else:
                template = "contact.html"
                try:
                    text_objects = SimpleText.objects.filter(page=page_object)[0]
                except SimpleText.DoesNotExist:
                    text_objects = ""
                return render_to_response(template, {'communities': Community.objects.all(), 'page': page_object,
                                                     'text': text_objects}, context_instance=RequestContext(request))
        elif page_object.template == "D":
            template = "deals.html"
            try:
                text_objects = SimpleText.objects.filter(page=page_object)[0]
            except SimpleText.DoesNotExist:
                text_objects = ""
            try:
                complex_objects = ComplexText.objects.filter(page=page_object).order_by('id')
            except BlockHome.DoesNotExist:
                complex_objects = ""
            try:
                details_objects = Detail.objects.filter(page=page_object).order_by('id')
            except BlockHome.DoesNotExist:
                details_objects = ""
            try:
                purchase_objects = Purchase.objects.filter(page=page_object).order_by('id')
            except BlockHome.DoesNotExist:
                purchase_objects = ""
            form = FormCouponsRequest()
            return render_to_response(template, {'communities': Community.objects.all(), 'page': page_object,
                                                 'coupons_form': form, 'text': text_objects,
                                                 'complex': complex_objects, 'details': details_objects,
                                                 'purchases': purchase_objects},
                                      context_instance=RequestContext(request))
        elif page_object.template == "K":
            template = "carriers.html"
            if request.method == 'POST':
                form = FormApply(request.POST, request.FILES)
                if form.is_valid():
                    f = request.FILES['resume']
                    for chunk in f.chunks():
                        destination = open(settings.MEDIA_ROOT + 'careers/' + str(time.time()) + f.name, 'wb+')
                        destination.write(chunk)
                        destination.close()
                    subject = '[Web detourMaps] New careers apply'
                    body = '<div><h3>Career Apply</h3>'
                    for i in form.cleaned_data.items():
                        body += '<p>%s: <b>%s</b>' % i
                    body += '</div>'
                    email = EmailMessage(
                        subject,
                        body,
                        'DetourMaps<info@detourmaps.com>',
                        ['info@detourmaps.com', 'detourcommunitymaps@gmail.com', 'mauri544@gmail.com'],
                    )
                    email.attach_file(settings.MEDIA_ROOT + 'careers/' + str(time.time()) + f.name)
                    email.content_subtype = 'html'
                    email.send()
                    return HttpResponse('Thanks')
                else:
                    return HttpResponseBadRequest(
                        'There is something wrong! Sorry please email us to info@detourmaps.com')
            else:
                try:
                    complex_objects = ComplexText.objects.filter(page=page_object).order_by('id')
                except BlockHome.DoesNotExist:
                    complex_objects = ""
                form = FormApply()
                return render_to_response(template, {'page': page_object, 'complex': complex_objects, 'form': form},
                                          context_instance=RequestContext(request))
        else:
            return HttpResponse("Ok, We have a trouble!")


@csrf_protect
def registerBusiness(request):
    form_register = FormRegister()
    if request.method == "POST":
        form_register = FormRegister(request.POST)
        if form_register.is_valid():
            data = form_register.cleaned_data
            register_object = RegisterBusiness(
                name=data['name'],
                address=data['address'],
                city=data['city'],
                owner=data['owner'],
                contact=data['contact'],
                phone=data['phone'],
                email=data['email'],
                cell=data['cell'],
                website=data['website']
            )
            register_object.save()

            subject = '[Web detourMaps] New business registration'
            body = '<div><h3>New Business %s</h3>' % data['name']
            for i in data.items():
                body += '<p>%s: <b>%s</b>' % i
            body += '</div>'
            email = EmailMessage(
                subject,
                body,
                'Register business <register@detourmaps.com>',
                ['detourcommunitymaps@gmail.com', ],
            )
            email.content_subtype = 'html'
            email.send()

            return render_to_response(
                'register.html', {
                    'form': form_register,
                    'msg': "Thanks, Your Business was saved. We'll call you as soon "
                           "as our staff reviews your application",
                },
                context_instance=RequestContext(request)
            )
        else:
            return render_to_response(
                'register.html', {
                    'form': form_register,
                    'error': 'Ops! there is some wrong values...',
                    'email_us': form_email_us
                },
                context_instance=RequestContext(request)
            )
    else:
        return render_to_response('register.html', {'form': form_register, }, context_instance=RequestContext(request))


@csrf_exempt
def registerBusinessAjax(request):
    if request.method == "POST":
        register_object = RegisterBusiness(
            name=request.POST['name'],
            address=request.POST['address'],
            city=request.POST['city'],
            state=request.POST['state'],
            zip_code=request.POST['zip'],
            owner=request.POST['owner'],
            contact=request.POST['owner'],
            phone=request.POST['phone'],
            email=request.POST['email'],
            cell=request.POST['cell'],
            website=request.POST['website']
        )
        register_object.save()
        try:
            category_object = Category.objects.get(id=request.POST["category"])
            cat_register = CategoryRegisterBusiness(id_cat=category_object.pk, name=category_object.name,
                                                    register_business=register_object)
            cat_register.save()
        except Category.DoesNotExist:
            cat_object = CategoryRegisterBusiness(name=request.POST["category"], register_business=register_object)
            cat_object.save()
        types_objects_array = request.POST["types"]
        tactics_objects_array = request.POST["tactics"]
        planned_objects_array = request.POST["planned"]
        freq_objects_array = request.POST["freq"]
        month_objects_array = request.POST["month"]
        #print request.POST("types")
        objetos = simplejson.loads('[%s]' % types_objects_array)
        objetos_tactics = simplejson.loads('[%s]' % tactics_objects_array)
        objetos_planned = simplejson.loads('[%s]' % planned_objects_array)
        objetos_freq = simplejson.loads('[%s]' % freq_objects_array)
        objetos_month = simplejson.loads('[%s]' % month_objects_array)
        for newtype in objetos[0]:
            typeMkt = MarketingTypes(name=newtype, register_business=register_object)
            typeMkt.save()
        for newtactic in objetos_tactics[0]:
            tacticMkt = MarketingTactics(name=newtactic, register_business=register_object)
            tacticMkt.save()
        for newplanned in objetos_planned[0]:
            plannedMkt = ConductMarketing(name=newplanned, register_business=register_object)
            plannedMkt.save()
        for newfreq in objetos_freq[0]:
            freqMkt = FrecuencyMarketing(name=newfreq, register_business=register_object)
            freqMkt.save()
        for newmonth in objetos_month[0]:
            monthMkt = MonthMarketing(name=newmonth, register_business=register_object)
            monthMkt.save()
        return HttpResponse("Business Save")


@csrf_exempt
def registerUserAjax(request):
    if request.method == "POST":
        register_object = RegisterUser(
            firstname=request.POST['firstname'],
            lastname=request.POST['lastname'],
            address=request.POST['address'],
            city=request.POST['city'],
            state=request.POST['state'],
            zip_code=request.POST['zip'],
            phone=request.POST['phone'],
            email=request.POST['email'],
            cell=request.POST['cell'],
            website=request.POST['website'],
            suscribe=request.POST["suscribe"]
        )
        register_object.save()
        return HttpResponse("User Save")


@csrf_protect
def contactUs(request):
    msg = ''
    if request.method == "POST":
        form = FormContactUs(request.POST)
        if form.is_valid():
            interested = form.cleaned_data["interested"]
            name_is = form.cleaned_data["name_is"]
            email_is = form.cleaned_data["email_is"]
            phones_is = form.cleaned_data["phones_is"]
            questions = form.cleaned_data["questions"]
            #Internal notification
            email_us_objects = EmailUs(
                interested=interested,
                name_is=name_is,
                email_is=email_is,
                phones_is=phones_is,
                questions=questions
            )
            email_us_objects.save()
            subject_message_admin = "Contact from Email us form"
            #ugly!! replace with template
            body_subject_admin = "<div>" \
                                 "<p><b>Name :</b>%s</p>" \
                                 "<p><b>Email :</b>%s</p>" \
                                 "<p><b>Phone :</b>%s</p>" \
                                 "<p><b>Question :</b>%s</p>" \
                                 "<p><b>Interested :</b>%s</p>" \
                                 "</div>" % (
                                     name_is, email_is, phones_is, questions, email_us_objects.get_interested_display())
            email_message_admin = EmailMessage(
                subject_message_admin,
                body_subject_admin,
                "Email Us <info@detourmaps.com>",
                ['detourcommunitymaps@gmail.com']
            )
            email_message_admin.content_subtype = "html"
            email_message_admin.send()
            #Auto-response
            subject_message_user = "Thanks for your comunication"
            body_message_user = "<div>" \
                                "<h1>DetourMaps</h1>" \
                                "<p>Thanks for your comunication %s</p>" \
                                "</div>" % name_is
            email_message_user = EmailMessage(subject_message_user, body_message_user, "Email Us<info@detourmaps.com>",
                                              [email_is])
            email_message_user.content_subtype = "html"
            email_message_user.send()
            msg = "Your Information was sent"
            return HttpResponse(msg)
        else:
            return render_to_response('contact.html', {'form': form, 'msg': msg, 'email_us': form_email_us},
                                      context_instance=RequestContext(request))
    else:
        form = FormContactUs()
        return render_to_response('contact.html', {'communities': Community.objects.all(), 'form': form, 'msg': msg,
                                                   'email_us': form_email_us}, context_instance=RequestContext(request))


def generateCard(community, name, code):
    basedir = path.dirname(__file__)
    try:
        font = ImageFont.truetype(basedir + '/resources/VERDANAB.TTF', 18)
        img = Image.open("%s/resources/%s_card.png" % (basedir, community.url_name))
        txt = '%s - %s' % (name, code)
        x, y = (180, 420)
        draw_img = ImageDraw.Draw(img)
        draw_img.text((x - 1, y - 1), txt, font=font, fill='#ffffff')
        draw_img.text((x - 1, y + 1), txt, font=font, fill='#ffffff')
        draw_img.text((x + 1, y + 1), txt, font=font, fill='#ffffff')
        draw_img.text((x + 1, y - 1), txt, font=font, fill='#ffffff')
        draw_img.text((x + 1, y), txt, font=font, fill='#ffffff')
        draw_img.text((x - 1, y), txt, font=font, fill='#ffffff')
        draw_img.text((x, y - 1), txt, font=font, fill='#ffffff')
        draw_img.text((x, y + 1), txt, font=font, fill='#ffffff')
        draw_img.text((x, y), txt, font=font, fill='#000000')
    except IOError:
        return 'Error 0 No image'
    try:
        img.save('%scards/%s.jpg' % (settings.MEDIA_ROOT, code), "JPEG", quality=90)
        return '%scards/%s.jpg' % (settings.MEDIA_ROOT, code)
    except IOError:
        return 'Error 1 Could not save'


@csrf_protect
def couponsForm(request):
    if request.method == "POST":
        name = request.POST['name']
        cellphone = request.POST['cellphone']
        email = request.POST['email']
        community = Community.objects.get(pk=request.POST['community'])
        subscribe = request.POST['subscribe']

        couponRequest = CouponRequestsForm(
            name=name,
            cellphone=cellphone,
            email=email,
            community=community,
            subscribe=subscribe
        )
        couponRequest.save()
        print couponRequest
        code = encode_url(couponRequest.id)
        card = generateCard(community, name, code)
        if not card.startswith('Error'):
            context = {
                'commnunity': community,
                'name': name,
                'businesses': Business.objects.filter(community=community, tag_service__id=121),
                'CARD_URL': '/media/cards/%s.jpg' % code
            }
            r = RequestContext(request)
            message = render_to_string('couponsResponse.html', context, r)
        else:
            message = 'Sorry, there is an error in the generation of cards or we have no promotions available in %s. We have registered this incident, so soon you will have news. Sincerely Detourmaps.'
        email_message = EmailMessage('DetourMaps Coupon', message, "DetourMaps <info@detourmaps.com>", [email])
        email_message.content_subtype = "html"
        email_message.send()

        return HttpResponse('Thanks')
    else:
        return HttpResponse('Error')


def report_comment(request):
    report_type = {
        'span': 'Is reporting a span content in this comment.',
        'violent': 'Is reporting a violent content in this comment.',
        'sexual': 'Is reporting a sexual content in this comment.',
        'privacy': 'Is reporting a endanger user privacy in this comment.',
        'other': request.GET['report_comment'] or 'Non comment report.'
    }

    comment_id = request.GET['id'] or None
    comment = Review.objects.get(id=comment_id)

    stars = comment.stars or None
    comment = comment.comment or None
    email_message = EmailMessage(
        from_email='jm.ticona.pacheco@gmail.com',
        to=['cs.detourmaps@gmail.com'],
        subject='Report Comment',
        body='''
        <table>
            <tr>
                <td>Stars:</td>
                <td>''' + str(stars) + '''</td>
            </tr>
            <tr>
                <td>Comment:</td>
                <td>''' + str(comment) + '''</td>
            </tr>
            <tr>
                <td>User:</td>
                <td>''' + request.user.username + '''</td>
            </tr>
            <tr>
                <td>Type report:</td>
                <td>''' + report_type[request.GET['report_type']] + '''</td>
            </tr>
        </table><br>
        <a href="http://''' + request.META['HTTP_HOST'] + '''/admin/community/review/''' + str(
            comment_id) + '''/">http://''' + request.META['HTTP_HOST'] + '''/admin/community/review/''' + str(
            comment_id) + '''/ See Comment</a>
        '''
    )
    email_message.content_subtype = "html"
    email_message.send()
    return HttpResponse('Mail Send')


@csrf_exempt
def renderModules(request):
    """
    liatado de modulos de acuerdo al template
    """
    module_object = Module.objects.filter(page=request.POST['template']).order_by('module_name')
    option = "<option>-- Choose a Module --</option>"
    for i in module_object:
        option += "<option value='%s' idb='%s'>%s</option>" % (i.pk, i.type_module, i.module_name)
    return HttpResponse(option)


@login_required
@csrf_exempt
def addContent(request, page_number):
    if page_number:
        if request.method == "POST":
            return HttpResponse("form")
        else:
            page_objects = get_object_or_404(Page, pk=page_number)
            module_objects = Module.objects.filter(page=page_objects.template)
            lista = []
            for module in module_objects:
                modelo_name = get_model("web", module.get_type_module_display())
                modelo_name_objects_count = modelo_name.objects.filter(page=page_objects)
                for j in modelo_name_objects_count:
                    renderForm = CustomForm(module.get_type_module_display())
                    renderFormtemplate = renderForm(instance=j)
                    lista.append(renderFormtemplate.as_p())
            return render_to_response('content.html',
                                      {'page': page_objects, 'modules': module_objects, 'cantidad': lista},
                                      context_instance=RequestContext(request))


@login_required
@csrf_exempt
def addForm(request):
    if request.method == "POST":
        dictionary = {
            'H': FormHeader().as_p(),
            'B': FormBlockHome().as_p(),
            'M': FormTestimonial().as_p(),
            'C': FormComplexText().as_p(),
            'T': FormSimpleText().as_p(),
        }
        return HttpResponse(dictionary[request.POST['idm']])


def bring_detourmaps(request):
    return render_to_response(
        'bring-detourmaps.html',
        {
            'communities': Community.objects.all(),
        },
        context_instance=RequestContext(request)
    )


def mailTestView(request):
    context = {
        'commnunity': Community.objects.get(id=1),
        'businesses': Business.objects.filter(community=Business.objects.get(id=1), tag_service__id=121)
    }
    return render_to_response('couponsResponse.html', context, RequestContext(request))


def userUtils(request):
    return render_to_response('utils_sys.js', mimetype="text/javascript", context_instance=RequestContext(request))


@csrf_exempt
def remoteConfirm(request):
    if request.method == "POST":
        valid = False
        username = request.POST["username"]
        try:
            user_object = User.objects.get(username=username)
        except User.DoesNotExist:
            valid = True
        return HttpResponse(simplejson.dumps(valid))


#USER VIEWS
@csrf_exempt
def userRegister(request):
    if request.POST:
        username = request.POST['user_email']
        password = request.POST['user_password']
        user_new = User()
        user_new.email = username
        user_new.username = username
        user_new.set_password(password)
        user_new.is_active = False
        user_new.is_staff = False
        user_new.is_superuser = False
        user_new.save()
        usuario_object = Usuario(
            user=user_new
        )
        usuario_object.save()
        tipo_usuario_object = TipoUsuario(
            usuario=usuario_object,
            access_token=user_new.username,
            expires=3600,
            userid=user_new.username,
            session_key=user_new.username
        )
        tipo_usuario_object.save()
        usuario_object.tipo_usuario = tipo_usuario_object.pk
        usuario_object.save()
        mail_status = 'ok'
        message = render_to_string("registerConfirm.html", {
            'user': user_new
        }, RequestContext(request))
        email_message = EmailMessage('DetourMaps Registration', message, "DetourMaps <info@detourmaps.com>",
                                     [user_new.email])
        email_message.content_subtype = "html"
        try:
            email_message.send()
        except Exception as err:
            mail_status = 'err'
        dict_msg = {
            'state': True
        }
    return HttpResponse(simplejson.dumps(dict_msg))


def reSendActivationMail(request):
    usr = User.objects.get(email=request.GET['user_email'])
    message = render_to_string("registerConfirm.html", {
        'user': usr
    }, RequestContext(request))
    email_message = EmailMessage('DetourMaps Registration', message, "DetourMaps <info@detourmaps.com>", [usr.email])
    email_message.content_subtype = "html"
    result = {
        'value': True
    }
    try:
        email_message.send()
    except Exception as err:
        result['value'] = True

    return HttpResponse(simplejson.dumps(result), mimetype='application/json')


@csrf_exempt
def shareQRUrl(request):
    if request.method == "GET":
        result = False
        message = '<h1><a href="http://detourmaps.com"><img src="http://detourmaps.com/static/community/img/detourOrange.png"/></a></h1>' \
                 '<a href="%s">%s</a>' % (request.GET['urlToShare'], request.GET['hiddenBiz'])
        email_message = EmailMessage('DetourMaps Registration', message, "DetourMaps <info@detourmaps.com>", [request.GET['emailShare']])
        email_message.content_subtype = "html"
        try:
            email_message.send()
            result = True
        except Exception as err:
            result = False
        dict_response = {
            'response': result
        }
        return HttpResponse(request.GET["callback"] + "(" + simplejson.dumps(dict_response,
                                                                             cls=simplejson.encoder.JSONEncoderForHTML) + ")   ",
                            mimetype="application/json")


def registerConfirm(request, user_id):
    usr = User.objects.get(id=user_id)
    usr.is_active = True
    usr.save()
    request.session["user"] = usr
    return redirect("/")


def userLogout(request):
    logout(request)
    return redirect('/')
    # Redirect to a success page.


@csrf_exempt
def userLogin(request):
    username = request.POST['user_email']
    password = request.POST['user_password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            request.session["user"] = user
            return redirect("/")
        else:
            return redirect("/")
            # Return a 'disabled account' error message
    else:
        return redirect("/")
        # Return an 'invalid login' error message.


@csrf_exempt
def userLoginAjax(request):
    username = request.POST['user_email']
    password = request.POST['user_password']
    user = authenticate(username=username, password=password)
    dict_response = {}
    if user is not None:
        if user.is_active:
            login(request, user)
            request.session["user"] = user
            dict_response["msg"] = "You are now logged in. Let's Get Started!"
            dict_response["confirm"] = True
            return HttpResponse(simplejson.dumps(dict_response))
        else:
            dict_response["msg"] = "User is not active, comunicate with the webmaster"
            dict_response["confirm"] = False
            return HttpResponse(simplejson.dumps(dict_response))
            # Return a 'disabled account' error message
    else:
        dict_response["msg"] = "The email and/or the password were incorrect"
        dict_response["confirm"] = False
        return HttpResponse(simplejson.dumps(dict_response))
        # Return an 'invalid login' error message.


@csrf_exempt
def newPassword(request):
    user_object = None
    if request.method == "POST":
        try:
            user_object = User.objects.get(username=request.POST["user_email"])
            user_object.set_password(request.POST["password"])
            user_object.save()
            return redirect('/communities/loginUser/')
        except User.DoesNotExist:
            pass
    elif request.method == "GET":
        try:
            decoder_email = decode_url(request.GET["code"])
            user_object = User.objects.get(pk=decoder_email)
        except User.DoesNotExist:
            pass
        return render_to_response(
            'newPassword.html',
            {
                'communities': Community.objects.all(),
                'user': user_object
            },
            context_instance=RequestContext(request)
        )


@csrf_exempt
def reset_password(request):
    return render_to_response(
        'reset.html',
        {
            'communities': Community.objects.all()
        },
        context_instance=RequestContext(request)
    )


@csrf_exempt
def reset_email_password(request):
    email_account = request.POST["email"]
    user_object = None
    try:
        user_object = User.objects.get(username=email_account)
        reset_password = encode_url(user_object.pk, 8)
        message = render_to_string("password.html", {
            'hash': reset_password
        }, RequestContext(request))
        email_message = EmailMessage('DetourMaps Registration', message, "DetourMaps <info@detourmaps.com>",
                                     [user_object.email, ])
        email_message.content_subtype = "html"
        email_message.send()
    except User.DoesNotExist:
        user_object = User.objects.get(email=email_account)
        user_object = User.objects.get(username=email_account)
        reset_password = encode_url(user_object.pk, 8)
        message = render_to_string("password.html", {
            'hash': reset_password
        }, RequestContext(request))
        email_message = EmailMessage('DetourMaps Registration', message, "DetourMaps <info@detourmaps.com>",
                                     [user_object.email, ])
        email_message.content_subtype = "html"
        email_message.send()
    return HttpResponse("Please check your email inbox")


def tiny(request):
    return render_to_response('tiny.js', {'textarea_id': request.GET['textarea_id']}, mimetype="text/javascript",
                              context_instance=RequestContext(request))


def checkout_email(request):
    __user = None
    __available = False
    try:
        __user = User.objects.get(username=request.GET['value'])
        __available = True
    except Exception:
        __available = False
    obj = {'username': request.GET['value'],
           'available': __available}
    return HttpResponse(simplejson.dumps(obj), mimetype='application/json')


def faq(request):
    return render_to_response(
        'faq.html',
        {
            'communities': Community.objects.filter(active=True)
        },
        context_instance=RequestContext(request)
    )


def privacy(request):
    return render_to_response(
        'policy.html',
        {
            'communities': Community.objects.filter(active=True)
        },
        context_instance=RequestContext(request)
    )


def terms(request):
    return render_to_response(
        'terms.html',
        {
            'communities': Community.objects.filter(active=True)
        },
        context_instance=RequestContext(request)
    )


@csrf_exempt
def uploadImage(request):
    '''
    funcion para subir las imagenes al editor
    '''
    if request.method == "POST":
        #file =  request.META["HTTP_X_FILENAME"]
        image_object = ImagenEditor(
            imagen=request.FILES['file']
        )
        image_object.save()
        thumbnailer = get_thumbnailer(image_object.imagen)
        thumb = thumbnailer.get_thumbnail({'size': (600, 600)})
        thumb = thumbnailer.get_thumbnail_name({'size': (600, 600)})
        thumbStr = thumb.replace("\\", "/")
        thumbnail = "http://%s/media/%s" % (request.META["HTTP_HOST"], thumbStr)
        return HttpResponse(thumbnail)
    else:
        return HttpResponse("not save")


@csrf_exempt
def get_active_posts(request):
    if request.method == "GET":
        post_objects = Post.objects.filter(active=True)
        list_posts = []
        for j in post_objects:
            thumbnailer = get_thumbnailer(j.principal_image)
            thumb = thumbnailer.get_thumbnail({'size': (600, 600)})
            thumb = thumbnailer.get_thumbnail_name({'size': (600, 600)})
            thumbStr = thumb.replace("\\", "/")
            thumbnail = "http://%s/media/%s" % (request.META["HTTP_HOST"], thumbStr)
            dict_posts = {
                'name': j.name,
                'url_name': j.url_name,
                'category': j.category.name,
                'url_category': j.category.url_name,
                'img': force_unicode(thumbnail),
                'content': force_unicode(j.content),
                'date': datetime.date.strftime(j.date, "%A, %B %dth, %Y"),
                'user': j.user.username,
                'reblog': j.reblog
            }
            list_posts.append(dict_posts)
        dict_response = {
            'posts': list_posts
        }
        return HttpResponse(request.GET["callback"] + "(" + simplejson.dumps(list_posts,
                                                                             cls=simplejson.encoder.JSONEncoderForHTML) + ")   ",
                            mimetype="application/json")


@csrf_exempt
def searchBusiness(request):
    if request.method == "GET":
        biz_objects = Business.objects.filter(name__icontains=request.GET["marklet-search"])
        list_biz = []
        for i in biz_objects:
            dict_biz = {
                'name': i.name,
                'url': 'http://detourmaps.com%s' % i.get_absolute_url()
            }
            list_biz.append(dict_biz)
        return HttpResponse(request.GET["callback"] + "(" + simplejson.dumps(list_biz,
                                                                             cls=simplejson.encoder.JSONEncoderForHTML) + ")   ",
                            mimetype="application/json")


def media_kit(request):
    return render_to_response(
        'media-kit.html',
        {},
        context_instance=RequestContext(request)
    )


def media_kit_file(request):
    return render_to_response(
        'media-kit-file.html',
        {
            'communities': Community.objects.filter(active=True)
        },
        context_instance=RequestContext(request)
    )


def bookmarklet(request):
    if request.META.has_key('HTTP_USER_AGENT'):
        user_agent = request.META['HTTP_USER_AGENT']
        pattern = "(up.browser|up.link|mmp|symbian|smartphone|midp|wap|phone|windows ce|pda|mobile|mini|palm|netfront)"
        prog = re.compile(pattern, re.IGNORECASE)
        match = prog.search(user_agent)
        if match:
            response = render_to_response('drag-marklet-m.html', {},
                                          context_instance=RequestContext(request))
            return response
        else:
            response = render_to_response('drag-marklet.html', {},
                                          context_instance=RequestContext(request))
            return response


def mobile_partner(request, name):
    if name:
        partner_object = Partner.objects.get(url_name=name)
        if request.META.has_key('HTTP_USER_AGENT'):
            user_agent = request.META['HTTP_USER_AGENT']
            pattern = "(up.browser|up.link|mmp|symbian|smartphone|midp|wap|phone|windows ce|pda|mobile|mini|palm|netfront)"
            prog = re.compile(pattern, re.IGNORECASE)
            match = prog.search(user_agent)
            if match:
                return render_to_response(
                    'landing-partner-m.html',
                    {
                        'partner': partner_object,
                    },
                    context_instance=RequestContext(request)
                )


def mobile_welcome(request):
    if request.META.has_key('HTTP_USER_AGENT'):
        user_agent = request.META['HTTP_USER_AGENT']
        pattern = "(up.browser|up.link|mmp|symbian|smartphone|midp|wap|phone|windows ce|pda|mobile|mini|palm|netfront)"
        prog = re.compile(pattern, re.IGNORECASE)
        match = prog.search(user_agent)
        if match:
            return render_to_response(
                'welcome-m.html',
                {},
                context_instance=RequestContext(request)
            )


@csrf_exempt
def create_user_welcome(request):
    if request.method == "POST":
        user_new = User.objects.get_or_create(username=request.POST["email"])
        if user_new[1]:
            user_new[0].set_password(request.POST["password"])
            user_new[0].save()
        return HttpResponse("User was saved!!!")


@csrf_exempt
def contact_us(request):
    dict_msg = {}
    if request.method == "GET":
        interested = request.GET["interested"]
        name_is = request.GET["name_is"]
        email_is = request.GET["email_is"]
        phones_is = request.GET["phones_is"]
        questions = request.GET["questions"]
        #Internal notification
        email_us_objects = EmailUs(
            interested=interested,
            name_is=name_is,
            email_is=email_is,
            phones_is=phones_is,
            questions=questions
        )
        email_us_objects.save()
        subject_message_admin = "Contact from Email us form"
        #ugly!! replace with template
        body_subject_admin = "<div>" \
                             "<p><b>Name :</b>%s</p>" \
                             "<p><b>Email :</b>%s</p>" \
                             "<p><b>Phone :</b>%s</p>" \
                             "<p><b>Question :</b>%s</p>" \
                             "<p><b>Interested :</b>%s</p>" \
                             "</div>" % (name_is, email_is, phones_is, questions,
                                         email_us_objects.get_interested_display())
        email_message_admin = EmailMessage(
            subject_message_admin,
            body_subject_admin,
            "Email Us <info@detourmaps.com>",
            ['detourcommunitymaps@gmail.com']
        )
        email_message_admin.content_subtype = "html"
        email_message_admin.send()
        #Auto-response
        subject_message_user = "Thanks for your comunication"
        body_message_user = "<div>" \
                            "<h1>DetourMaps</h1>" \
                            "<p>Thanks for your comunication %s</p>" \
                            "</div>" % name_is
        email_message_user = EmailMessage(subject_message_user, body_message_user,
                                          "Email Us<info@detourmaps.com>", [email_is])
        email_message_user.content_subtype = "html"
        email_message_user.send()
        msg = "Your Information was sent"
        dict_msg['msg'] = msg
        return HttpResponse(request.GET["callback"] + "(" + simplejson.dumps(dict_msg,
                                                                         cls=simplejson.encoder.JSONEncoderForHTML) + ")   ",
                        mimetype="application/json")