# -*- coding: utf-8 -*-
import re
import random
import datetime
from datetime import timedelta
import base64
import urllib
import hashlib
import urlparse
import json

import simplejson
import qrcode
import requests

#pdf
import ho.pisa as pisa
import os
import cStringIO as StringIO
import cgi
import urllib2
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseBadRequest, Http404, HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.encoding import force_unicode
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.sessions.models import Session
from django.contrib.auth import authenticate, login
from django.db.models import Count
from django.db import connection
from easy_thumbnails.files import get_thumbnailer
from django.template.defaultfilters import slugify
from django.core.mail import EmailMessage
from localflavor.us.us_states import US_STATES
from os import path
#models
from community.models import Community, Category, Business, ImageBusiness, Service, Review, \
    Subscription, BusinessEvent, ImageBusinessEvents, BusinessMenu, BusinessSchedule, \
    ContactCard, Card, NewsletterSuscription, CuponBusiness, Usuario, Partner, LandingPartner, PhoneNumber as PNumber, \
    CommunitySocial, CommunityText, HeaderCommunity, Video, TipoUsuario
from community.twitter import Twitter
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import settings
from web.models import PrintMaps, ImagesPrintMaps, LandingPage, PhoneNumber, LandingSocial, HeaderPage, LandingText, \
    Video as WVideo, Newsletter
from web.forms import FormCouponsRequest
from django.template.loader import render_to_string
#draw card
from PIL import Image, ImageDraw, ImageFont
from django.template.loader import get_template
from django.template import Context, loader
from web.short_url import encode_url, decode_url
#facebook auth
from community.facebook import Facebook
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q


class MyPagination:
    def mySelfPagination(self, objeto, offset, pager):
        objects_list = objeto
        paginator = Paginator(objects_list, offset)
        page = pager
        try:
            objetos = paginator.page(page)
        except PageNotAnInteger:
            objetos = paginator.page(1)
        except EmptyPage:
            objetos = paginator.page(paginator.num_pages)
        return objetos


def setUrlNameBusiness(request):
    business_objects = Business.objects.all()
    for biz in business_objects:
        biz.url_name = slugify(biz.name)
        biz.save()
    return HttpResponse('Businesses Updated')


def setCodeNameBusiness(request):
    business_objects = Business.objects.all()
    for biz in business_objects:
        biz.auth_code = encode_url(biz.id, 8)
        biz.save()
    return HttpResponse('Businesses Updated')


def getReview(request):
    if request.method == "GET":
        business_object = Business.objects.get(id=int(decode_url(request.GET["tag"])))
        review_objects = Review.objects.filter(business=business_object).order_by("-date")
        votes = qualify(business_object)
        dict_votes = {
            'votes': votes,
            'qReviews': review_objects.count()
        }
        lista_reviews = []
        for i in review_objects:
            dict_review = {
                'posted': i.user.username,
                'date': force_unicode(i.date.strftime('%b %d - %Y')),
                'comment': i.comment,
                'rate': i.stars
            }
            lista_reviews.append(dict_review)
        dict_votes['reviews'] = lista_reviews
        return HttpResponse(simplejson.dumps(dict_votes))


def getMenu(request):
    if request.method == "GET":
        business_object = Business.objects.get(id=int(decode_url(request.GET["tag"])))
        #menu_object = BusinessMenu.objects.filter(business=business_object)

        dict_votes = {
            #'menu': menu_object[0].menu
            'menu': business_object.html_menu
        }
        return HttpResponse(simplejson.dumps(dict_votes))


def generateCard(community, name, code):
    basedir = path.dirname(__file__)
    try:
        font = ImageFont.truetype(basedir + '/resources/VERDANAB.TTF', 12)
        img = Image.open("%s/resources/%s/card.png" % (basedir, str(community.name).capitalize()))
        txt = '%s - %s' % (name, code)
        x, y = (55, 160)
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
        return '%scards/%s.jpg' % (settings.MEDIA_URL, code)
    except IOError:
        return 'Error 1 Could not save'


def generateQR(url, code, host):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )
    data = 'http://%s/community/%s' % (host, url)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image()
    try:
        img.save('%sqr/%s.jpg' % (settings.MEDIA_ROOT, code), "JPEG")
        return '%sqr/%s.jpg' % (settings.MEDIA_URL, code)
    except IOError:
        return 'Error 1 Could not save'


@csrf_exempt
def getDealCard(request):
    if request.method == "GET":
        business_object = Business.objects.get(id=int(decode_url(request.GET["tag"])))
        contact_object = None
        try:
            contact_object = ContactCard.objects.get(email=request.GET["email"])
            card_object = Card.objects.filter(contact_card=contact_object).filter(business=business_object)
            if card_object.count() > 0:
                card_last = card_object[card_object.count() - 1]
                if card_last.used:
                    card_object = Card(
                        contact_card=contact_object,
                        business=business_object,
                        mode='D'
                    )
                    card_object.save()
                    card = generateCard(business_object.community, request.GET["name"], encode_url(card_object.id))
                    qr_code = generateQR('%s/map/business/panel?auth_code=%s' % (
                        business_object.community.url_name, encode_url(card_object.id)),
                                         encode_url(card_object.id), request.META["HTTP_HOST"])
                    html = render_to_string(
                        'pdf_deals.html',
                        {
                            'pagesize': 'A4',
                            'card': card,
                            'qr_code': qr_code
                        },
                        context_instance=RequestContext(request)
                    )
                    result = StringIO.StringIO()
                    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")), dest=result,
                                            link_callback=fetch_resources,
                                            encoding='UTF-8')
                    if not pdf.err:
                        resp = HttpResponse(result.getvalue(), mimetype='application/pdf')
                        resp['Content-Disposition'] = 'attachment; filename=%s.pdf' % request.GET["name"]
                        return resp
                    return HttpResponse('Gremlins ate your pdf! %s' % cgi.escape(html))
                else:
                    card = generateCard(business_object.community, request.GET["name"], encode_url(card_last.id))
                    qr_code = generateQR('%s/map/business/panel?auth_code=%s' % (
                        business_object.community.url_name, encode_url(card_last.id)),
                                         encode_url(card_last.id), request.META["HTTP_HOST"])
                    html = render_to_string(
                        'pdf_deals.html',
                        {
                            'pagesize': 'A4',
                            'card': card,
                            'qr_code': qr_code
                        },
                        context_instance=RequestContext(request)
                    )
                    result = StringIO.StringIO()
                    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")), dest=result,
                                            link_callback=fetch_resources,
                                            encoding='UTF-8')
                    if not pdf.err:
                        resp = HttpResponse(result.getvalue(), mimetype='application/pdf')
                        resp['Content-Disposition'] = 'attachment; filename=%s.pdf' % request.GET["name"]
                        return resp
                    return HttpResponse('Gremlins ate your pdf! %s' % cgi.escape(html))
            else:
                card = generateCard(business_object.community, request.GET["name"], encode_url(card_object.id))
                qr_code = generateQR('%s/map/business/panel?auth_code=%s' % (
                    business_object.community.url_name, encode_url(card_object.id)),
                                     encode_url(card_object.id), request.META["HTTP_HOST"])
                html = render_to_string(
                    'pdf_deals.html',
                    {
                        'pagesize': 'A4',
                        'card': card,
                        'qr_code': qr_code
                    },
                    context_instance=RequestContext(request)
                )
                result = StringIO.StringIO()
                pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")), dest=result,
                                        link_callback=fetch_resources,
                                        encoding='UTF-8')
                if not pdf.err:
                    resp = HttpResponse(result.getvalue(), mimetype='application/pdf')
                    resp['Content-Disposition'] = 'attachment; filename=%s.pdf' % request.GET["name"]
                    return resp
                return HttpResponse('Gremlins ate your pdf! %s' % cgi.escape(html))
        except ContactCard.DoesNotExist:
            contact_object = ContactCard(
                name=request.GET["name"],
                email=request.GET["email"],
                phone=request.GET["phone"]
            )
            contact_object.save()
            card_object = Card(
                contact_card=contact_object,
                business=business_object,
                mode='D'
            )
            card_object.save()
            card = generateCard(business_object.community, request.GET["name"], encode_url(card_object.id))
            qr_code = generateQR('%s/map/business/panel?auth_code=%s' % (
                business_object.community.url_name, encode_url(card_object.id)),
                                 encode_url(card_object.id), request.META["HTTP_HOST"])
            html = render_to_string(
                'pdf_deals.html',
                {
                    'pagesize': 'A4',
                    'card': card,
                    'qr_code': qr_code
                },
                context_instance=RequestContext(request)
            )
            result = StringIO.StringIO()
            pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")), dest=result, link_callback=fetch_resources,
                                    encoding='UTF-8')
            if not pdf.err:
                resp = HttpResponse(result.getvalue(), mimetype='application/pdf')
                resp['Content-Disposition'] = 'attachment; filename=%s.pdf' % request.GET["name"]
                return resp
            return HttpResponse('Gremlins ate your pdf! %s' % cgi.escape(html))
            #return html


@csrf_exempt
def printCoupon(request):
    if request.method == "GET":
        if "source" in request.GET:
            business_object = Business.objects.get(id=int(decode_url(request.GET["source"])))
            coupon_object = CuponBusiness.objects.filter(business=business_object)
            html = render_to_response(
                'coupon.html',
                {
                    'pagesize': 'A4',
                    'source': coupon_object[0]
                },
                context_instance=RequestContext(request)
            )
            #result = StringIO.StringIO()
            #pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")), dest=result, link_callback=fetch_resources,
            #                        encoding='UTF-8')
            #if not pdf.err:
            #    resp = HttpResponse(result.getvalue(), mimetype='application/pdf')
            #    resp['Content-Disposition'] = 'attachment; filename=%s.pdf' % business_object.url_name
            #    return resp
            #return HttpResponse('Gremlins ate your pdf! %s' % cgi.escape(html))
            return html


@csrf_exempt
def generateShareMenu(request):
    if request.method == "GET":
        business_object = Business.objects.get(id=int(decode_url(request.GET["tag"])))
        menu_object = BusinessMenu.objects.filter(business=business_object)
        html = render_to_string(
            'pdfMenu.html',
            {
                'menu': menu_object[0].menu,
                'biz': business_object
            },
            context_instance=RequestContext(request)
        )
        result = open('%s/%s-menu.pdf' % (settings.MEDIA_ROOT, business_object.url_name), "wb")
        pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")), dest=result, link_callback=fetch_resources,
                                encoding='UTF-8')
        # if not pdf.err:
        #     pdf = HttpResponse(result.getvalue(), mimetype='application/pdf')
        #     pdf['Content-Disposition'] = 'attachment; filename=%s-menu.pdf' % business_object.url_name
        #     return pdf
        result.close()
        dict_response = {
            'url': 'http://www.detourmaps.com/media/%s-menu.pdf' % business_object.url_name,
            'name': "%s's Menu" % business_object.name,
            'description': business_object.description,
            'redirect': 'http://localhost:8000/community/%s/map/business/?name=%s&auth_code%s' % (
                business_object.community.url_name, business_object.url_name, business_object.getUniqueCode())
        }
        return HttpResponse(simplejson.dumps(dict_response))


@csrf_exempt
def sendCardEmail(request):
    if request.method == "GET":
        business_object = Business.objects.get(id=int(decode_url(request.GET["tag"])))
        user_template_html = '/home/mauricio/Documentos/backup_detourmaps/detourmaps/community/templates/savings-template.html'
        html_user = get_template(user_template_html)
        context_user = Context(
            {
                'name': request.GET["name"],
                'biz': business_object.getUniqueCode(),
                'email': request.GET["email"],
                'phone': request.GET["phone"],
                'business': business_object
            }
        )
        subject_user, from_user, to_user = 'Detour Maps - Get your deal card', 'Detour Maps <info@detourmaps.com>',
        request.GET["email"]
    user_context_html = html_user.render(context_user)
    message_user = EmailMessage(subject_user, user_context_html, from_user, [to_user])
    message_user.content_subtype = "html"
    message_user.send()
    dict_response = {
        'msg': 'Congratulations. Check your email and follow the instructions!'
    }
    return HttpResponse(simplejson.dumps(dict_response))


@csrf_exempt
def panelBusiness(request, name):
    if request.method == "GET":
        if "auth_code" in request.GET:
            code = decode_url(request.GET["auth_code"])
            card_object = Card.objects.get(pk=code)
            return render_to_response(
                'panel_card.html',
                {
                    'card': card_object
                },
                context_instance=RequestContext(request)
            )
    if request.method == "POST":
        if "check" in request.POST and "card" in request.POST:
            card_object = Card.objects.get(pk=decode_url(request.POST["card"]))
            card_object.used = request.POST["check"]
            card_object.save()
            return HttpResponse("Card Used")


