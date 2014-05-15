import json
from community import tweepy
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from community.models import Usuario, TipoUsuario
from community.tweepy.parsers import RawParser
__author__ = 'brian'

TOKENS = {}


class Twitter:
    def get_authorization_url(self):

        # URL to where we will redirect to
        redirect_url = settings.TWITTER_REDIRECT_URL

        # create the handler
        auth = tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET,redirect_url)

        # get the authorization url (i.e. https://api.twitter.com/oauth/authorize?oauth_token=XXXXXXX)
        # this method automatically grabs the request token first
        # Note: must ensure a callback URL (can be any URL) is defined for the application at dev.twitter.com,
        #       otherwise this will fail (401 Unauthorized)
        try:
            url = auth.get_authorization_url()
        except tweepy.TweepError:
            # failed to get auth url (maybe twitter is down)
            url = reverse('index')
            return url

        # store the returned values
        TOKENS['twitter_request_token_key'] = auth.request_token.key
        TOKENS['twitter_request_token_secret'] = auth.request_token.secret

        return url

    def verify(self,request):
        # Twitter will direct with oauth_token and oauth_verifier in the URL
        # ?oauth_token=EoSsg1...&oauth_verifier=NB3bvAkb...

        # did the user deny the request

        if 'denied' in request.GET:

            return False

        # ensure we have a session state and the state value is the same as what twitter returned
        if 'twitter_request_token_key' not in TOKENS \
           or 'oauth_token' not in request.GET \
           or 'oauth_verifier' not in request.GET \
           or TOKENS['twitter_request_token_key'] != request.GET['oauth_token']:

            return False
        else:

            return True

    def get_user_data(self, request):

        data = {}

        # create the connection
        auth = tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
        #redirect_Url=auth.get_authorization_url()
        # set the token and verifier

        auth.set_request_token(request.GET['oauth_token'], request.GET['oauth_verifier'])
        # determine if we've already requested an access token
        if 'twitter_access_token_key' not in TOKENS:

            # get the access token
            access_token = auth.get_access_token(request.GET['oauth_verifier'])

            # update the stored values
            TOKENS['twitter_access_token_key'] = access_token.key
            TOKENS['twitter_access_token_secret'] = access_token.secret

        else:

            # set the access token
            auth.set_access_token(TOKENS['twitter_access_token_key'], TOKENS['twitter_access_token_secret'])

        api = tweepy.API(auth_handler=auth, parser=RawParser())

        user = json.loads(api.me())
        user_object_return = None
        try:
            user_twitter = TipoUsuario.objects.get(
                usuario__user__username=user['screen_name']
            )
            user_object_return = user_twitter.usuario.user
            profile = user_twitter.query()
            user_twitter.access_token = TOKENS['twitter_access_token_key']
            user_twitter.save()
        except TipoUsuario.DoesNotExist:
            user_twitter = TipoUsuario(
                access_token=access_token
            )
            user_twitter.save()
            profile = user_twitter.query()
            try:
                user_object = User.objects.get(username=user['screen_name'])
                user_twitter.expires = 3600
                user_twitter.userid = user['id']
                user_twitter.session_key = user['id']
                usuario_object = Usuario(
                    user=user_object,
                    tipo_usuario=user_twitter.id
                )
                usuario_object.save()
                user_twitter.usuario = usuario_object
                user_twitter.save()
            except User.DoesNotExist:
                user_object = User.objects.create_user(user['screen_name'])
                user_object.set_unusable_password()
                user_object.backend = 'community.twitter.Twitter'

                full_name = user['name'].split(' ', 1)

                user_object.first_name = full_name[0] if len(full_name) > 0 else ''
                user_object.last_name = full_name[1] if len(full_name) >= 2 else ''
                user_object.is_active = True
                user_object.save()
                user_twitter.expires = 3600
                user_twitter.userid = user['id']
                user_twitter.session_key = user['id']
                usuario_object = Usuario(
                    user=user_object,
                    tipo_usuario=user_twitter.id
                )
                usuario_object.save()
                user_twitter.usuario = usuario_object
                user_twitter.save()
                user_object_return = user_object
        return user_object_return


