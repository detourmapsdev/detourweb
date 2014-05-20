import httplib2
import simplejson
import urllib
from django.contrib.auth.models import User
from community.models import Usuario, TipoUsuario
from django.conf import settings
from web.views import getPasswordRandom
from web.models import UserProfile
from django.db import transaction
__author__ = 'mauricio'


class Facebook:

    def refresh_token(self):
        url = 'https://graph.facebook.com/oauth/authorize?client_id=%s&redirect_uri=%s&scope=publish_stream,email&display=popup' % (settings.FACEBOOK_APP_ID,settings.FACEBOOK_REDIRECT_URI)
        return url

    def authenticate(self,access_token=None,user=None,expires=None):
        user_object = None
        user_facebook = None
        try:
            url = 'https://graph.facebook.com/me?access_token=%s' \
                % access_token
            response = simplejson.load(urllib.urlopen(url))
            user_facebook = TipoUsuario.objects.get(
                userid=response['id']
            )
            profile = user_facebook.query()
            user_facebook.access_token = access_token
            user_facebook.expires = expires
            user_facebook.save()
            user_object = user_facebook.usuario.user
        except TipoUsuario.DoesNotExist:
            user_facebook = TipoUsuario.objects.get_or_create(
                access_token=access_token
            )
            profile = user_facebook[0].query()
            try:
                user_object = User.objects.get(username=profile['email'])
                usuario_parent = Usuario(
                    user=user_object
                )
                usuario_parent.save()
                user_facebook[0].expires = expires
                user_facebook[0].userid = profile['id']
                user_facebook[0].usuario = usuario_parent
                user_facebook[0].save()
                usuario_parent.tipo_usuario = user_facebook[0].id
                usuario_parent.save()
            except User.DoesNotExist:
                user_object = User()
                user_object.username = profile['email']
                user_object.set_unusable_password()
                user_object.backend = 'community.facebook.Facebook'
                user_object.first_name = profile['first_name']
                user_object.last_name = profile['last_name']
                user_object.email = profile['email']
                user_object.save()
                user_object.is_active = True
                user_object.is_staff = False
                user_object.is_superuser = False
                user_object.save()
                usuario_parent = Usuario(
                    user=user_object
                )
                usuario_parent.save()
                user_facebook[0].expires = expires
                user_facebook[0].userid = profile['id']
                user_facebook[0].usuario = usuario_parent
                user_facebook[0].save()
                usuario_parent.tipo_usuario = user_facebook[0].id
                usuario_parent.save()
        return user_object

    def authenticate_only_facebook(self,access_token=None):
        user_facebook = Usuario.objects.get(
            access_token=access_token
        )
        profile = user_facebook.query()
        try:
            user = Usuario.objects.get(user__username=profile['email'])
        except Usuario.DoesNotExist, e:
            user = User(username=profile['email'])

        user.set_unusable_password()
        user.backend='community.facebook.Facebook'
        user.email = profile['email']
        user.first_name = profile['first_name']
        user.last_name = profile['last_name']
        user.is_active = True
        user.save()

        try:
            Usuario.objects.get(userid=profile['id']).delete()
        except Usuario.DoesNotExist, e:
            pass

        user_facebook.uid = profile['id']
        user_facebook.user = user
        user_facebook.save()

        return user

    def createUserConect(self,access_token,user_connect):
        user_facebook = Usuario.objects.get(
            access_token=access_token
        )
        profile = user_facebook.query()
        user_facebook.userid = profile['id']
        print profile['id']
        user_facebook.user = user_connect
        user_facebook.save()

        return user_facebook

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
