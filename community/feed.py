
__author__ = 'mauricio'
from django.contrib.syndication.views import FeedDoesNotExist, Feed
from django.shortcuts import get_object_or_404

from community.models import Business, BusinessEvent


class LatestEntriesFeed(Feed):

    def get_object(self, request, business_id):
        return get_object_or_404(Business, pk=business_id)

    def title(self, obj):
        return "%s: Events for %s" % (obj.name, obj.name)

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return "Detour Maps: %s" % obj.name

    def items(self, obj):
        return BusinessEvent.objects.filter(business=obj).order_by('-date_begin')[:30]