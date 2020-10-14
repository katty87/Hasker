from rest_framework import viewsets, renderers
from rest_framework import generics
from rest_framework.decorators import action
from rest_framework.pagination import CursorPagination
from rest_framework.response import Response
from django.db.models import Q
from django.db.models import Sum, Count, Exists, OuterRef
from django.db.models.functions import Coalesce

from api.paginators import QuestionPagination, AnswerPagination
from api.serializers import QuestionSerializer, AnswerSerializer, TrendingSerializer
from main.models import Question, Answer, Tag


class CustomQuestionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = QuestionSerializer
    pagination_class = QuestionPagination

    def filter(self, queryset):
        return queryset

    def orderby(self, queryset):
        return queryset

    def get_queryset(self):
        queryset = Question.objects.all()
        queryset = queryset \
            .annotate(answer_cnt=Count('answer', distinct=True),
                      vote_sum=Count('questionvote__id', fiter=~Q(questionvote__value=0), distinct=True))
        queryset = self.filter(queryset)
        return self.orderby(queryset)


class QuestionViewSet(CustomQuestionViewSet):
    def filter(self, queryset):
        search_string = self.request.query_params.get('search', None)
        if search_string:
            queryset = queryset.filter(Q(header__icontains=search_string) | Q(content__icontains=search_string))

        tag_name = self.request.query_params.get('tag', None)
        if tag_name:
            queryset = queryset.filter(
                Exists(Tag.objects.filter(question=OuterRef('pk'), name=tag_name))
            )

        return queryset

    def orderby(self, queryset):
        return queryset.order_by('-vote_sum', '-create_date')


class HotQuestionViewSet(CustomQuestionViewSet):
    def orderby(self, queryset):
        return queryset.order_by('-vote_sum', '-create_date')


class NewQuestionViewSet(CustomQuestionViewSet):
    def orderby(self, queryset):
        return queryset.order_by('-create_date', '-vote_sum', )


class AnswerViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AnswerSerializer
    pagination_class = AnswerPagination

    def get_queryset(self):
        return Answer.objects.filter(question_id=self.kwargs['questions_pk']) \
            .annotate(vote_sum=Coalesce(Sum('answervote__value'), 0)) \
            .order_by('-vote_sum', 'create_date')


class TrendingQuestionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TrendingSerializer
    queryset = Question.objects \
        .annotate(vote_sum=Coalesce(Sum('questionvote__value'), 0)) \
        .filter(vote_sum__gt=0)
    queryset = queryset.order_by('-vote_sum', 'create_date')[:20]