@csrf_exempt
def printDealCard(request):
    if request.method == "GET":
        business_object = Business.objects.get(id=int(decode_url(request.GET["tag"])))
        contact_object = None
        try:
            contact_object = ContactCard.objects.get(email=request.GET["email"])
            card_object = Card.objects.filter(contact_card=contact_object).filter(business=business_object).filter(
                used=False)
            if card_object.count() > 0:
                card_last = card_object[card_object.count() - 1]
                if card_last.used:
                    card_object = Card(
                        contact_card=contact_object,
                        business=business_object,
                        mode='P'
                    )
                    card_object.save()
                    card = generateCard(business_object.community, request.GET["name"], encode_url(card_object.id))
                    qr_code = generateQR('%s/map/business/panel?auth_code=%s' % (
                        business_object.community.url_name, encode_url(card_object.id)),
                                         encode_url(card_object.id), request.META["HTTP_HOST"])
                    html = render_to_response(
                        'print_deals.html',
                        {
                            'card': card,
                            'qr_code': qr_code
                        },
                        context_instance=RequestContext(request)
                    )
                    return HttpResponse(html)
                else:
                    card = generateCard(business_object.community, request.GET["name"], encode_url(card_last.id))
                    qr_code = generateQR('%s/map/business/panel?auth_code=%s' % (
                        business_object.community.url_name, encode_url(card_last.id)),
                                         encode_url(card_last.id), request.META["HTTP_HOST"])
                    html = render_to_response(
                        'print_deals.html',
                        {
                            'card': card,
                            'qr_code': qr_code
                        },
                        context_instance=RequestContext(request)
                    )
                    return HttpResponse(html)
            else:
                card_object = Card(
                    contact_card=contact_object,
                    business=business_object,
                    mode='P'
                )
                card_object.save()
                card = generateCard(business_object.community, request.GET["name"], encode_url(card_object.id))
                qr_code = generateQR('%s/map/business/panel?auth_code=%s' % (
                    business_object.community.url_name, encode_url(card_object.id)),
                                     encode_url(card_object.id), request.META["HTTP_HOST"])
                html = render_to_response(
                    'print_deals.html',
                    {
                        'card': card,
                        'qr_code': qr_code
                    },
                    context_instance=RequestContext(request)
                )
                #result = StringIO.StringIO()
                #pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")), dest=result, link_callback=fetch_resources, encoding='UTF-8')
                #if not pdf.err:
                #    resp = HttpResponse(result.getvalue(), mimetype='application/pdf')
                #    resp['Content-Disposition'] = 'attachment; filename=%s.pdf' % request.GET["name"]
                #    return resp
                #return HttpResponse('Gremlins ate your pdf! %s' % cgi.escape(html))
                return HttpResponse(html)
        except ContactCard.DoesNotExist:
            contact_object = ContactCard(
                name=request.GET["name"],
                email=request.GET["email"],
                phone=request.GET["phone"]
            )
            contact_object.save()
            card_object = Card(
                contact_card=contact_object,
                business=business_object,
                mode='P'
            )
            card_object.save()
            card = generateCard(business_object.community, request.GET["name"], encode_url(card_object.id))
            qr_code = generateQR('%s/map/business/panel?auth_code=%s' % (
                business_object.community.url_name, encode_url(card_object.id)),
                                 encode_url(card_object.id), request.META["HTTP_HOST"])
            html = render_to_response(
                'print_deals.html',
                {
                    'card': card,
                    'qr_code': qr_code
                },
                context_instance=RequestContext(request)
            )
            #result = StringIO.StringIO()
            #pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")), dest=result, link_callback=fetch_resources, encoding='UTF-8')
            #if not pdf.err:
            #    resp = HttpResponse(result.getvalue(), mimetype='application/pdf')
            #    resp['Content-Disposition'] = 'attachment; filename=%s.pdf' % request.GET["name"]
            #    return resp
            #return HttpResponse('Gremlins ate your pdf! %s' % cgi.escape(html))
            return HttpResponse(html)


class UnsupportedMediaPathException(Exception):
    pass


def fetch_resources(uri, rel):
    """
    Callback to allow xhtml2pdf/reportlab to retrieve Images,Stylesheets, etc.
    `uri` is the href attribute from the html link element.
    `rel` gives a relative path, but it's not used here.

    """
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT,
                            uri.replace(settings.MEDIA_URL, ""))
    elif uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT,
                            uri.replace(settings.STATIC_URL, ""))
    else:
        path = os.path.join(settings.STATIC_ROOT,
                            uri.replace(settings.STATIC_URL, ""))

        if not os.path.isfile(path):
            path = os.path.join(settings.MEDIA_ROOT,
                                uri.replace(settings.MEDIA_URL, ""))

            if not os.path.isfile(path):
                raise UnsupportedMediaPathException(
                    'media urls must start with %s or %s' % (
                        settings.MEDIA_ROOT, settings.STATIC_ROOT))

    return path


def getSchedule(request):
    if request.method == "GET":
        business_object = Business.objects.get(id=int(decode_url(request.GET["tag"])))
        schedule_object = BusinessSchedule.objects.filter(business=business_object)
        dict_votes = {
            'schedule': schedule_object[0].schedule
        }
        return HttpResponse(simplejson.dumps(dict_votes))


def communitySelection(request):
    if request.META.has_key('HTTP_USER_AGENT'):
        user_agent = request.META['HTTP_USER_AGENT']
        pattern = "(up.browser|up.link|mmp|symbian|smartphone|midp|wap|phone|windows ce|pda|mobile|mini|palm|netfront)"
        prog = re.compile(pattern, re.IGNORECASE)
        match = prog.search(user_agent)
        if match:
            return render_to_response(
                'index.html',
                {
                    'community': Community.objects.filter(active=True),
                },
                context_instance=RequestContext(request)
            )
        else:
            print_maps = PrintMaps.objects.all()[0]
            img_print_maps = ImagesPrintMaps.objects.filter(print_maps=print_maps)
            img_list = []
            for i in img_print_maps:
                thumbnailer = get_thumbnailer(i.img)
                thumb = thumbnailer.get_thumbnail({'size': (600, 400), 'crop': True})
                thumb = thumbnailer.get_thumbnail_name({'size': (600, 400), 'crop': True})
                img_list.append(thumb)

            new_user = False
            if request.session.has_key('sing_up'):
                if request.session['sing_up']:
                    new_user = request.session['sing_up']
            context = {
                'new_user': new_user,
                'community': Community.objects.filter(active=True),
                'coupons_form': FormCouponsRequest(),
                'categories': Category.objects.all().order_by('id'),
                'print_maps': {
                    'type_img_src': print_maps.type_img_src,
                    'maps_standard': img_list,
                    'maps_customize': print_maps.maps_customize
                }
            }
            print context
            return render_to_response('homeDetourMaps.html', context, RequestContext(request))


def communityEvolution(request):
    if request.META.has_key('HTTP_USER_AGENT'):
        user_agent = request.META['HTTP_USER_AGENT']
        pattern = "(up.browser|up.link|mmp|symbian|smartphone|midp|wap|phone|windows ce|pda|mobile|mini|palm|netfront)"
        prog = re.compile(pattern, re.IGNORECASE)
        match = prog.search(user_agent)
        if match:
            return render_to_response(
                'index.html',
                {
                    'community': Community.objects.filter(active=True),
                },
                context_instance=RequestContext(request)
            )
        else:
            print_maps = PrintMaps.objects.all()[0]
            img_print_maps = ImagesPrintMaps.objects.filter(print_maps=print_maps)
            img_list = []
            for i in img_print_maps:
                thumbnailer = get_thumbnailer(i.img)
                thumb = thumbnailer.get_thumbnail({'size': (600, 400), 'crop': True})
                thumb = thumbnailer.get_thumbnail_name({'size': (600, 400), 'crop': True})
                img_list.append(thumb)

            new_user = False
            if request.session.has_key('sing_up'):
                if request.session['sing_up']:
                    new_user = request.session['sing_up']
            context = {
                'new_user': new_user,
                'community': Community.objects.filter(active=True),
                'coupons_form': FormCouponsRequest(),
                'categories': Category.objects.all().order_by('id'),
                'print_maps': {
                    'type_img_src': print_maps.type_img_src,
                    'maps_standard': img_list,
                    'maps_customize': print_maps.maps_customize
                }
            }
            print context
            return render_to_response('home-evolution.html', context, RequestContext(request))


@csrf_protect
def search_page(request):
    paginator_objects = MyPagination()
    if request.method == "POST":
        request.session["q"] = request.POST["q"]
        if "cat" in request.POST:
            request.session["cat"] = request.POST["cat"]
            if request.POST["cat"] == "c":
                resultset = Business.objects.filter(name__icontains = request.POST["q"]).order_by('community__name')
            elif request.POST["cat"] == "d":
                resultset = Business.objects.filter(name__icontains = request.POST["q"]).order_by('local_deals')
            else:
                resultset = Business.objects.filter(name__icontains = request.POST["q"]).order_by()
        else:
            resultset = Business.objects.filter(name__icontains = request.POST["q"])
        return render_to_response(
            'search/search.html',
            {
                'resultset': paginator_objects.mySelfPagination(resultset, 6, request.GET.get('page', 1)),
                'search': request.POST["q"]
            },
            context_instance=RequestContext(request)
        )
    else:
        q = request.session["q"]
        if "cat" in request.session:
            cat = request.session["cat"]
            if cat == "c":
                resultset = Business.objects.filter(name__icontains = q).order_by('community__name')
            elif cat == "d":
                resultset = Business.objects.filter(name__icontains = q).order_by('local_deals')
            else:
                resultset = Business.objects.filter(name__icontains = q).order_by()
        else:
            resultset = Business.objects.filter(name__icontains = q)
        return render_to_response(
            'search/search.html',
            {
                'resultset': paginator_objects.mySelfPagination(resultset, 6, request.GET.get('page', 1)),
                'search': q
            },
            context_instance=RequestContext(request)
        )

@csrf_exempt
def get_business_by_letter(request):
    response = False
    dict_response = {}
    x = 0
    if request.method == "GET":
        if 'letter' in request.GET:
            letter = request.GET["letter"]
            business_objects = Business.objects.filter(Q(name__icontains=str(letter))|Q(category__name__icontains=str(letter))|Q(community__name__icontains=str(letter))|Q(tag_service__name__icontains=str(letter)))
            if business_objects.count() > 0: response = True
            lista_biz = []
            return_cat_id = lambda cat_id: cat_id or ''
            for biz in business_objects:
                dict_biz = {
                    'name': biz.name,
                    'url_name': biz.url_name,
                    'auth_code': encode_url(biz.pk, 8),
                    'community': biz.community.url_name
                }
                lista_biz.append(dict_biz)
            dict_response['business'] = lista_biz
            dict_response['response'] = response
            return HttpResponse(simplejson.dumps(dict_response))


def listCommunities(request):
    return render_to_response(
        'menu-community.html',
        {},
        context_instance=RequestContext(request)
    )


def getSavings(request):
    return render_to_response(
        'savings.html',
        {},
        context_instance=RequestContext(request)
    )


def getQRPage(request):
    return render_to_response(
        'qr-page.html',
        {},
        context_instance=RequestContext(request)
    )


def getAboutPage(request):
    return render_to_response(
        'about-mobile.html',
        {},
        context_instance=RequestContext(request)
    )


def getSignInPage(request):
    return render_to_response(
        'sign-in.html',
        {},
        context_instance=RequestContext(request)
    )


def getRegisterBusinessPage(request):
    return render_to_response(
        'register-business.html',
        {},
        context_instance=RequestContext(request)
    )


def getJoinUs(request):
    return render_to_response(
        'join-us-mobile.html',
        {
            'states': US_STATES
        },
        context_instance=RequestContext(request)
    )


def get_events_by_mobile(request):
    events_objects_today = BusinessEvent.objects.filter(date_begin=datetime.datetime.now().date()).order_by("date_begin")
    events_objects_community = BusinessEvent.objects.values('business__community').annotate(cCount=Count('business__community'))
    community_events = Community.objects.filter(
        business__businessevent__date_begin__gte=datetime.datetime.now().date()
    ).annotate(
        num_events=Count('business__businessevent')
    ).order_by('-num_events')
    return render_to_response(
        'events_mobile.html',
        {
            'events_today': events_objects_today,
            'community': community_events
        },
        context_instance=RequestContext(request)
    )


def get_landing_event(request):
    if request.method == "GET":
        event = BusinessEvent.objects.get(pk=decode_url(request.GET["auth_code"]))
        return render_to_response(
            'landing-event.html',
            {
                'event': event
            },
            context_instance=RequestContext(request)
        )


def contact_mobile(request):
    if request.method == "POST":
        pass
    else:
        return render_to_response(
            'contact-mobile.html',
            {
                'states': US_STATES
            },
            context_instance=RequestContext(request)
        )


def testDesign(request):
    return render_to_response(
        'test-design.html',
        {},
        context_instance=RequestContext(request)
    )


@csrf_exempt
def saveSuscriptionNewsletter(request):
    if request.method == "GET":
        business_object = Business.objects.get(id=int(decode_url(request.GET["tag"])))
        suscription_news_object = NewsletterSuscription(
            email=request.GET["emailRSS"],
            business=business_object
        )
        suscription_news_object.save()
        dict_response = {
            'msg': 'Thanks for your suscription to %s' % business_object.name
        }
        return HttpResponse(simplejson.dumps(dict_response))


