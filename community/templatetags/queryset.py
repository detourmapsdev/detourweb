# -*- coding: utf-8 -*-
__author__ = 'juancho'
import base64
import random
import datetime
from django.core.cache import cache
from django import template
from django.db.models import Count, Q
#models
from community.models import Community, Business, BusinessEvent, \
    Service, Partner, Category

from community.views import parseSpecialChar
from operator import itemgetter

register = template.Library()


@register.inclusion_tag('templatetags/list_community.html')
def list_community():
    community_objects = Community.objects.all()
    return {'community': community_objects}


@register.inclusion_tag('templatetags/menu-neighborhood.html')
def list_community_active():
    community_objects = Community.objects.filter(active=True)
    return {'community': community_objects}



@register.inclusion_tag('templatetags/list-community-footer.html')
def list_community_footer():
    community_objects = Community.objects.all()
    return {'community': community_objects}


@register.inclusion_tag('templatetags/list_communities_savings.html')
def list_community_savings():
    community_objects = Community.objects.all()
    return {'communities_savings': community_objects}


@register.inclusion_tag('templatetags/list_partners_by_community.html')
def list_partners(idCommunity):
    #TODO:trabajar con cache
    partner_object = Partner.objects.filter(community__pk=idCommunity).order_by(
        "name")
    return {'partners': partner_object}


@register.inclusion_tag('templatetags/list-partners-poop.html')
def list_partners_pop(idCommunity):
    #TODO:trabajar con cache
    partner_object = Partner.objects.filter(community__pk=idCommunity).filter(pop=1).order_by(
        "name")
    if partner_object:
        return {'partners': partner_object, 'content': True}
    else:
        return {'content': False}


@register.inclusion_tag('templatetags/list_business.html')
def list_business(idCommunity, idCategory):
    #TODO:trabajar con cache
    business_object = Business.objects.filter(category__pk=idCategory).filter(community__pk=idCommunity).order_by(
        "name")
    return {'businesses': business_object}


@register.inclusion_tag('templatetags/list_business_by_cat_m.html')
def list_business_cat_mobile(idCommunity, idCategory):
    #TODO:trabajar con cache
    business_object = Business.objects.filter(category__pk=idCategory).filter(community__pk=idCommunity).order_by(
        "name")
    return {'businesses': business_object}


@register.inclusion_tag('templatetags/list_service_by_category.html')
def listServiceByCategoryByBusiness(idCommunity, idCategory):
    business_object = Business.objects.filter(category__pk=idCategory).filter(community__pk=idCommunity).order_by("id")
    lista = []
    for bis in business_object:
        for service in bis.tag_service.all().order_by('-name'):
            lista.append(service)
    return {'services': set(lista)}


@register.inclusion_tag('templatetags/list_business_by_deals.html')
def listBusinessByDeals(idCommunity):
    list_business = []
    business_object = Business.objects.filter(community__pk=idCommunity).exclude(local_deals="N").order_by(
        "local_deals")
    for buss in business_object:
        list_business.append({
            'name': buss.name,
            'id': buss.id,
            'local_deals': buss.local_deals,
            'url': parseSpecialChar(buss.name) + "/" + base64.urlsafe_b64encode(str(buss.id))
        })
    community_object = Community.objects.get(pk=idCommunity)
    return {'businesses': list_business, 'community': community_object}


@register.inclusion_tag('templatetags/list_business_events.html')
def listBusinessEvents(idCommunity):
    list_business = []
    business_object = Business.objects.filter(community__pk=idCommunity)
    for bus in business_object:
        business_events = BusinessEvent.objects.filter(business=bus, active=True)
        if len(business_events) > 0:
            for evt in business_events:
                list_business.append({
                    'event': evt,
                    'obj': u'''{id:%s,geo:'%s',address:'%s',title:'%s',description:'%s',date:'%s'}''' % (
                        str(evt.id), evt.geo, evt.address, evt.title, evt.description, evt.date.strftime('%m-%d-%Y')),
                    'd_date': evt.date,
                    'date': evt.date.strftime('%m-%d-%Y'),
                    'url': parseSpecialChar(bus.name) + "/" + base64.urlsafe_b64encode(str(bus.id))
                })
    list_business.sort(key=itemgetter('d_date'))
    return {'events': list_business}


@register.inclusion_tag('templatetags/list_services.html')
def listServiceRandom():
    service_objects = Service.objects.distinct().filter(subcat=False)
    pool = list(service_objects)
    random.shuffle(pool)
    list_service = pool[:5]
    return {'services': list_service}


@register.filter(name='arrobe')
def arrobe(value):
    filtro = value.split("@")
    return filtro[0]


@register.inclusion_tag('templatetags/events_by_date_by_community.html')
def events_by_date_by_community(idCommunity):
    events_objects = BusinessEvent.objects.filter(
        date_begin__gt=datetime.datetime.now().date()
    ).filter(
        business__community__id=idCommunity
    )
    return {
        'events': events_objects
    }


@register.inclusion_tag('templatetags/community_deals.html')
def community_panel_mobile():
    community_objects = Community.objects.filter(Q(business__local_deals='T')|Q(business__local_deals='Q')|Q(business__local_deals='F'))
    return {
        'community': community_objects
    }


@register.inclusion_tag('templatetags/business_filter_mobile.html')
def business_filter_mobile():
    business_objects = Business.objects.all().order_by('name')
    return {
        'businesses' : business_objects
    }


@register.inclusion_tag('templatetags/list_service_mobile.html')
def service_community_category(idCategory, idCommunity):
    service_obejcts = Service.objects.filter(business__category__pk=idCategory, business__community__pk=idCommunity).filter(subcat=False).distinct()
    category_objects = Category.objects.get(pk=idCategory)
    return {
        'services': service_obejcts,
        'category': category_objects
    }


@register.inclusion_tag('templatetags/all_business_data.html')
def all_business_data():
    #result = cache.get('business')
    #if result is None:
    result = Business.objects.all().order_by('name')
    #cache.set('business', 'result')
    return {
        'business': result
    }
    #else:
    #    return {
    #        'business': result
    #    }