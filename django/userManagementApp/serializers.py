from rest_framework import serializers
from .models import PlayerProfile
import os

class ProfilePictureSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()
    class Meta:
        model = PlayerProfile
        fields = ['id', 'profile_picture_url']
    
    def get_profile_picture_url(self, obj):
        if obj.profile_picture and hasattr(obj.profile_picture, 'path') and os.path.exists(obj.profile_picture.path):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None