def mapConstructor(request, name=None):
    if name:
        if request.GET:
            if 'code' in request.GET:
                args = {
                    'client_id': settings.FACEBOOK_APP_ID,
                    'redirect_uri': request.META["HTTP_REFERER"],
                    'client_secret': settings.FACEBOOK_APP_SECRET,
                    'code': request.GET.get('code')
                }
                url = 'https://graph.facebook.com/oauth/access_token?' + \
                      urllib.urlencode(args)
                response = urlparse.parse_qs(urllib.urlopen(url).read())
                access_token = response['access_token'][0]
                expires = response['expires'][0]
                face = Facebook()
                user_face = face.authenticate(access_token, None, expires)
                request.session['user'] = user_face
                request.session.set_expiry(3600)
                request.session.modified = True
                return HttpResponseRedirect(reverse('map'))
        else:
            url_name = name
            communities = Community.objects.filter(active=True)
            community_object = communities.get(url_name=url_name)
            category_object = Category.objects.all().order_by('id')
            service_object = Service.objects.all().order_by('name')
            partner_objects = Partner.objects.filter(community=community_object)
            popup = False
            if request.META.has_key('HTTP_USER_AGENT'):
                user_agent = request.META['HTTP_USER_AGENT']
                pattern = "(up.browser|up.link|mmp|symbian|smartphone|midp|wap|phone|windows ce|pda|mobile|mini|palm|netfront)"
                prog = re.compile(pattern, re.IGNORECASE)
                match = prog.search(user_agent)
                if match:
                    return render_to_response(
                        'community-mobile.html',
                        {
                            'community': communities,
                            'community': community_object,
                            'categories': category_object,
                            'services': service_object
                        },
                        context_instance=RequestContext(request)
                    )
                else:
                    if "pop" in request.session and "community" in request.session:
                        if name == request.session["community"]:
                            popup = request.session["pop"]
                        else:
                            popup = False
                            request.session["community"] = name
                    else:
                        request.session["pop"] = True
                        request.session["community"] = name
                        popup = False
                    try:
                        basedir = settings.MEDIA_ROOT
                        if community_object.has_css_file:
                            with open('%s/%s' % (basedir, str(community_object.css_file)), 'r') as f:
                                text_css = ""
                                for i in f:
                                    text_css += i
                        else:
                            text_css = community_object.discover_css
                    except Community.DoesNotExist:
                        text_css = community_object.discover_css
                    form = FormCouponsRequest()
                    return render_to_response('cBaseB.html', {
                        'communities': communities,
                        'community': community_object,
                        'categories': category_object,
                        'services': service_object,
                        'coupons_form': form,
                        'css': text_css,
                        'business': False,
                        'partners': partner_objects,
                        'pop': popup
                    }, RequestContext(request))
    else:
        return Http404()


def deals_by_community(request, name=None):
    if name:
        community_object = Community.objects.get(url_name=name)
        biz_objects = Business.objects.filter(community=community_object)
        lista_biz = []
        for i in biz_objects:
            deals = get_deals(i)
            if deals:
                if deals != 'N':
                    lista_biz.append(i)
        if request.META.has_key('HTTP_USER_AGENT'):
            user_agent = request.META['HTTP_USER_AGENT']
            pattern = "(up.browser|up.link|mmp|symbian|smartphone|midp|wap|phone|windows ce|pda|mobile|mini|palm|netfront)"
            prog = re.compile(pattern, re.IGNORECASE)
            match = prog.search(user_agent)
            if match:
                return render_to_response(
                    'deals_by_community.html',
                    {
                        'businesses': lista_biz,
                        'community': community_object,
                        'communities': Community.objects.all(),
                    },
                    context_instance=RequestContext(request)
                )
            else:
                return render_to_response(
                    'deals-community.html',
                    {
                        'businesses': lista_biz,
                        'community': community_object,
                        'communities': Community.objects.all(),
                    },
                    context_instance=RequestContext(request)
                )


def events_by_community(request, name=None):
    paginator_objects = MyPagination()
    community_object = None
    if name:
        community_object = Community.objects.get(url_name=name)
        events_biz_objects = BusinessEvent.objects.filter(business__community=community_object).filter(
            date_begin__gte=datetime.datetime.now().date()).order_by('date_begin')
        lista_biz_events = paginator_objects.mySelfPagination(events_biz_objects, 2, request.GET.get('page', 1))
    else:
        events_biz_objects = BusinessEvent.objects.filter(
            date_begin__gte=datetime.datetime.now().date()
        ).order_by('date_begin')
        lista_biz_events = paginator_objects.mySelfPagination(events_biz_objects, 2, request.GET.get('page', 1))
        community_object = False
    return render_to_response(
        'events_by_community.html',
        {
            'events': lista_biz_events,
            'community': community_object,
            'communities': Community.objects.all()
        },
        context_instance=RequestContext(request)
    )


def discover_by_community(request, name=None):
    if name:
        community_object = Community.objects.get(url_name=name)
        # url_locator = "http://xoap.weather.com/weather/search/search?where=%s,il" % community_object.name
        # response = urllib2.urlopen(url_locator)
        # page = response.read()
        # xml_info = parse(StringIO.StringIO(page))
        # name = xml_info.getElementsByTagName('loc')
        # value_yahoo = name[0].attributes["id"].value
        # url = "http://weather.yahooapis.com/forecastrss?p=%s&u=f" % value_yahoo
        # info = feedparser.parse(url)
        # doc = info.entries[0].summary_detail.value
        # html_tags = BeautifulSoup(doc)
        # img_tags = html_tags.find_all('img')
        f = urllib2.urlopen(
            "http://api.wunderground.com/api/e6bf60cfa7a98a56/conditions/q/IL/%s.json" % community_object.url_name)
        json_string = f.read()
        parsed_json = json.loads(json_string)
        temp = None
        icon_url = None
        if 'current_observation' in parsed_json:
            temp = parsed_json["current_observation"]["temp_f"]
            icon_url = parsed_json["current_observation"]["icon_url"]
        else:
            g = urllib2.urlopen("http://api.wunderground.com/api/e6bf60cfa7a98a56/conditions/q/IL/chicago.json")
            json_string = g.read()
            parsed_json = json.loads(json_string)
            temp = parsed_json["current_observation"]["temp_f"]
            icon_url = parsed_json["current_observation"]["icon_url"]

        events_objects = BusinessEvent.objects.filter(business__community__url_name=community_object.url_name).filter(
            date_begin__gte=datetime.datetime.now().date()).order_by('date_begin')
        print name
        return render_to_response(
            'discover.html',
            {
                'community': community_object,
                'communities': Community.objects.all(),
                'temperature': temp,
                'image': '%s' % icon_url,
                'event': randomizer(events_objects, 0),
                'partners': Partner.objects.filter(community=community_object)
            },
            context_instance=RequestContext(request)
        )


@csrf_exempt
def api_communities(request):
    if request.method == "GET":
        if 'community' in request.GET:
            lista_business = []
            communities_var = request.GET['community']
            communities_split = communities_var.split("|")
            if communities_var.find("|") != -1:
                for i in communities_split:
                    community_object = Community.objects.get(url_name=i)
                    business_objects = Business.objects.filter(community=community_object)
                    for j in business_objects:
                        dict_biz = {
                            'name': j.name,
                            'url_name': j.url_name,
                            'auth_code': j.getUniqueCode()
                        }
                        lista_business.append(dict_biz)
            else:
                community_object = Community.objects.get(url_name=communities_var)
                business_objects = Business.objects.filter(community=community_object)
                for j in business_objects:
                    dict_biz = {
                        'name': j.name,
                        'url_name': j.url_name,
                        'auth_code': j.getUniqueCode()
                    }
                    lista_business.append(dict_biz)
            return HttpResponse(simplejson.dumps(lista_business))


def landing_partner(request, name=None):
    if name:
        community_object = Community.objects.get(url_name=name)
        partner_object = Partner.objects.get(url_name=request.GET['name'])
        landing_partner_object = LandingPartner.objects.get(partner_parent=partner_object)
        business_objects = landing_partner_object.partner_parent.business.all()
        events_objects = BusinessEvent.objects.filter(business__community__url_name=name).filter(
            date_begin__gte=datetime.datetime.now().date()).order_by('date_begin').order_by('date_begin').reverse()
        category_object = Category.objects.all()
        if request.META.has_key('HTTP_USER_AGENT'):
            user_agent = request.META['HTTP_USER_AGENT']
            pattern = "(up.browser|up.link|mmp|symbian|smartphone|midp|wap|phone|windows ce|pda|mobile|mini|palm|netfront)"
            prog = re.compile(pattern, re.IGNORECASE)
            match = prog.search(user_agent)
            if match:
                return render_to_response(
                    'landing-partner-m.html',
                    {
                        'landing_info': landing_partner_object,
                        'q': business_objects.count() / 8,
                        'categories': category_object,
                        'communities': Community.objects.all(),
                        'community': community_object,
                        'events': randomizer(events_objects, 2),
                        'partner': partner_object
                    },
                    context_instance=RequestContext(request)
                )
            else:
                return render_to_response(
                    'landing-partner.html',
                    {
                        'landing_info': landing_partner_object,
                        'q': business_objects.count() / 8,
                        'categories': category_object,
                        'communities': Community.objects.all(),
                        'community': community_object,
                        'events': randomizer(events_objects, 2),
                        'partner': partner_object
                    },
                    context_instance=RequestContext(request)
                )


def randomizer(pool_objects, number_views):
    if len(pool_objects) > 0:
        pool = list(pool_objects)
        random.shuffle(pool)
        if number_views == 0:
            list_objects = pool[number_views]
            return list_objects
        else:
            list_objects = pool[:number_views]
            return list_objects
    else:
        return False


def landing_page(request, name=None):
    if name:
        community_object = Community.objects.get(url_name=name)
        if request.META.has_key('HTTP_USER_AGENT'):
            user_agent = request.META['HTTP_USER_AGENT']
            pattern = "(up.browser|up.link|mmp|symbian|smartphone|midp|wap|phone|windows ce|pda|mobile|mini|palm|netfront)"
            prog = re.compile(pattern, re.IGNORECASE)
            match = prog.search(user_agent)
            if match:
                landing_page_object = LandingPage.objects.get(community=community_object)
                category_object = Category.objects.all()
                business_objects = Business.objects.filter(community=community_object).order_by('category')
                reviews_from_day = Review.objects.filter(business__community__url_name=name).filter(
                    date=datetime.datetime.now().date())
                rates = None
                if reviews_from_day.count() > 0:
                    rates = [i + 1 for i in range(randomizer(reviews_from_day, 0).stars)],
                else:
                    rates = ''
                events_objects = BusinessEvent.objects.filter(business__community__url_name=name).filter(
                    date_begin__gte=datetime.datetime.now().date()).order_by('date_begin')
                return render_to_response(
                    'landing-mobile.html',
                    {
                        'community': community_object,
                        'landing_info': landing_page_object,
                        'categories': category_object,
                        'businesses': business_objects,
                        'q': business_objects.count() / 8,
                        'review': randomizer(reviews_from_day, 0),
                        'stars': rates,
                        'events': randomizer(events_objects, 2),
                        'communities': Community.objects.all()
                    },
                    context_instance=RequestContext(request)
                )
            else:
                landing_page_object = LandingPage.objects.get(community=community_object)
                category_object = Category.objects.all()
                business_objects = Business.objects.filter(community=community_object).order_by('category')
                reviews_from_day = Review.objects.filter(business__community__url_name=name).filter(
                    date=datetime.datetime.now().date())
                rates = None
                if reviews_from_day.count() > 0:
                    rates = [i + 1 for i in range(randomizer(reviews_from_day, 0).stars)],
                else:
                    rates = ''
                events_objects = BusinessEvent.objects.filter(business__community__url_name=name).filter(
                    date_begin__gte=datetime.datetime.now().date()).order_by('date_begin')
                return render_to_response(
                    'landing.html',
                    {
                        'landing_info': landing_page_object,
                        'categories': category_object,
                        'businesses': business_objects,
                        'q': business_objects.count() / 8,
                        'review': randomizer(reviews_from_day, 0),
                        'stars': rates,
                        'events': randomizer(events_objects, 2),
                        'communities': Community.objects.all(),
                        'community': community_object,
                    },
                    context_instance=RequestContext(request)
                )


def getVideoDialog(request, videoId):
    if videoId:
        return render_to_response(
            'video-landing.html',
            {
                'videoId': videoId
            },
            context_instance=RequestContext(request)
        )


def qr_landing_page(request, name):
    if request.method == "GET":
        if 'code' in request.GET:
            args = {
                'client_id': settings.FACEBOOK_APP_ID,
                'redirect_uri': "http://" + request.META['HTTP_HOST'] + request.META['PATH_INFO'] + "?name=" +
                                request.GET["name"] + "&auth_code=" + request.GET["auth_code"],
                'client_secret': settings.FACEBOOK_APP_SECRET,
                'code': request.GET.get('code')
            }
            url = 'https://graph.facebook.com/oauth/access_token?' + \
                  urllib.urlencode(args)
            response = urlparse.parse_qs(urllib.urlopen(url).read())
            access_token = response['access_token'][0]
            expires = response['expires'][0]
            face = Facebook()
            user_face = face.authenticate(access_token, None, expires)
            request.session['user'] = user_face
            request.session.set_expiry(3600)
            request.session.modified = True
            return HttpResponseRedirect(
                "http://" + request.META['HTTP_HOST'] + request.META['PATH_INFO'] + "?name=" + request.GET[
                    "name"] + "&auth_code=" + request.GET["auth_code"])
        if request.META.has_key('HTTP_USER_AGENT'):
            user_agent = request.META['HTTP_USER_AGENT']
            pattern = "(up.browser|up.link|mmp|symbian|smartphone|midp|wap|phone|windows ce|pda|mobile|mini|palm|netfront)"
            prog = re.compile(pattern, re.IGNORECASE)
            match = prog.search(user_agent)
            community_object = Community.objects.get(url_name=name)
            try:
                business_object = Business.objects.get(id=int(decode_url(request.GET["auth_code"])),
                                                       url_name=request.GET["name"])
                events_biz_objects = BusinessEvent.objects.filter(business=business_object).filter(
                    date_begin__gte=datetime.datetime.now().date()).order_by('date_begin')
            except Business.DoesNotExist:
                raise Http404
            if match:
                return render_to_response(
                    'landing-qr.html',
                    {
                        'business': business_object,
                        'events': events_biz_objects,
                        'communities': Community.objects.all().order_by('name')
                    },
                    context_instance=RequestContext(request)
                )
            else:
                return HttpResponseRedirect(business_object.get_absolute_url())


