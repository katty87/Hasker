from datetime import datetime

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.template import loader
from django.db.models import Q
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

from homepage.forms import SignUpForm, AddQuestionForm
from homepage.models import Question, QuestionVote, Answer, AnswerVote, Tag


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
def answer_question(request, pk):
    question = get_object_or_404(Question, pk=pk)

    answer = Answer()
    answer.content = request.POST['answer_text']
    answer.question = question
    answer.is_correct = False
    answer.user = request.user
    answer.save()
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


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def settings_view(request):
    return HttpResponse("Settings")

