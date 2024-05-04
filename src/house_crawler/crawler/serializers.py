from rest_framework.serializers import ModelSerializer

from crawler.models import Post


class PostSerializer(ModelSerializer):
    class Meta:
        model = Post
        exclude = ()
