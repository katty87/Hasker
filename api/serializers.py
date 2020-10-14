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
    answer_cnt = serializers.SerializerMethodField()
    vote_sum = serializers.SerializerMethodField()

    def get_answer_cnt(self, obj):
        return obj.answer_cnt

    def get_vote_sum(self, obj):
        return obj.vote_sum

    class Meta:
        model = Question
        fields = ['header', 'content', 'user', 'create_date', 'tags', 'answer_cnt', 'vote_sum']


class AnswerSerializer(serializers.HyperlinkedModelSerializer):
    user = UserProfileSerializer(many=False, read_only=True)
    vote_sum = serializers.SerializerMethodField()

    def get_vote_sum(self, obj):
        return obj.vote_sum

    class Meta:
        model = Answer
        fields = ['content', 'user', 'create_date', 'is_correct', 'vote_sum']
