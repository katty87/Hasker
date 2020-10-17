from rest_framework.pagination import PageNumberPagination

from Hasker.settings.base import QUESTIONS_PER_PAGE, ANSWERS_PER_PAGE


class QuestionPagination(PageNumberPagination):
    page_size = QUESTIONS_PER_PAGE
    page_size_query_param = 'page_size'
    max_page_size = 100


class AnswerPagination(PageNumberPagination):
    page_size = ANSWERS_PER_PAGE
    page_size_query_param = 'page_size'
    max_page_size = 100
