from rest_framework import serializers

from main.models import Question, Answer, Tag
from user.models import UserProfile


class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'date_joined', 'is_superuser']


class TagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tag
        fields = ['name']


class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    user = UserProfileSerializer(many=False, read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['header', 'content', 'user', 'create_date', 'tags']


class AnswerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Answer
        fields = ('content', )