def getBusiness(request, name):
    if request.method == "GET":
        tab = False
        if 'code' in request.GET:
            args = {
                'client_id': settings.FACEBOOK_APP_ID,
                'redirect_uri': "http://" + request.META['HTTP_HOST'] + request.META['PATH_INFO'] + "?name=" +
                                request.GET["name"] + "&auth_code=" + request.GET["auth_code"],
                'client_secret': settings.FACEBOOK_APP_SECRET,
                'code': request.GET.get('code')
            }
            url = 'https://graph.facebook.com/oauth/access_token?' + \
                  urllib.urlencode(args)
            response = urlparse.parse_qs(urllib.urlopen(url).read())
            access_token = response['access_token'][0]
            expires = response['expires'][0]
            face = Facebook()
            user_face = face.authenticate(access_token, None, expires)
            request.session['user'] = user_face
            request.session.set_expiry(3600)
            request.session.modified = True
            return HttpResponseRedirect(
                "http://" + request.META['HTTP_HOST'] + request.META['PATH_INFO'] + "?name=" + request.GET[
                    "name"] + "&auth_code=" + request.GET["auth_code"])
        if request.META.has_key('HTTP_USER_AGENT'):
            user_agent = request.META['HTTP_USER_AGENT']
            pattern = "(up.browser|up.link|mmp|symbian|smartphone|midp|wap|phone|windows ce|pda|mobile|mini|palm|netfront)"
            prog = re.compile(pattern, re.IGNORECASE)
            match = prog.search(user_agent)
            community_object = Community.objects.get(url_name=name)
            popup = False
            if "pop" in request.session and "community" in request.session:
                if name == request.session["community"]:
                    popup = request.session["pop"]
                else:
                    popup = False
                    request.session["community"] = name
            else:
                request.session["pop"] = True
                request.session["community"] = name
                popup = False
            try:
                business_object = Business.objects.get(id=int(decode_url(request.GET["auth_code"])),
                                                       url_name=request.GET["name"])
            except Business.DoesNotExist:
                raise Http404

            if "tab" in request.GET:
                tab_split = request.GET["tab"].split("|")
                if len(tab_split) > 1:
                    tab = {
                        'tab': tab_split[0],
                        'subtab': tab_split[1]
                    }
                else:
                    tab = {
                        'tab': tab_split[0]
                    }
            if match:
                if 'type' in request.GET:
                    return render_to_response(
                        'landing-qr.html',
                        {
                            'business': business_object
                        },
                        context_instance=RequestContext(request)
                    )
                else:
                    return render_to_response(
                        'landing-qr.html',
                        {
                            'business': business_object
                        },
                        context_instance=RequestContext(request)
                    )
            else:
                url_name = name
                communities = Community.objects.filter(active=True)
                community_object = communities.get(url_name=url_name)
                category_object = Category.objects.all().order_by('id')
                service_object = Service.objects.all().order_by('name')
                try:
                    basedir = settings.MEDIA_ROOT
                    if community_object.has_css_file:
                        with open('%s/%s' % (basedir, str(community_object.css_file)), 'r') as f:
                            text_css = ""
                            for i in f:
                                text_css += i
                    else:
                        text_css = community_object.discover_css
                except Community.DoesNotExist:
                    text_css = community_object.discover_css
                form = FormCouponsRequest()
                return render_to_response('cBaseB.html', {
                    'communities': communities,
                    'community': community_object,
                    'categories': category_object,
                    'services': service_object,
                    'coupons_form': form,
                    'css': text_css,
                    'business': business_object,
                    'pop': popup,
                    'tab': tab
                }, context_instance=RequestContext(request))
    else:
        return Http404()


def testJson(request):
    return render_to_response('savings-template.html', RequestContext(request))


def qualify(bis):
    """
    cantidad de votos del negocio
    """
    review_object = Review.objects.filter(business=bis)
    cantidad = review_object.count()
    if not cantidad:
        return 0
    else:
        subTotal = 0
        for i in review_object:
            subTotal += i.stars
        total = float(subTotal) / float(cantidad)
        return round(total, 1)


def getIfVotes(primary, ipAddress):
    try:
        review_object = Review.objects.get(business__pk=primary, ip=ipAddress)
        return 1
    except Review.DoesNotExist:
        return 0


def getSuscription(item):
    subscription_object = Subscription.objects.filter(business=item)
    if subscription_object:
        if subscription_object.count() > 0:
            renew_subscription = subscription_object[subscription_object.count() - 1].auto_renew
            if renew_subscription:
                return 1
            else:
                date_subscription = subscription_object.filter(date_start__lte=datetime.datetime.today()).filter(
                    date_end__gte=datetime.datetime.today())
                if date_subscription:
                    return 1
                else:
                    return 0
    else:
        return 0


@csrf_exempt
def toCSV(request, name):
    if name:
        import csv

        response = HttpResponse(mimetype="text/csv")
        response['Content-Disposition'] = 'attachment; filename=%s-urls.csv' % name
        writer = csv.writer(response)
        category_objects = Category.objects.order_by('id')
        for i in category_objects:
            business_object = Business.objects.filter(category=i).filter(
                community__url_name=name).order_by("name")
            for j in business_object:
                writer.writerow(['%s' % j.name.encode("ascii", "ignore"),
                                 'http://www.detourmaps.com/communities/%s/map/business/?name=%s&auth_code=%s' % (
                                     name, j.url_name, encode_url(j.id))])
        return response


@csrf_exempt
def toAllCSV(request):
    import csv

    response = HttpResponse(mimetype="text/csv")
    response['Content-Disposition'] = 'attachment; filename=%s-urls.csv' % 'all'
    writer = csv.writer(response)
    business_object = Business.objects.all().order_by("name")
    for j in business_object:
        url_community = ""
        if j.community:
            url_community = j.community.url_name
        writer.writerow(['%s' % j.name.encode("ascii", "ignore"),
                         'http://www.detourmaps.com/communities/%s/map/business/?name=%s&auth_code=%s' % (
                             url_community, j.url_name, encode_url(j.id, 8))])
    return response


@csrf_exempt
def toCSVSuscription(request, name):
    if name:
        import csv
        response = HttpResponse(mimetype="text/csv")
        response['Content-Disposition'] = 'attachment; filename=%s-urls.csv' % name
        writer = csv.writer(response)
        category_objects = Category.objects.order_by('id')
        for i in category_objects:
            business_object = Business.objects.filter(category=i).filter(
                community__url_name=name).order_by("name")
            for j in business_object:
                writer.writerow(['%s' % j.name.encode("ascii", "ignore"),
                                 'http://www.detourmaps.com/community/%s/map/business/?name=%s&auth_code=%s' % (
                                     name, j.url_name, encode_url(j.id))])
        return response


@csrf_exempt
def getCodesBusiness(request):
    if request.method == "GET":
        import csv

        response = HttpResponse(mimetype="text/csv")
        response['Content-Disposition'] = 'attachment; filename=%s-urls.csv' % 'codes'
        writer = csv.writer(response)
        if 'community' in request.GET:
            lista_business = []
            communities_var = request.GET['community']
            communities_split = communities_var.split("|")
            if communities_var.find("|") != -1:
                for i in communities_split:
                    community_object = Community.objects.get(url_name=i)
                    business_objects = Business.objects.filter(community=community_object)
                    for j in business_objects:
                        writer.writerow(['%s' % j.name.encode("ascii", "ignore"),
                                         j.getUniqueCode()
                        ])
            else:
                community_object = Community.objects.get(url_name=communities_var)
                business_objects = Business.objects.filter(community=community_object)
                for j in business_objects:
                    writer.writerow(['%s' % j.name.encode("ascii", "ignore"),
                                     j.getUniqueCode()
                    ])
            return response


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


def get_deals(biz):
    """
    get deals if exist return the value of the field if not exist return false or field is None return False
    """
    if biz.local_deals:
        if biz.local_deals == "N":
            return False
        else:
            return biz.local_deals
    else:
        return False


def get_partner(biz):
    """
    get partner, if business belongs to partner
    """
    if biz.partner_set.all():
        return "%s Member" % biz.partner_set.all()[0].name
    else:
        return ""


def get_thumbnail_vists(image):
    thumbnailer = get_thumbnailer(image)
    thumb = thumbnailer.get_thumbnail({'size': (346, 231), 'crop': True})
    thumb = thumbnailer.get_thumbnail_name({'size': (346, 231), 'crop': True})
    return thumb


