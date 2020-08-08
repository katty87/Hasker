from datetime import datetime
import os

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from django.contrib.auth.forms import UserCreationForm

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
from django.core.files.storage import default_storage

from homepage.forms import SignUpForm, AddQuestionForm
from homepage.models import Question, QuestionVote, Answer, AnswerVote, Tag, UserProfile


class IndexView(generic.ListView):
    template_name = 'homepage/index.html'
    context_object_name = 'question_list'

    def get_queryset(self):
        return Question.objects.all()


class SearchResultsView(generic.ListView):
    model = Question
    template_name = 'homepage/search_results.html'
    context_object_name = 'question_list'

    def get_queryset(self):
        search_string = self.request.GET.get('q')
        return Question.objects.filter(Q(header__icontains=search_string) | Q(content__icontains=search_string))


@login_required
def ask_view(request):
    question_instance = Question()

    if request.method == 'POST':
        form = AddQuestionForm(request.POST)
        if form.is_valid():
            question_instance.header = form.cleaned_data['title']
            question_instance.content = form.cleaned_data['content']
            question_instance.create_date = datetime.now()
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


class QuestionDetailView(generic.DetailView):
    model = Question
    template_name = 'homepage/detail_question.html'

    def get_context_data(self, **kwargs):
        if not self.request.user:
            return super(QuestionDetailView, self).get_context_data(**kwargs)

        user_id = self.request.user.id
        context = super(QuestionDetailView, self).get_context_data(**kwargs)
        question = self.get_object()
        context.update({'question_vote': question.current_user_vote(user_id)})

        return context


@login_required
@require_http_methods(['POST'])
def answer_question(request, pk):
    question = get_object_or_404(Question, pk=pk)

    answer = Answer()
    answer.content = request.POST['answer_text']
    answer.question = question
    answer.create_date = datetime.now()
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

    question_vote.save()

    return JsonResponse({'current_vote': question_vote.value, 'total_votes': question.vote_count()})


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

    return JsonResponse({'current_vote': answer_vote.value, 'total_votes': answer.vote_count()})


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
    template_name = "signup.html"

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
    model = UserProfile
    template_name = 'registration/user_settings.html'
    fields = ['avatar']

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
