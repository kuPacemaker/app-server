from rest_framework import serializers
from .models import *
from rest_framework.authtoken.models import Token

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('url_id','username','first_name')

class BKDSerializer(serializers.ModelSerializer):
    class Meta:
        model = BKD
        fields = ('url_id','title','body')

class BKDIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = BKD
        fields = ('id',)

class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = ('token',)

class ChannelIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ('url_id',)

class ChannelInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ('url_id','name','description','accesspath')

class QAPairSerializer(serializers.ModelSerializer):
    class Meta:
        model = QAPair
        fields = ('url_id','question','answer','answer_set')

class HostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Host
        fields = ('user','channel')

class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = ('user','channel')

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ('url_id','channel','index','name')