@csrf_exempt
def data(request, name):
    """
    """
    if name:
        categoria_object = Category.objects.all().order_by('id')
        service_object = Service.objects.all().order_by('id')
        community_object = Community.objects.get(url_name=name)
        dictionary_category = {}
        lista = []
        list_business_event = []
        dictionary_community = {
            'border': force_unicode(GEOSGeometry(community_object.borders).json)
        }
        for i in categoria_object:
            dictionary_detalle_categoria = {
                'name': i.name,
                'desc': force_unicode(i.description),
                'img': force_unicode(i.icon),
                'color': force_unicode(i.color)
            }
            business_object = Business.objects.filter(category=i).filter(
                community__url_name=name).order_by("name")
            lista_business = []

            for j in business_object:
                avg = qualify(j)
                #hasVote = getIfVotes(j.pk,request.META.get('REMOTE_ADDR', ''))
                ten_visits = False
                if j.tenvisitsbusiness_set.all().count() > 0:
                    ten_visits = get_thumbnail_vists(j.tenvisitsbusiness_set.all()[0].image)
                hasSubscription = getSuscription(j)
                if not j.EntryDetails():
                    dictionary_detalle_business = {
                        'id': j.id,
                        'name': j.name,
                        'desc': j.description,
                        'b2c': j.belongs2community,
                        'chamber_member': j.chamber_member,
                        'geo': force_unicode(j.geo),
                        'address': j.address,
                        'phones': j.phones,
                        'site': force_unicode(j.site),
                        'fb': force_unicode(j.facebook),
                        'tt': force_unicode(j.twitter),
                        'enable_comments': j.enable_comments,
                        'avg': avg,
                        #'vote':hasVote,
                        'logo': force_unicode(j.logo),
                        'video': '',
                        'video_title': '',
                        'ten_visit': ten_visits,
                        'video_description': j.video_description,
                        'subscription': hasSubscription,
                        'url': j.url_name + "/" + encode_url(j.id, 8),
                        'deals': get_deals(j),
                        'community': j.community.url_name,
                        'auth_code': j.getUniqueCode(),
                        'url_name': j.url_name,
                        'partner': get_partner(j)
                    }
                else:
                    entryDetails = j.EntryDetails()
                    dictionary_detalle_business = {
                        'id': j.id,
                        'name': j.name,
                        'desc': j.description,
                        'b2c': j.belongs2community,
                        'chamber_member': j.chamber_member,
                        'geo': force_unicode(j.geo),
                        'address': j.address,
                        'phones': j.phones,
                        'site': force_unicode(j.site),
                        'fb': force_unicode(j.facebook),
                        'tt': force_unicode(j.twitter),
                        'enable_comments': j.enable_comments,
                        'avg': avg,
                        #'vote':hasVote,
                        'logo': force_unicode(j.logo),
                        'video': j.parseId(),
                        'video_title': entryDetails.title.text,
                        'ten_visit': ten_visits,
                        'video_img_0': entryDetails.media.thumbnail[1].url,
                        'video_img_1': entryDetails.media.thumbnail[2].url,
                        'video_img_2': entryDetails.media.thumbnail[3].url,
                        'video_description': j.video_description,
                        'subscription': hasSubscription,
                        'url': j.url_name + "/" + encode_url(j.id, 8),
                        'deals': get_deals(j),
                        'community': j.community.url_name,
                        'auth_code': j.getUniqueCode(),
                        'url_name': j.url_name,
                        'partner': get_partner(j)
                    }
                lista_tag_services = []
                for tag in j.tag_service.all():
                    lista_tag_services.append(str(tag.id))
                lista_images_business = []
                lista_cupon_business = []
                image_business_object = ImageBusiness.objects.filter(business=j)
                for img in image_business_object:
                    thumbnailer = get_thumbnailer(img.img)
                    thumb = thumbnailer.get_thumbnail({'size': (215, 198), 'crop': True})
                    thumb = thumbnailer.get_thumbnail_name({'size': (215, 198), 'crop': True})
                    dictionary_image_business = {
                        'name': img.name,
                        'img': thumb
                    }
                    lista_images_business.append(dictionary_image_business)

                cupon_business_object = CuponBusiness.objects.filter(business=j, active=1)
                for img in cupon_business_object:
                    thumbnailer = get_thumbnailer(img.coupon)
                    thumb = thumbnailer.get_thumbnail({'size': (420, 200), 'crop': True})
                    thumb = thumbnailer.get_thumbnail_name({'size': (420, 200), 'crop': True})
                    medium_thumb = thumbnailer.get_thumbnail({'size': (720, 400), 'crop': True})
                    medium_thumb = thumbnailer.get_thumbnail_name({'size': (720, 400), 'crop': True})
                    small_thumb = thumbnailer.get_thumbnail({'size': (280, 120), 'crop': True})
                    small_thumb = thumbnailer.get_thumbnail_name({'size': (280, 120), 'crop': True})
                    dictionary_cupon_business = {
                        'id': img.id,
                        'name': img.name,
                        'img': thumb,
                        'medium': medium_thumb,
                        'small': small_thumb,
                        'start_date': img.start_date.strftime('%m/%d/%Y'),
                        'end_date': img.end_date.strftime('%m/%d/%Y')
                    }
                    lista_cupon_business.append(dictionary_cupon_business)

                dictionary_detalle_business['img'] = lista_images_business
                dictionary_detalle_business['cupon'] = lista_cupon_business
                dictionary_detalle_business['tags'] = lista_tag_services
                lista_business.append(dictionary_detalle_business)

                #begin = datetime.datetime.now().strftime('%Y-%m-%d')
                #end = (datetime.datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
                business_events = BusinessEvent.objects.filter(business__id=j.id, active=True).filter(date_end__gte=datetime.datetime.now().date())
                for evt in business_events:
                    img_business_event = ImageBusinessEvents.objects.filter(business_event=evt)
                    list_img_business_event = []
                    for img_evt in img_business_event:
                        thumbn = get_thumbnailer(img_evt.img)
                        thumb = thumbn.get_thumbnail({'size': (215, 215), 'crop': True})
                        thumb = thumbn.get_thumbnail_name({'size': (215, 215), 'crop': True})
                        dictionary_image_business_event = {
                            'name': img_evt.name,
                            'img': settings.MEDIA_URL + thumb
                        }
                        list_img_business_event.append(dictionary_image_business_event)
                    return_date = lambda date_evt: date_evt or ''
                    if evt.date_end:
                        list_business_event.append({
                            'id': j.id,
                            'name': j.name,
                            'title': evt.title,
                            'description': evt.description,
                            'facebook': evt.facebook,
                            'twitter': evt.twitter,
                            'google_plus': evt.google_plus,
                            'images': list_img_business_event,
                            'date': {
                                'str': force_unicode(return_date(evt.date_begin.strftime('%b %d'))),
                                'end': force_unicode(return_date(evt.date_end.strftime('%b %d'))),
                                'day': force_unicode(return_date(evt.date_begin.strftime('%d'))),
                                'month': force_unicode(return_date(evt.date_begin.strftime('%m'))),
                                'year': force_unicode(return_date(evt.date_begin.strftime('%Y'))),
                            },
                            'geo': force_unicode(evt.geo),
                            'address': evt.address,
                            'url': "event/" + base64.urlsafe_b64encode(str(evt.id))
                        })
                    else:
                        list_business_event.append({
                            'id': j.id,
                            'name': j.name,
                            'title': evt.title,
                            'description': evt.description,
                            'facebook': evt.facebook,
                            'twitter': evt.twitter,
                            'google_plus': evt.google_plus,
                            'images': list_img_business_event,
                            'date': {
                                'str': force_unicode(return_date(evt.date_begin.strftime('%b %d'))),
                                'end': '',
                                'day': force_unicode(return_date(evt.date_begin.strftime('%d'))),
                                'month': force_unicode(return_date(evt.date_begin.strftime('%m'))),
                                'year': force_unicode(return_date(evt.date_begin.strftime('%Y'))),
                            },
                            'geo': force_unicode(evt.geo),
                            'address': evt.address,
                            'url': "event/" + base64.urlsafe_b64encode(str(evt.id))
                        })
                del business_events

            dictionary_detalle_categoria['bis'] = lista_business
            lista.append(dictionary_detalle_categoria)
        lista_tag_id = []
        dictionary_tag = {}
        for tag in service_object:
            dictionary_detalle_tag = {
                'name': tag.name,
                'icon': force_unicode(tag.icon),
                'color': tag.color,
                'desc': tag.description
            }
            dictionary_tag[tag.id] = dictionary_detalle_tag
            lista_tag_id.append(dictionary_tag)

        dictionary_category['cat'] = lista
        dictionary_category['tags'] = dictionary_tag
        dictionary_category['community'] = dictionary_community
        dictionary_category['events'] = list_business_event
        return HttpResponse(simplejson.dumps(dictionary_category), mimetype='application/json')


def getUrlCommunity(biz):
    if biz.community:
        return biz.community.url_name
    else:
        return ''


