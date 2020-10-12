from rest_framework import viewsets, renderers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.db.models import Exists, OuterRef

from api.serializers import QuestionSerializer, AnswerSerializer
from main.models import Question, Answer, Tag


class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        queryset = Question.objects.all().order_by('create_date')
        search_string = self.request.query_params.get('search', None)
        if search_string:
            queryset = queryset.filter(Q(header__icontains=search_string) | Q(content__icontains=search_string))

        tag_name = self.request.query_params.get('tag', None)
        if tag_name:
            queryset = queryset.filter(
                Exists(Tag.objects.filter(question=OuterRef('pk'), name=tag_name))
            )
        return queryset


class AnswerViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AnswerSerializer

    def get_queryset(self):
        return Answer.objects.filter(question=self.kwargs['questions_pk'])
