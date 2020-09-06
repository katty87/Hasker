from datetime import datetime
import os

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from django.views.generic.edit import FormMixin
from django.views.generic import ListView

from django.db.models import Sum, Count, When, Case, Exists, OuterRef
from django.db.models.functions import Coalesce

from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q
from django.views import generic
from django.http import JsonResponse
from django.core.mail import send_mail
import json
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from Hasker.settings import EMAIL_HOST_USER

from homepage.forms import SignUpForm, AddQuestionForm, QuestionDetailForm, UserSettings
from homepage.models import Question, QuestionVote, Answer, AnswerVote, Tag, UserProfile, GroupConcat


class IndexView(generic.ListView):
    template_name = 'homepage/index.html'
    context_object_name = 'question_list'
    paginate_by = 20

    def get_queryset(self):
        order_by = ['-vote_cnt', '-create_date'] if self.request.GET.get('ordering', '0') == '1' \
            else ['-create_date', '-vote_cnt']

        qs = Question.objects.all() \
            .annotate(answer_cnt=Count('answer', distinct=True),
                      vote_cnt=Count('questionvote__id', fiter=Q(questionvote__id=0), distinct=True),
                      tag_list=GroupConcat('tags__name', distinct=True)) \
            .order_by(*order_by) \
            .values('id', 'header', 'create_date', 'user__username', 'user__userprofile__avatar',
                    'answer_cnt', 'vote_cnt', 'tag_list')

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
    template_name = 'homepage/search_results.html'
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
            .order_by('-vote_cnt', '-create_date') \
            .values('id', 'header', 'create_date', 'user__username', 'user__userprofile__avatar',
                    'answer_cnt', 'vote_cnt', 'tag_list')

    def get_context_data(self, **kwargs):
        context = super(SearchResultsView, self).get_context_data(**kwargs)
        q = self.request.GET.get('q', '')
        context.update({'q': q})
        context.update({'tag_search': 1 if q.split(':')[0].strip().lower() == 'tag' else 0})

        return context


@login_required
def ask_view(request):
    question_instance = Question()

    if request.method == 'POST':
        form = AddQuestionForm(request.POST)
        if form.is_valid():
            question_instance.header = form.cleaned_data['title']
            question_instance.content = form.cleaned_data['content']
            question_instance.create_date = datetime.utcnow()
            question_instance.user = request.user
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
    else:
        form = AddQuestionForm()

    context = {
        'form': form,
        'question_instance': question_instance,
        'tags': json.dumps(list(Tag.objects.all().values_list('name', flat=True)))
    }

    return render(request, 'homepage/add_question.html', context)


class QuestionDetailView(ListView, FormMixin):
    form_class = QuestionDetailForm
    model = Answer
    template_name = 'homepage/detail_question.html'
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
            .order_by('-vote_sum', 'create_date').values('id', 'content', 'is_correct', 'user__username', 'user__userprofile__avatar',
                                                         'vote_sum', 'current_user_vote')

    def get_context_data(self, **kwargs):
        if not self.request.user:
            return super(QuestionDetailView, self).get_context_data(**kwargs)

        user_id = self.request.user.id
        context = super(QuestionDetailView, self).get_context_data(**kwargs)

        pk = self.kwargs.get('pk', '')

        if pk:
            question = get_object_or_404(Question, pk=pk)
            context.update({'question_vote': question.current_user_vote(user_id)})
            context.update({'question': question})

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
@require_http_methods(['POST'])
def answer_question(request, pk):
    question = get_object_or_404(Question, pk=pk)

    form = QuestionDetailForm(request.POST)

    if form.is_valid():
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


@login_required
def vote_question(request):
    question_id = request.POST.get('question_id')
    value = request.POST.get('value')
    user_id = request.POST.get('user_id')

    try:
        question = Question.objects.get(pk=question_id)
        user = User.objects.get(pk=user_id)
    except (User.DoesNotExist, Question.DoesNotExist) as e:
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
        user = User.objects.get(pk=user_id)
    except (User.DoesNotExist, Answer.DoesNotExist) as e:
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
    except (User.DoesNotExist, Answer.DoesNotExist) as e:
        return HttpResponse(-1)

    if answer.question.user.id != int(user_id):
        return HttpResponse(-1)

    value = 0 if answer.is_correct == 1 else 1
    answer.is_correct = value
    answer.save()

    return HttpResponse(value)


class SignUpView(generic.CreateView):
    form_class = SignUpForm
    template_name = "registration/signup.html"

    def get_success_url(self):
        redirect_to = self.request.POST['next']
        return redirect_to

    def get_context_data(self, **kwargs):
        context = super(SignUpView, self).get_context_data(**kwargs)
        context.update({'next': self.request.GET.get('next', '')})
        return context

    def post(self, request, *args, **kwargs):
        response = super(SignUpView, self).post(request, *args, **kwargs)
        form = self.get_form()

        if form.is_valid():
            new_user = form.save()
            user_profile = new_user.userprofile
            user_profile.avatar = form.cleaned_data['avatar']
            user_profile.save()

            login(request, new_user, 'django.contrib.auth.backends.ModelBackend')
        return response


class SettingsView(LoginRequiredMixin, UpdateView):
    form_class = UserSettings
    model = UserProfile
    template_name = 'registration/user_settings.html'
    # fields = ['avatar']

    def get_success_url(self):
        redirect_to = self.request.POST['next']
        return redirect_to

    def get_context_data(self, **kwargs):
        context = super(SettingsView, self).get_context_data(**kwargs)
        context.update({'next': self.request.GET.get('next', '')})
        if self.request.user.userprofile.avatar:
            context.update({'file_name': os.path.basename(self.request.user.userprofile.avatar.name)})
        else:
            context.update({'file_name': ''})

        return context

    def post(self, request, *args, **kwargs):
        response = super(SettingsView, self).post(request, *args, **kwargs)
        form = self.get_form()
        request.user.email = form.data['email']
        request.user.save()
        return response