@csrf_exempt
def alldata(request):
    """
    """
    categoria_object = Category.objects.all().order_by('id')
    service_object = Service.objects.all().order_by('id')
    dictionary_category = {}
    lista = []
    list_business_event = []
    for i in categoria_object:
        dictionary_detalle_categoria = {
            'name': i.name,
            'desc': force_unicode(i.description),
            'img': force_unicode(i.icon),
            'color': force_unicode(i.color)
        }
        business_object = Business.objects.filter(category=i).order_by("name")
        lista_business = []

        for j in business_object:
            avg = qualify(j)
            #hasVote = getIfVotes(j.pk,request.META.get('REMOTE_ADDR', ''))
            hasSubscription = getSuscription(j)
            dictionary_detalle_business = {
                'id': j.id,
                'url': j.get_absolute_url(),
                'name': j.name,
                'address': j.address
            }
            lista_tag_services = []
            for tag in j.tag_service.all():
                lista_tag_services.append(str(tag.id))
            lista_images_business = []
            lista_cupon_business = []
            image_business_object = ImageBusiness.objects.filter(business=j)
            for img in image_business_object:
                thumbnailer = get_thumbnailer(img.img)
                thumb = thumbnailer.get_thumbnail({'size': (215, 198), 'crop': True})
                thumb = thumbnailer.get_thumbnail_name({'size': (215, 198), 'crop': True})
                dictionary_image_business = {
                    'name': img.name,
                    'img': thumb
                }
                lista_images_business.append(dictionary_image_business)

            cupon_business_object = CuponBusiness.objects.filter(business=j)
            for img in cupon_business_object:
                thumbnailer = get_thumbnailer(img.img)
                thumb = thumbnailer.get_thumbnail({'size': (420, 200), 'crop': True})
                thumb = thumbnailer.get_thumbnail_name({'size': (420, 200), 'crop': True})
                medium_thumb = thumbnailer.get_thumbnail({'size': (720, 400), 'crop': True})
                medium_thumb = thumbnailer.get_thumbnail_name({'size': (720, 400), 'crop': True})
                dictionary_cupon_business = {
                    'name': img.name,
                    'img': thumb,
                    'medium': medium_thumb
                }
                lista_cupon_business.append(dictionary_cupon_business)

            dictionary_detalle_business['img'] = lista_images_business
            dictionary_detalle_business['cupon'] = lista_cupon_business
            dictionary_detalle_business['tags'] = lista_tag_services
            lista_business.append(dictionary_detalle_business)

            begin = datetime.datetime.now().strftime('%Y-%m-%d')
            end = (datetime.datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            business_events = BusinessEvent.objects.raw(
                '''SELECT * FROM community_businessevent cb
                WHERE cb.business_id=%s and cb.active=true
                and (cb.date_begin between '%s' and '%s'
                OR cb.date_end between '%s' and '%s'
                OR '%s' between cb.date_begin and cb.date_end
                OR '%s' between cb.date_begin and cb.date_end)''' % (j.id, begin, end, begin, end, begin, end))
            #if len(business_events) > 0:
            for evt in business_events:
                img_business_event = ImageBusinessEvents.objects.filter(business_event=evt)
                list_img_business_event = []
                for img_evt in img_business_event:
                    thumbn = get_thumbnailer(img_evt.img)
                    thumb = thumbn.get_thumbnail({'size': (215, 215), 'crop': True})
                    thumb = thumbn.get_thumbnail_name({'size': (215, 215), 'crop': True})
                    dictionary_image_business_event = {
                        'name': img_evt.name,
                        'img': settings.MEDIA_URL + thumb
                    }
                    list_img_business_event.append(dictionary_image_business_event)
                return_date = lambda date_evt: date_evt or ''
                if evt.date_end:
                    list_business_event.append({
                        'id': j.id,
                        'name': j.name,
                        'title': evt.title,
                        'description': evt.description,
                        'facebook': evt.facebook,
                        'twitter': evt.twitter,
                        'google_plus': evt.google_plus,
                        'images': list_img_business_event,
                        'date': {
                            'str': force_unicode(return_date(evt.date_begin.strftime('%b %d'))), #%m-%d-%Y
                            'end': force_unicode(return_date(evt.date_end.strftime('%b %d'))),
                            'day': force_unicode(return_date(evt.date_begin.strftime('%d'))),
                            'month': force_unicode(return_date(evt.date_begin.strftime('%m'))),
                            'year': force_unicode(return_date(evt.date_begin.strftime('%Y'))),
                        },
                        'geo': force_unicode(evt.geo),
                        'address': evt.address,
                        'url': "event/" + base64.urlsafe_b64encode(str(evt.id))
                    })
                else:
                    list_business_event.append({
                        'id': j.id,
                        'name': j.name,
                        'title': evt.title,
                        'description': evt.description,
                        'facebook': evt.facebook,
                        'twitter': evt.twitter,
                        'google_plus': evt.google_plus,
                        'images': list_img_business_event,
                        'date': {
                            'str': force_unicode(return_date(evt.date_begin.strftime('%b %d'))), #%m-%d-%Y
                            'end': '',
                            'day': force_unicode(return_date(evt.date_begin.strftime('%d'))),
                            'month': force_unicode(return_date(evt.date_begin.strftime('%m'))),
                            'year': force_unicode(return_date(evt.date_begin.strftime('%Y'))),
                        },
                        'geo': force_unicode(evt.geo),
                        'address': evt.address,
                        'url': "event/" + base64.urlsafe_b64encode(str(evt.id))
                    })
            del business_events

        dictionary_detalle_categoria['bis'] = lista_business
        lista.append(dictionary_detalle_categoria)
    lista_tag_id = []
    dictionary_tag = {}
    for tag in service_object:
        dictionary_detalle_tag = {
            'name': tag.name,
            'icon': force_unicode(tag.icon),
            'color': tag.color,
            'desc': tag.description
        }
        dictionary_tag[tag.id] = dictionary_detalle_tag
        lista_tag_id.append(dictionary_tag)

    dictionary_category['cat'] = lista
    dictionary_category['tags'] = dictionary_tag
    dictionary_category['events'] = list_business_event
    return HttpResponse(simplejson.dumps(dictionary_category), mimetype='application/json')


@csrf_exempt
def dataIndividual(request):
    """
        function for unique url for a business
    """
    if "name" in request.GET:
        business_object = Business.objects.filter(name=request.GET['name'])
        dictionary_business = {
            'bi': business_object[0].pk,
            'ci': "0"
        }
        return HttpResponse(simplejson.dumps(dictionary_business))


@csrf_exempt
def rate_business(request):
    if request.method == "POST":
        business_object = Business.objects.get(id=int(request.POST['bis']))
        try:
            last_review = Review.objects.order_by('-date').filter(business=business_object, user=request.user)[0].date
        except Exception:
            last_review = datetime.date.today() - timedelta(days=30)
        diff = datetime.date.today() - datetime.date(last_review.year, last_review.month, last_review.day)
        if business_object.enable_comments and int(diff.days) >= business_object.rate_interval:
            comment = request.POST['comment'] or None
            stars = int(request.POST['stars'])
            review = Review.objects.create(user=request.user, business=business_object, stars=stars, comment=comment)
            obj = {
                'id': review.id,
                'username': review.user.username,
                'comment': review.comment,
                'stars': review.stars
            }
            return HttpResponse(simplejson.dumps(obj), mimetype='application/json')
        else:
            return HttpResponseBadRequest(content='This Business does not allow comments.')


@csrf_exempt
def getRattingBusiness(request):
    if request.method == 'POST':
        business_object = Business.objects.get(name__contains=request.POST['bis'])
        cantidad_votos = qualify(business_object)
        return HttpResponse(cantidad_votos)
    else:
        return 0


def getBusinessReview(request):
    if request.method == "GET":
        business_object = Business.objects.get(id=int(request.GET['bis']))
        reviews = Review.objects.order_by('-date').filter(business=business_object, enable=True)[0:50]

        reviews_list = []
        for obj in reviews:
            reviews_list.append({
                'id': obj.id,
                'username': obj.user.username,
                'comment': obj.comment,
                'stars': obj.stars,
                'date': obj.date.strftime("%m-%d-%Y")
            })

        return HttpResponse(simplejson.dumps(reviews_list), mimetype='application/json')


def getitem(request):
    if request.method == "GET":
        business_object = Business.objects.get(id=int(request.GET['bis']))
        obj = {
            'id': business_object.id,
            'name': business_object.name,
            'geo': str(business_object.geo)
        }
    return HttpResponse(simplejson.dumps(obj), mimetype='application/json')


def mobile(request):
    community_object = Community.objects.all()
    return render_to_response('mobile.html', {'communities': community_object},
                              context_instance=RequestContext(request))


@csrf_exempt
def get_session(request):
    dict_response = {}
    uid = None
    if request.method == "GET":
        if request.session.session_key:
            session_object = Session.objects.get(session_key=request.session.session_key)
            uid = session_object.get_decoded().get('_auth_user_id')
            if uid is not None:
                print "uid"
                try:
                    user_objects = User.objects.get(pk=uid)
                    dict_response["session"] = True
                    dict_response["id"] = user_objects.id
                    dict_response["username"] = user_objects.username
                    dict_response["email"] = user_objects.email
                    img_default = "http://www.detourmaps.com/static/web/img/detourIcon.png"
                    size = 40
                    gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(
                        user_objects.email.lower()).hexdigest() + "?"
                    gravatar_url += urllib.urlencode({'d': img_default, 's': str(size)})
                    dict_response["gravatar"] = gravatar_url
                except User.DoesNotExist:
                    print "sin user"
                    dict_response["session"] = False
            else:
                if 'user' in request.session:
                    print "usuario"
                    user_objects = request.session["user"]
                    dict_response["session"] = True
                    dict_response["id"] = user_objects.id
                    dict_response["username"] = user_objects.username
                    dict_response["email"] = user_objects.email
                    img_default = "http://www.detourmaps.com/static/web/img/detourIcon.png"
                    size = 40
                    gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(
                        user_objects.email.lower()).hexdigest() + "?"
                    gravatar_url += urllib.urlencode({'d': img_default, 's': str(size)})
                    dict_response["gravatar"] = gravatar_url
                else:
                    print "sin user"
                    dict_response["session"] = False
        elif 'user' in request.session:
            print "user"
            user_objects = request.session["user"]
            dict_response["session"] = True
            dict_response["id"] = user_objects.id
            dict_response["username"] = user_objects.username
            dict_response["email"] = user_objects.email
            img_default = "http://www.detourmaps.com/static/web/img/detourIcon.png"
            size = 40
            gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(user_objects.email.lower()).hexdigest() + "?"
            gravatar_url += urllib.urlencode({'d': img_default, 's': str(size)})
            dict_response["gravatar"] = gravatar_url
        else:
            print "without"
            dict_response["session"] = False
        return HttpResponse(simplejson.dumps(dict_response))


@csrf_exempt
def set_review(request):
    uid = None
    if request.method == "GET":
        biz_object = Business.objects.get(id=int(decode_url(request.GET["tag"])))
        if uid is not None:
            session_object = Session.objects.get(session_key=request.session.session_key)
            uid = session_object.get_decoded().get('_auth_user_id')
            user_objects = User.objects.get(pk=uid)
            review_object = Review(
                user=user_objects,
                business=biz_object,
                comment=request.GET["commentBiz"],
                stars=request.GET["rateBiz"],
            )
            review_object.save()
        else:
            user_objects = request.session["user"]
            review_object = Review(
                user=user_objects,
                business=biz_object,
                comment=request.GET["commentBiz"],
                stars=request.GET["rateBiz"],
            )
            review_object.save()
        dict_response = {
            'msg': 'Congratulations. Your review was saved!'
        }
        return HttpResponse(simplejson.dumps(dict_response))


@csrf_exempt
def share_by_email(request):
    if request.method == "GET":
        biz_object = Business.objects.get(id=int(decode_url(request.GET["tag"])))
        html = """\
        <html>
        <head></head>
        <body>
        <div style="position: relative; width: 600px; margin: auto;">
        <h1><img src="http://www.detourmaps.com/static/community/img/detourOrange.png"/></h1>
        <p>
        <h2>See %s</h2>
        <a href="http://www.detourmaps.com%s">View more information about this business here</a>
        </p>
        </div>
        </body>
        </html>
        """ % (biz_object.name, biz_object.get_absolute_url())
        requests.post(
            "https://api.mailgun.net/v2/detourmaps.mailgun.org/messages",
            auth=("api", "key-2dracu8lzgq16-4r8jugoslhe8r9q3a3"),
            data={"from": "Detour Maps <events@detourmaps.mailgun.org>",
                  "to": [request.GET["emailShared"], ],
                  "subject": "Detour Maps - %s" % biz_object.name,
                  "text": "Testing some Mailgun awesomness!",
                  "html": html}
        )
        dict_response = {
            'msg': 'Congratulations. Your shared is complete!'
        }
        return HttpResponse(simplejson.dumps(dict_response))


@csrf_exempt
def share_by_email_event(request):
    if request.method == "GET":
        event_object = BusinessEvent.objects.get(id=int(request.GET["tag"]))
        html = """\
        <html>
        <head></head>
        <body>
        <div style="position: relative; width: 600px; margin: auto;">
        <h1><img src="http://www.detourmaps.com/static/community/img/detourOrange.png"/></h1>
        <p>
        <h2>See %s</h2>
        <a href="http://www.detourmaps.com%s">View more information about this business here</a>
        </p>
        </div>
        </body>
        </html>
        """ % (event_object.title, event_object.get_absolute_url())
        requests.post(
            "https://api.mailgun.net/v2/detourmaps.mailgun.org/messages",
            auth=("api", "key-2dracu8lzgq16-4r8jugoslhe8r9q3a3"),
            data={"from": "Detour Maps <events@detourmaps.mailgun.org>",
                  "to": [request.GET["emailShared"], ],
                  "subject": "Detour Maps - %s" % event_object.title,
                  "text": "Testing some Mailgun awesomness!",
                  "html": html}
        )
        dict_response = {
            'msg': 'Congratulations. Your shared is complete!'
        }
        return HttpResponse(simplejson.dumps(dict_response))


@csrf_exempt
def share_direction_by_email(request):
    if request.method == "GET":
        biz_object = Business.objects.get(id=int(decode_url(request.GET["tag"])))
        html = """\
        <html>
        <head></head>
        <body>
        <div style="position: relative; width: 600px; margin: auto;">
        <h1><img src="http://www.detourmaps.com/static/community/img/detourOrange.png"/></h1>
        <p>
        <h2>How to get to %s</h2>
        <a href="https://maps.google.com/maps?saddr=%s&daddr=%s">Get the direction</a>
        </p>
        </div>
        </body>
        </html>
        """ % (biz_object.name, request.GET["saddr"], request.GET["daddr"])
        requests.post(
            "https://api.mailgun.net/v2/detourmaps.mailgun.org/messages",
            auth=("api", "key-2dracu8lzgq16-4r8jugoslhe8r9q3a3"),
            data={"from": "Detour Maps <directions@detourmaps.mailgun.org>",
                  "to": [request.GET["emailShared"], ],
                  "subject": "Detour Maps - %s - Get Direction" % biz_object.name,
                  "text": "Sending directions by email",
                  "html": html}
        )
        dict_response = {
            'msg': 'Congratulations. Your shared is complete!'
        }
        return HttpResponse(simplejson.dumps(dict_response))


@csrf_exempt
def share_direction_by_email_event(request):
    if request.method == "GET":
        event_object = BusinessEvent.objects.get(id=int(request.GET["tag"]))
        html = """\
        <html>
        <head></head>
        <body>
        <div style="position: relative; width: 600px; margin: auto;">
        <h1><img src="http://www.detourmaps.com/static/community/img/detourOrange.png"/></h1>
        <p>
        <h2>How to get to %s</h2>
        <a href="https://maps.google.com/maps?saddr=%s&daddr=%s">Get the direction</a>
        </p>
        </div>
        </body>
        </html>
        """ % (event_object.title, request.GET["saddr"], request.GET["daddr"])
        requests.post(
            "https://api.mailgun.net/v2/detourmaps.mailgun.org/messages",
            auth=("api", "key-2dracu8lzgq16-4r8jugoslhe8r9q3a3"),
            data={"from": "Detour Maps <directions@detourmaps.mailgun.org>",
                  "to": [request.GET["emailShared"], ],
                  "subject": "Detour Maps - %s - Get Direction" % event_object.title,
                  "text": "Sending directions by email",
                  "html": html}
        )
        dict_response = {
            'msg': 'Congratulations. Your shared is complete!'
        }
        return HttpResponse(simplejson.dumps(dict_response))


@csrf_exempt
def get_events_by_biz_or_by_date(request):
    if request.method == "GET":
        return_phone = lambda event_date: event_date or ''
        if "date" in request.GET:
            biz_object = Business.objects.get(id=int(decode_url(request.GET["tag"])))
            events_objects = BusinessEvent.objects.filter(business=biz_object).filter(date_begin=request.GET["date"]).order_by("date_begin")
            list_events = []
            dict_events = None
            if events_objects.count() > 0:
                dict_events = {
                    'msg': True,
                    'Q': events_objects.count()
                }
                for i in events_objects:
                    dict_event = {
                        'title': i.title,
                        'description': i.description,
                        'address': i.address,
                        'date': i.date_begin.strftime('%B %d'),
                        'phone': force_unicode(return_phone(i.phone))
                    }
                    list_events.append(dict_event)
                dict_events['lists'] = list_events
            else:
                dict_events = {
                    'msg': False,
                    'Q': 0,
                    'biz': biz_object.name
                }
            return HttpResponse(simplejson.dumps(dict_events))
        else:
            biz_object = Business.objects.get(id=int(decode_url(request.GET["tag"])))
            events_objects = BusinessEvent.objects.filter(business=biz_object).filter(
                date_begin__gte=datetime.datetime.now().date()).order_by("date_begin")
            list_events = []
            dict_events = None
            if events_objects.count() > 0:
                dict_events = {
                    'msg': True,
                    'Q': events_objects.count()
                }
                for i in events_objects:
                    dict_event = {
                        'title': i.title,
                        'description': i.description,
                        'address': i.address,
                        'date': i.date_begin.strftime('%B %d'),
                        'phone': force_unicode(return_phone(i.phone))
                    }
                    list_events.append(dict_event)
                dict_events['lists'] = list_events
            else:
                dict_events = {
                    'msg': False,
                    'Q': 0,
                    'biz': biz_object.name
                }
            return HttpResponse(simplejson.dumps(dict_events))


Sesion = {}


@csrf_exempt
def LoginAccount(request):
    #Logeo con Google+
    if request.POST and request.POST.get('user_type') == 'G':
        try:
            user = TipoUsuario.objects.get(usuario__user__username=request.POST.get('username'))
            request.session['user'] = user.usuario.user
            print request.session["user"]
            Sesion['estado'] = True

        except TipoUsuario.DoesNotExist:
            name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('username')
            accessToken = request.POST.get('access_token')
            expires = request.POST.get('expires')
            user_id = request.POST.get('user_id')
            user_type = request.POST.get('user_type')
            try:
                user = User.objects.get(username=email)
                request.session['user'] = user
                usuario_object = Usuario(
                    user=user
                )
                usuario_object.save()
                userGoogle = TipoUsuario(
                    usuario=usuario_object,
                    access_token=accessToken,
                    expires=expires,
                    userid=user_id,
                )
                userGoogle.save()
                usuario_object.tipo_usuario = userGoogle.id
                usuario_object.save()
                Sesion['estado'] = True
            except User.DoesNotExist:
                user = User()
                user.first_name = name
                user.username = email
                user.last_name = last_name
                user.email = email
                user.is_active = True
                user.set_unusable_password()
                user.save()
                request.session['user'] = user
                usuario_object = Usuario(
                    user=user
                )
                usuario_object.save()
                userGoogle = TipoUsuario(
                    usuario=usuario_object,
                    access_token=accessToken,
                    expires=expires,
                    userid=user_id,
                )
                userGoogle.save()
                usuario_object.tipo_usuario = userGoogle.id
                usuario_object.save()
                request.session['user'] = user
                Sesion['estado'] = True
    #Logeo con Twitter
    elif 'oauth_token' in request.GET:
        twitter = Twitter()
        twitter.verify(request)
        user = twitter.get_user_data(request)
        request.session['user'] = user
        request.session.set_expiry(3600)
        request.session.modified = True
        Sesion['estado'] = True
        return HttpResponse('<script>window.history.go(-3)</script>')

    #Logeo con Facebook
    elif 'code' in request.GET:
        args = {
            'client_id': settings.FACEBOOK_APP_ID,
            #'redirect_uri': "http://" + request.META['HTTP_HOST'] + request.META['PATH_INFO'] + "?name=" +
            #                request.GET["name"] + "&auth_code=" + request.GET["auth_code"],
            'redirect_uri': settings.FACEBOOK_REDIRECT_URI,
            'client_secret': settings.FACEBOOK_APP_SECRET,
            'code': request.GET.get('code')
        }
        url = 'https://graph.facebook.com/oauth/access_token?' + \
              urllib.urlencode(args)
        response = urlparse.parse_qs(urllib.urlopen(url).read())
        access_token = response['access_token'][0]
        expires = response['expires'][0]
        face = Facebook()
        user_face = face.authenticate(access_token, None, expires)
        Sesion['estado'] = True
        request.session['user'] = user_face
        request.session.set_expiry(3600)
        request.session.modified = True
        return HttpResponse('<script>window.history.go(-3)</script>')
    #Logeo nativo
    elif request.POST:
        username = request.POST.get('user_email')
        password = request.POST.get('user_password')
        user = authenticate(username=username, password=password)
        dict_response = {}
        if user is not None:
            if user.is_active:
                login(request, user)
                request.session["user"] = user
                print request.session["user"]
                Sesion['estado'] = True
                dict_response['state'] = True
                return HttpResponse(simplejson.dumps(dict_response))
            else:
                dict_response['msg'] = "User is not active, you need to activate your account"
                dict_response['state'] = False
                return HttpResponse(simplejson.dumps(dict_response))
                # Return a 'disabled account' error message
        else:
            #No hay concordancia entre user y password
            dict_response['msg'] = "The email and/or the password were incorrect"
            dict_response['state'] = False
            return HttpResponse(simplejson.dumps(dict_response))

    return render_to_response(
        "login-user.html",
        {
            'communities': Community.objects.all(),
        },
        context_instance=RequestContext(request)
    )


def getSessionTwitter(request):
    twitter = Twitter()
    response = twitter.get_authorization_url()
    cad = response.split("=")
    dato = cad[len(cad) - 1]
    dictionary = {}
    dictionary['datos'] = dato
    return HttpResponse(simplejson.dumps(dictionary))


def getSessionFacebook(request):
    facebook = Facebook()
    response = facebook.refresh_token()
    dictionary = {}
    dictionary['datos'] = response
    return HttpResponse(simplejson.dumps(dictionary))


def endSession(request):
    try:
        del request.session['user']
    except KeyError:
        pass
    return HttpResponseRedirect(reverse('/'))


@csrf_exempt
def RegisterUser(request):
    if request.POST:
        dictionary = {}
        try:
            user = Usuario.objects.get(user__username=request.POST.get('user_email'), user_type='N')
            dictionary['state'] = False
            dictionary['msg'] = "This email is already been used, try with other"
            return HttpResponse(simplejson.dumps(dictionary))

        except Usuario.DoesNotExist:

            email = request.POST.get('user_email')
            user = User.objects.create_user(email, email, request.POST.get("user_password"))

            user.is_active = False
            user.save()

            userNativo = Usuario()
            userNativo.user = user
            userNativo.access_token = email
            userNativo.userid = email
            userNativo.user_type = 'N'
            userNativo.save()

            html_user = loader.get_template("/home/adrian/work/detourmaps/community/templates/registration.html")
            context_user = Context({'link': 'www.facebook.com'})
            subject_user, from_user, to_user = 'Registration DetourMaps', 'Detour Maps <info@detourmaps.com>', user.email
            user_context_html = html_user.render(context_user)
            message_user = EmailMessage(subject_user, user_context_html, from_user, [to_user])
            message_user.content_subtype = "html"
            message_user.send()

            dictionary['state'] = True
            dictionary['msg'] = "Now activate your account, and you're ready to go!!!"
            return HttpResponse(simplejson.dumps(dictionary))

    return render_to_response(
        "register-user.html",
        {
            'communities': Community.objects.all(),
        },
        context_instance=RequestContext(request)
    )


@csrf_exempt
@login_required(login_url='/community/loginUser/')
def AccountSettings(request):
    userAccount = request.session['user']
    email = userAccount.username
    password = userAccount.password

    dictionary = {}

    if request.POST:
        oldpassword = request.POST.get('oldPassword')
        newpassword = request.POST.get('newPassword')
        newemail = request.POST.get('newEmail')

        user = User.objects.get(username=email)

        if newpassword == "":
            user.email = newemail
            user.username = newemail
        else:
            if user.check_password(oldpassword):
                if newemail == "":
                    user.set_password(newpassword)
                elif newemail != "" and newpassword != "":
                    user.set_password(newpassword)
                    user.username = newemail
                    user.email = newemail
            else:
                dictionary['state'] = False
                dictionary['msg'] = 'The original password is wrong'
                return HttpResponse(simplejson.dumps(dictionary))
        user.save()
        dictionary['state'] = True
        return HttpResponse(simplejson.dumps(dictionary))
    return render_to_response("account-settings.html", {'user': userAccount, 'community': Community.objects.all()},
                              context_instance=RequestContext(request))


def join_us(request):
    return render_to_response(
        'join_us.html',
        {
            'communities': Community.objects.all(),
        },
        context_instance=RequestContext(request)
    )


def printed_maps(request):
    return render_to_response(
        'printed_maps.html',
        {
            'communities': Community.objects.all(),
        },
        context_instance=RequestContext(request)
    )


def printed_maps_new(request):
    return render_to_response(
        'printed-map.html',
        {},
        context_instance=RequestContext(request)
    )


def savings_card(request):
    return render_to_response(
        'savings-card.html',
        {},
        context_instance=RequestContext(request)
    )


def business_card(request, name=None):
    return render_to_response(
        'business-card.html',
        {
            'name': name
        },
        context_instance=RequestContext(request)
    )


def offline(request):
    return render_to_response(
        'offline.html',
        {
            'categories': Category.objects.all()
        },
        context_instance=RequestContext(request)
    )


def number_landing_to_community(request):
    phone_landing = PhoneNumber.objects.all()
    for i in phone_landing:
        new_phone = PNumber(
            text=i.text,
            landing_page=i.landing_page.community
        )
        new_phone.save()
    return HttpResponse("OK, The change was made!")


def inline_landing_to_community(request):
    social_objects = LandingSocial.objects.all()
    header_objects = HeaderPage.objects.all()
    text_objects = LandingText.objects.all()
    video_objects = WVideo.objects.all()
    for i in social_objects:
        new_social = CommunitySocial(
            type_social=i.type_social,
            url=i.url,
            community=i.landing_page.community
        )
        new_social.save()
    for j in header_objects:
        new_header = HeaderCommunity(
            caption=j.caption,
            image=j.image,
            community=j.landing_page.community
        )
        new_header.save()
    for k in text_objects:
        new_text = CommunityText(
            image=k.image,
            title=k.title,
            text=k.text,
            community=k.landing_page.community
        )
        new_text.save()
    for l in video_objects:
        new_video = Video(
            url_video=l.url_video,
            text=l.text,
            community=l.landing_page.community
        )
        new_video.save()
    return HttpResponse("Back Up was made!")


def handler404(request):
    response = render_to_response('404.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 404
    return response


def handler500(request):
    response = render_to_response('500.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 500
    return response


def category_json(request):
    categories_object = Category.objects.all().order_by('name')
    lista_categories = []
    for i in categories_object:
        dict_cat = {
            'id': i.id,
            'name': i.name
        }
        lista_categories.append(dict_cat)
    return HttpResponse(simplejson.dumps(lista_categories))


def community_json(request):
    community_object = Community.objects.filter(active=True).order_by('name')
    lista_communities = []
    for i in community_object:
        dict_community = {
            'id': i.id,
            'name': i.name
        }
        lista_communities.append(dict_community)
    return HttpResponse(simplejson.dumps(lista_communities))


def business_json(request, page, slice):
    business_objects = Business.objects.all()[int(page):int(slice)]
    lista_business = []
    return_community = lambda biz_community: biz_community or ''
    return_category = lambda biz_category: biz_category or ''
    comm_id = ""
    cat_id = ""
    for i in business_objects:
        if i.community:
            comm_id = i.community.id
        if i.category:
            cat_id = i.category.id
        dict_business = {
            'id': i.id,
            'name': i.name,
            'url_name': i.get_absolute_url(),
            'local_deals': i.local_deals,
            'ten_off': i.ten_off,
            'smart_buys': i.smart_buys,
            'ten_visits': i.ten_visits,
            'refer_friends': i.refer_friends,
            'community': comm_id,
            'category': cat_id,
            'description': force_unicode(i.description)
        }
        lista_business.append(dict_business)
    return HttpResponse(simplejson.dumps(lista_business))


def all_business_json(request):
    community_object = Community.objects.filter(active=True).order_by('name')
    lista_communities = []
    for i in community_object:
        dict_community = {
            'id': i.id,
            'name': i.name
        }
        lista_communities.append(dict_community)#communities
    categories_object = Category.objects.all().order_by('name')
    lista_categories = []
    for i in categories_object:
        dict_cat = {
            'id': i.id,
            'name': i.name
        }
        lista_categories.append(dict_cat)#categories
    business_objects = Business.objects.all().order_by('name')
    lista_business = []
    return_community = lambda biz_community: biz_community or ''
    return_category = lambda biz_category: biz_category or ''
    comm_id = ""
    cat_id = ""
    comm_name = ""
    image = ""
    ten_off = False
    smart_buys = False
    for i in business_objects:
        if i.community:
            comm_id = i.community.id
            comm_name = i.community.name
        if i.category: cat_id = i.category.id
        if i.imagebusiness_set.all():
            thumbnailer = get_thumbnailer(i.imagebusiness_set.all()[0].img)
            image = thumbnailer.get_thumbnail({'size': (300, 120), 'crop': True})
            image = thumbnailer.get_thumbnail_name({'size': (300, 120), 'crop': True})
        else:
            image = ""
        local_deals = {}
        if i.cuponbusiness_set.filter(active=1).count() > 0:
            smart_buys = True
        if i.local_deals == "T":
            local_deals["msg"] = "$10 Savings Card"
            local_deals["icon"] = "icon-yellow.png"
            local_deals["none"] = False
            ten_off = True
        elif i.local_deals == "F":
            local_deals["msg"] = "$10 Savings Card"
            local_deals["icon"] = "icon-red.png"
            local_deals["none"] = False
            ten_off = True
        elif i.local_deals == "Q":
            local_deals["msg"] = "$10 Savings Card"
            local_deals["icon"] = "icon-sky.png"
            local_deals["none"] = False
            ten_off = True
        else:
            local_deals["none"] = True
            ten_off = False
        dict_business = {
            'id': i.id,
            'name': i.name,
            'url_name': i.get_absolute_url(),
            'local_deals': local_deals,
            'ten_off': ten_off,
            'smart_buys': smart_buys,
            'ten_visits': i.ten_visits,
            'refer_friends': i.refer_friends,
            'community': comm_id,
            'community_name': comm_name,
            'category': cat_id,
            'description': force_unicode(i.description),
            'image': force_unicode(image),
            'url': force_unicode(i.get_absolute_url())
        }
        lista_business.append(dict_business)
    biz = Business.objects.filter(Q(local_deals='T') | Q(local_deals="Q") | Q(local_deals='F') | Q(ten_visits=1)| Q(refer_friends=1)).order_by("?")[0]
    comm_biz_id = ""
    comm_biz_name = ""
    cat_biz_id = ""
    image_biz = ""
    smart_biz = False
    if biz.cuponbusiness_set.filter(active=1).count() > 0:
        smart_biz = True
    if biz.community:
        comm_biz_id = biz.community.id
        comm_biz_name = biz.community.name
        if biz.category: cat_biz_id = biz.category.id
        if biz.imagebusiness_set.all().count() > 0:
            thumbnailer = get_thumbnailer(biz.imagebusiness_set.all()[0].img)
            image_biz = thumbnailer.get_thumbnail({'size': (800, 180), 'crop': True})
            image_biz = thumbnailer.get_thumbnail_name({'size': (800, 180), 'crop': True})
        else:
            image_biz = ""
        local_deals_biz = {}
        if biz.local_deals == "T":
            local_deals_biz["msg"] = "$10 Savings Card"
            local_deals_biz["icon"] = "icon-yellow.png"
            local_deals_biz["none"] = False
        elif biz.local_deals == "F":
            local_deals_biz["msg"] = "$10 Savings Card"
            local_deals_biz["icon"] = "icon-red.png"
            local_deals_biz["none"] = False
        elif biz.local_deals == "Q":
            local_deals_biz["msg"] = "$10 Savings Card"
            local_deals_biz["icon"] = "icon-sky.png"
            local_deals_biz["none"] = False
        else:
            local_deals_biz["none"] = True
        dict_biz = {
            'id': biz.id,
            'name': biz.name,
            'url_name': biz.get_absolute_url(),
            'local_deals': local_deals_biz,
            'ten_off': True,
            'smart_buys': smart_biz,
            'ten_visits': biz.ten_visits,
            'refer_friends': biz.refer_friends,
            'community': comm_biz_id,
            'community_name': comm_biz_name,
            'category': cat_biz_id,
            'description': force_unicode(biz.description),
            'image': force_unicode(image_biz),
            'url': force_unicode(biz.get_absolute_url())
        }
    dict_super_dupper = {
        'communities': lista_communities,
        'categories': lista_categories,
        'businesses': lista_business,
        'business': dict_biz
    }
    return HttpResponse(simplejson.dumps(dict_super_dupper))


def all_business_community_json(request, url_name):
    categories_object = Category.objects.all().order_by('name')
    lista_categories = []
    for i in categories_object:
        dict_cat = {
            'id': i.id,
            'name': i.name
        }
        lista_categories.append(dict_cat)#categories
    business_objects = Business.objects.filter(community__url_name=url_name).order_by('name')
    lista_business = []
    return_community = lambda biz_community: biz_community or ''
    return_category = lambda biz_category: biz_category or ''
    comm_id = ""
    cat_id = ""
    comm_name = ""
    image = ""
    ten_off = False
    smart_buys = False
    for i in business_objects:
        if i.community:
            comm_id = i.community.id
            comm_name = i.community.name
        if i.category: cat_id = i.category.id
        if i.imagebusiness_set.all():
            thumbnailer = get_thumbnailer(i.imagebusiness_set.all()[0].img)
            image = thumbnailer.get_thumbnail({'size': (300, 120), 'crop': True})
            image = thumbnailer.get_thumbnail_name({'size': (300, 120), 'crop': True})
        else:
            image = ""
        local_deals = {}
        if i.cuponbusiness_set.filter(active=1).count() > 0:
            smart_buys = True
        if i.local_deals == "T":
            local_deals["msg"] = "$10 Savings Card"
            local_deals["icon"] = "icon-yellow.png"
            local_deals["none"] = False
            ten_off = True
        elif i.local_deals == "F":
            local_deals["msg"] = "$10 Savings Card"
            local_deals["icon"] = "icon-red.png"
            local_deals["none"] = False
            ten_off = True
        elif i.local_deals == "Q":
            local_deals["msg"] = "$10 Savings Card"
            local_deals["icon"] = "icon-sky.png"
            local_deals["none"] = False
            ten_off = True
        else:
            local_deals["none"] = True
            ten_off = False
        dict_business = {
            'id': i.id,
            'name': i.name,
            'url_name': i.get_absolute_url(),
            'local_deals': local_deals,
            'ten_off': ten_off,
            'smart_buys': smart_buys,
            'ten_visits': i.ten_visits,
            'refer_friends': i.refer_friends,
            'community': comm_id,
            'community_name': comm_name,
            'category': cat_id,
            'description': force_unicode(i.description),
            'image': force_unicode(image),
            'url': force_unicode(i.get_absolute_url())
        }
        lista_business.append(dict_business)
    dict_super_dupper = {
        'categories': lista_categories,
        'businesses': lista_business,
    }
    return HttpResponse(simplejson.dumps(dict_super_dupper))


def all_business_deals_json(request):
    community_object = Community.objects.filter(active=True).order_by('name')
    lista_communities = []
    for i in community_object:
        dict_community = {
            'id': i.id,
            'name': i.name
        }
        lista_communities.append(dict_community)#communities
    categories_object = Category.objects.all().order_by('name')
    lista_categories = []
    for i in categories_object:
        dict_cat = {
            'id': i.id,
            'name': i.name
        }
        lista_categories.append(dict_cat)#categories
    business_objects = Business.objects.filter(Q(local_deals='T') | Q(local_deals="Q") | Q(local_deals='F') | Q(ten_visits=1)| Q(refer_friends=1))
    lista_business = []
    return_community = lambda biz_community: biz_community or ''
    return_category = lambda biz_category: biz_category or ''
    comm_id = ""
    cat_id = ""
    comm_name = ""
    image = ""
    smart = False
    for i in business_objects:
        if i.cuponbusiness_set.filter(active=1).count() > 0:
            smart = True
        if i.community:
            comm_id = i.community.id
            comm_name = i.community.name
        if i.category: cat_id = i.category.id
        if i.imagebusiness_set.all():
            thumbnailer = get_thumbnailer(i.imagebusiness_set.all()[0].img)
            image = thumbnailer.get_thumbnail({'size': (300, 120), 'crop': True})
            image = thumbnailer.get_thumbnail_name({'size': (300, 120), 'crop': True})
        else:
            image = ""
        local_deals = {}
        if i.local_deals == "T":
            local_deals["msg"] = "$10 Savings Card"
            local_deals["icon"] = "icon-yellow.png"
            local_deals["color"] = "FFF100"
            local_deals["none"] = False
        elif i.local_deals == "F":
            local_deals["msg"] = "$10 Savings Card"
            local_deals["icon"] = "icon-red.png"
            local_deals["color"] = "D71F26"
            local_deals["none"] = False
        elif i.local_deals == "Q":
            local_deals["msg"] = "$10 Savings Card"
            local_deals["icon"] = "icon-sky.png"
            local_deals["color"] = "00ADEE"
            local_deals["none"] = False
        else:
            local_deals["none"] = True
        dict_business = {
            'id': i.id,
            'name': i.name,
            'url_name': i.get_absolute_url(),
            'local_deals': local_deals,
            'ten_off': True,
            'smart_buys': smart,
            'ten_visits': i.ten_visits,
            'refer_friends': i.refer_friends,
            'community': comm_id,
            'community_name': comm_name,
            'category': cat_id,
            'description': force_unicode(i.description),
            'image': force_unicode(image),
            'url': force_unicode(i.get_absolute_url())
        }
        lista_business.append(dict_business)
    biz = Business.objects.filter(Q(local_deals='T') | Q(local_deals="Q") | Q(local_deals='F') | Q(ten_visits=1)| Q(refer_friends=1)).order_by("?")[0]
    comm_biz_id = ""
    comm_biz_name = ""
    cat_biz_id = ""
    image_biz = ""
    smart_biz = False
    if biz.cuponbusiness_set.filter(active=1).count() > 0:
        smart_biz = True
    if biz.community:
        comm_biz_id = biz.community.id
        comm_biz_name = biz.community.name
        if biz.category: cat_biz_id = biz.category.id
        if biz.imagebusiness_set.all().count() > 0:
            thumbnailer = get_thumbnailer(biz.imagebusiness_set.all()[0].img)
            image_biz = thumbnailer.get_thumbnail({'size': (800, 180), 'crop': 'smart'})
            image_biz = thumbnailer.get_thumbnail_name({'size': (800, 180), 'crop': 'smart'})
        else:
            image_biz = ""
        local_deals_biz = {}
        if biz.local_deals == "T":
            local_deals_biz["msg"] = "$10 Savings Card"
            local_deals_biz["icon"] = "icon-yellow.png"
            local_deals_biz["none"] = False
        elif biz.local_deals == "F":
            local_deals_biz["msg"] = "$10 Savings Card"
            local_deals_biz["icon"] = "icon-red.png"
            local_deals_biz["none"] = False
        elif biz.local_deals == "Q":
            local_deals_biz["msg"] = "$10 Savings Card"
            local_deals_biz["icon"] = "icon -sky.png"
            local_deals_biz["none"] = False
        else:
            local_deals_biz["none"] = True
        dict_biz = {
            'id': biz.id,
            'name': biz.name,
            'url_name': biz.get_absolute_url(),
            'local_deals': local_deals_biz,
            'ten_off': True,
            'smart_buys': smart_biz,
            'ten_visits': biz.ten_visits,
            'refer_friends': biz.refer_friends,
            'community': comm_biz_id,
            'community_name': comm_biz_name,
            'category': cat_biz_id,
            'description': force_unicode(biz.description),
            'image': force_unicode(image_biz),
            'url': force_unicode(biz.get_absolute_url())
        }
    dict_super_dupper = {
        'communities': lista_communities,
        'categories': lista_categories,
        'businesses': lista_business,
        'business': dict_biz
    }
    return HttpResponse(simplejson.dumps(dict_super_dupper))


def all_business_savings_json(request):
    community_object = Community.objects.filter(active=True).order_by('name')
    lista_communities = []
    for i in community_object:
        dict_community = {
            'id': i.id,
            'name': i.name
        }
        lista_communities.append(dict_community)#communities
    categories_object = Category.objects.all().order_by('name')
    lista_categories = []
    for i in categories_object:
        dict_cat = {
            'id': i.id,
            'name': i.name
        }
        lista_categories.append(dict_cat)#categories
    business_objects = Business.objects.filter(Q(local_deals='T') | Q(local_deals="Q") | Q(local_deals='F'))
    lista_business = []
    return_community = lambda biz_community: biz_community or ''
    return_category = lambda biz_category: biz_category or ''
    comm_id = ""
    cat_id = ""
    cat_name = ""
    comm_name = ""
    image = ""
    for i in business_objects:
        if i.community:
            comm_id = i.community.id
            comm_name = i.community.name
        if i.category:
            cat_id = i.category.id
            cat_name = i.category.name
        if i.imagebusiness_set.all():
            thumbnailer = get_thumbnailer(i.imagebusiness_set.all()[0].img)
            image = thumbnailer.get_thumbnail({'size': (300, 120), 'crop': True})
            image = thumbnailer.get_thumbnail_name({'size': (300, 120), 'crop': True})
        else:
            image = ""
        local_deals = {}
        if i.local_deals == "T":
            local_deals["msg"] = "$10 Savings Card"
            local_deals["icon"] = "icon-yellow.png"
            local_deals["color"] = "FFF100"
            local_deals["none"] = False
        elif i.local_deals == "F":
            local_deals["msg"] = "$10 Savings Card"
            local_deals["icon"] = "icon-red.png"
            local_deals["color"] = "D71F26"
            local_deals["none"] = False
        elif i.local_deals == "Q":
            local_deals["msg"] = "$10 Savings Card"
            local_deals["icon"] = "icon-sky.png"
            local_deals["color"] = "00ADEE"
            local_deals["none"] = False
        else:
            local_deals["none"] = True
        dict_business = {
            'id': i.id,
            'name': i.name,
            'url_name': i.get_absolute_url(),
            'local_deals': local_deals,
            'ten_off': i.ten_off,
            'smart_buys': i.smart_buys,
            'ten_visits': i.ten_visits,
            'refer_friends': i.refer_friends,
            'community': comm_id,
            'community_name': comm_name,
            'category': cat_id,
            'category_name': cat_name,
            'description': force_unicode(i.description),
            'image': force_unicode(image),
            'url': force_unicode(i.get_absolute_url())
        }
        lista_business.append(dict_business)
    biz = Business.objects.filter(Q(local_deals='T') | Q(local_deals="Q") | Q(local_deals='F') | Q(smart_buys=1) | Q(ten_off=1) | Q(ten_visits=1)| Q(refer_friends=1)).order_by("?")[0]
    comm_biz_id = ""
    comm_biz_name = ""
    cat_biz_id = ""
    image_biz = ""
    if biz.community:
        comm_biz_id = biz.community.id
        comm_biz_name = biz.community.name
        if biz.category: cat_biz_id = biz.category.id
        if biz.imagebusiness_set.all().count() > 0:
            thumbnailer = get_thumbnailer(biz.imagebusiness_set.all()[0].img)
            image_biz = thumbnailer.get_thumbnail({'size': (800, 180), 'crop': 'smart'})
            image_biz = thumbnailer.get_thumbnail_name({'size': (800, 180), 'crop': 'smart'})
        else:
            image_biz = ""
        local_deals_biz = {}
        if biz.local_deals == "T":
            local_deals_biz["msg"] = "$10 Savings Card"
            local_deals_biz["icon"] = "icon-yellow.png"
            local_deals_biz["none"] = False
        elif biz.local_deals == "F":
            local_deals_biz["msg"] = "$10 Savings Card"
            local_deals_biz["icon"] = "icon-red.png"
            local_deals_biz["none"] = False
        elif biz.local_deals == "Q":
            local_deals_biz["msg"] = "$10 Savings Card"
            local_deals_biz["icon"] = "icon -sky.png"
            local_deals_biz["none"] = False
        else:
            local_deals_biz["none"] = True
        dict_biz = {
            'id': biz.id,
            'name': biz.name,
            'url_name': biz.get_absolute_url(),
            'local_deals': local_deals_biz,
            'ten_off': biz.ten_off,
            'smart_buys': biz.smart_buys,
            'ten_visits': biz.ten_visits,
            'refer_friends': biz.refer_friends,
            'community': comm_biz_id,
            'community_name': comm_biz_name,
            'category': cat_biz_id,
            'description': force_unicode(biz.description),
            'image': force_unicode(image_biz),
            'url': force_unicode(biz.get_absolute_url())
        }
    dict_super_dupper = {
        'communities': lista_communities,
        'categories': lista_categories,
        'businesses': lista_business,
        'business': dict_biz
    }
    return HttpResponse(simplejson.dumps(dict_super_dupper))


def get_community_json(request):
    community_objects = Community.objects.all().order_by('name')
    list_community = []
    for i in community_objects:
        list_partner = []
        dict_community = {
            'name': i.name,
            'img_map': force_unicode(i.img_printed_map),
            'print_map': force_unicode(i.printed_map),
        }
        for j in i.partner_set.all():
            dict_partner = {
                'name': j.name,
                'url_name': force_unicode(j.get_absolute_url())
            }
            list_partner.append(dict_partner)
        dict_community['partners'] = list_partner
        list_community.append(dict_community)
    return HttpResponse(simplejson.dumps(list_community))


@csrf_protect
def save_newsletter_suscription(request):
    if request.method == "POST":
        if "suscribe" in request.POST:
            dict_response = {}
            try:
                news_object = Newsletter.objects.get(email=request.POST["suscribe"])
                dict_response['msg'] = 'Newsletter suscription exists!!!'
            except:
                news_object = Newsletter(
                    email=request.POST["suscribe"]
                )
                news_object.save()
                dict_response['msg'] = 'Newsletter suscription saved!!!'
        return HttpResponse(simplejson.dumps(dict_response))