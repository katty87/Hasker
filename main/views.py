import json
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.db.models import Q
from django.db.models import Sum, Count, When, Case, Exists, OuterRef
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.views import generic
from django.views.generic import ListView
from django.views.generic.edit import FormMixin, CreateView

from Hasker.settings.base import EMAIL_HOST_USER
from main.aggregates_extension import GroupConcat
from main.forms import AddQuestionForm, QuestionDetailForm
from main.models import Question, QuestionVote, Answer, AnswerVote, Tag
from user.models import UserProfile


class IndexView(generic.ListView):
    template_name = 'main/index.html'
    context_object_name = 'question_list'
    paginate_by = 20

    def get_queryset(self):
        order_by = ['-vote_sum', '-create_date'] if self.request.GET.get('ordering', '0') == '1' \
            else ['-create_date', '-vote_sum']

        qs = Question.objects.all() \
            .annotate(answer_cnt=Count('answer', distinct=True),
                      vote_sum=Count('questionvote__id', fiter=Q(questionvote__id=0), distinct=True),
                      tag_list=GroupConcat('tags__name', distinct=True)) \
            .order_by(*order_by) \
            .values('id', 'header', 'create_date', 'user__username', 'user__avatar',
                    'answer_cnt', 'vote_sum', 'tag_list')

        return qs

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context.update({'ordering': self.request.GET.get('ordering', '0')})

        return context

    def get(self, request, *args, **kwargs):
        response = super(IndexView, self).get(request, *args, **kwargs)
        return response


class SearchResultsView(generic.ListView):
    model = Question
    template_name = 'main/search_results.html'
    context_object_name = 'question_list'
    paginate_by = 20

    def get_queryset(self):
        search_string = self.request.GET.get('q', '').strip()

        if not search_string:
            queryset = Question.objects.all()
        else:
            words = search_string.split(':')
            if words[0].strip().lower() == 'tag':
                if len(words) == 1:
                    queryset = Question.objects.all()
                else:
                    queryset = Question.objects \
                        .filter(
                            Exists(Tag.objects.filter(question=OuterRef('pk'), name=words[1].strip().lower()))
                        )
            else:
                queryset = Question.objects \
                    .filter(Q(header__icontains=search_string) | Q(content__icontains=search_string))

        return queryset \
            .annotate(answer_cnt=Count('answer', distinct=True),
                      vote_sum=Count('questionvote__id', fiter=~Q(questionvote__value=0), distinct=True),
                      tag_list=GroupConcat('tags__name', distinct=True)) \
            .order_by('-vote_sum', '-create_date') \
            .values('id', 'header', 'create_date', 'user__username', 'user__avatar',
                    'answer_cnt', 'vote_sum', 'tag_list')

    def get_context_data(self, **kwargs):
        context = super(SearchResultsView, self).get_context_data(**kwargs)
        q = self.request.GET.get('q', '')
        context.update({'q': q})
        context.update({'tag_search': 1 if q.split(':')[0].strip().lower() == 'tag' else 0})

        return context


