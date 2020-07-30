from datetime import datetime

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.template import loader
from django.db.models import Q
from django.views import generic

from homepage.forms import SignUpForm, AddQuestionForm
from homepage.models import Question, UserProfile, Answer


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


# @login_required
def ask_view(request):
    question_instance = Question()

    if request.method == 'POST':
        form = AddQuestionForm(request.POST)
        question_instance.header = form.data['title']
        question_instance.content = form.data['content']
        question_instance.create_date = datetime.now()
        question_instance.user = User.objects.get(username='admin')
        question_instance.save()

        return redirect('question_detail', question_id=question_instance.id)
    else:
        form = AddQuestionForm()

    context = {
        'form': form,
        'question_instance': question_instance,
    }

    return render(request, 'homepage/add_question.html', context)


def question_view(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'homepage/detail_question.html', {'question': question})


def answer_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    answer = Answer()
    answer.content = request.POST['answer_text']
    answer.question = question
    answer.is_correct = False
    answer.save()
    return redirect('question_detail', question_id=question.id)


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

