# games.views
from django.utils import dateparse
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status
from rest_framework.permissions import AllowAny

from .models import Game
from gamerooms.models import Gameroom
from .serializers import GameSerializer

class GameListCreateView(generics.ListCreateAPIView):
    permission_classes = (AllowAny, )
    serializer_class = GameSerializer

    def create(self, request, *args, **kwargs):
        reqUser = request.user
        if reqUser.groups.filter(name='admin').exists():
            return super(GameListCreateView, self).create(request, *args, **kwargs)
        else:
            username = reqUser.username
            userId = reqUser.id
            errMsg = "You are not allow to create game as {} (userId: {}).".format(username, userId)
            return Response(
                data={
                    "error": errMsg
                },
                status=status.HTTP_404_NOT_FOUND
            )

    def perform_create(self, serializer):
        request = self.request
        if request.data['gameEnd'] == '':
            gameroomId = request.data['gameroom']
            gameroom = Gameroom.objects.get(gameroomId=gameroomId)
            gameDuration = gameroom.defaultDuration
            gameStart = dateparse.parse_datetime(request.data['gameStart'])
            gameEnd = gameStart + gameDuration
            serializer.save(gameEnd=gameEnd)
        else:
            serializer.save()

    def get_queryset(self):
        gameroomId = self.request.data['gameroomId'] if 'gameroomId' in self.request.data else None
        if gameroomId:
            return Game.objects.filter(gameroomId=gameroomId)
        else:
            return Game.objects.all()