class AskQuestionView(LoginRequiredMixin, CreateView):
    model = Question
    template_name = 'main/add_question.html'
    form_class = AddQuestionForm

    def form_valid(self, form):
        question_instance = form.save(commit=False)

        question_instance.create_date = datetime.utcnow()
        question_instance.user = self.request.user
        question_instance.save()

        tags = form.data['tags'].split(',')
        for tag_name in tags:
            tag = Tag.objects.filter(name=tag_name).first()
            if not tag:
                tag = Tag()
                tag.name = tag_name
                tag.save()
            question_instance.tags.add(tag)

        if tags:
            question_instance.save()

        return redirect('question_detail', pk=question_instance.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = json.dumps(list(Tag.objects.all().values_list('name', flat=True)))
        return context


class QuestionDetailView(ListView, FormMixin):
    form_class = QuestionDetailForm
    model = Answer
    template_name = 'main/detail_question.html'
    context_object_name = 'answer_list'
    paginate_by = 30

    def get_queryset(self):
        if self.request.user:
            user_id = self.request.user.id
        else:
            user_id = -1

        return Answer.objects.filter(question_id=self.kwargs['pk']) \
            .annotate(vote_sum=Coalesce(Sum('answervote__value'), 0),
                      current_user_vote=Sum(
                          Case(When(answervote__user_id=user_id, then='answervote__value'), default=0))) \
            .order_by('-vote_sum', 'create_date').values('id', 'content', 'is_correct', 'user__username',
                                                         'user__avatar',
                                                         'vote_sum', 'current_user_vote')

    def get_context_data(self, **kwargs):
        if not self.request.user:
            return super(QuestionDetailView, self).get_context_data(**kwargs)

        user_id = self.request.user.id
        context = super(QuestionDetailView, self).get_context_data(**kwargs)

        pk = self.kwargs.get('pk', '')

        if pk:
            question = get_object_or_404(Question, pk=pk)
            context['question_vote'] = question.current_user_vote(user_id)
            context['question'] = question

        return context

    def post(self, request, *args, **kwargs):
        if not request.user:
            self.get(request, *args, **kwargs)

        form = self.get_form()

        if form.is_valid():
            question = get_object_or_404(Question, pk=self.kwargs.get('pk', ''))
            answer = Answer()
            answer.content = request.POST['answer_text']
            answer.question = question
            answer.create_date = datetime.utcnow()
            answer.is_correct = False
            answer.user = request.user
            answer.save()

            send_mail(
                'Hasker: new answer to your question',
                '',
                EMAIL_HOST_USER,
                [question.user.email],
                fail_silently=True,
                html_message=
                '<!DOCTYPE html><html><body>You have got a new answer to your question.\n '
                'If you would like to see it please click '
                '<a href="{full_url}">{full_url}</a>'
                '</body></html>'.format(full_url=request.META['HTTP_REFERER'])
            )
            return redirect('question_detail', pk=question.id)

        return self.get(request, *args, **kwargs)


@login_required
def vote_question(request):
    question_id = request.POST.get('question_id')
    value = request.POST.get('value')
    user_id = request.POST.get('user_id')

    try:
        question = Question.objects.get(pk=question_id)
        user = UserProfile.objects.get(pk=user_id)
    except (UserProfile.DoesNotExist, Question.DoesNotExist) as e:
        return HttpResponse(0)

    try:
        question_vote = QuestionVote.objects.get(question_id=question_id, user_id=user.id)
    except QuestionVote.DoesNotExist:
        question_vote = QuestionVote()
        question_vote.question = question
        question_vote.user = user
        question_vote.value = 0

    if question_vote.value == int(value):
        question_vote.value = 0
    else:
        question_vote.value = int(value)

    if question_vote.value == 0:
        question_vote.delete()
    else:
        question_vote.save()

    return JsonResponse({'current_vote': question_vote.value, 'total_votes': question.vote_sum()})


@login_required
def vote_answer(request):
    answer_id = request.POST.get('answer_id')
    value = request.POST.get('value')
    user_id = request.POST.get('user_id')

    try:
        answer = Answer.objects.get(pk=answer_id)
        user = UserProfile.objects.get(pk=user_id)
    except (UserProfile.DoesNotExist, Answer.DoesNotExist) as e:
        return HttpResponse(0)

    try:
        answer_vote = AnswerVote.objects.get(answer_id=answer_id, user_id=user.id)
    except AnswerVote.DoesNotExist:
        answer_vote = AnswerVote()
        answer_vote.answer = answer
        answer_vote.user = user
        answer_vote.value = 0

    if answer_vote.value == int(value):
        answer_vote.value = 0
    else:
        answer_vote.value = int(value)

    answer_vote.save()

    return JsonResponse({'current_vote': answer_vote.value, 'total_votes': answer.vote_sum()})


@login_required
def mark_answer_right(request):
    answer_id = request.POST.get('answer_id')
    user_id = request.POST.get('user_id')

    try:
        answer = Answer.objects.get(pk=answer_id)
    except (UserProfile.DoesNotExist, Answer.DoesNotExist) as e:
        return HttpResponse(-1)

    if answer.question.user.id != int(user_id):
        return HttpResponse(-1)

    value = 0 if answer.is_correct == 1 else 1
    answer.is_correct = value
    answer.save()

    return HttpResponse(value)

