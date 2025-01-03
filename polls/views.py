from django.db.models import F
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.urls import reverse
from django.views import generic
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout

from .models import Choice, Question
from .forms import PollForm 

class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"
    
    def get_queryset(self):
        # Возвращает последние пять опубликованных вопроса
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5]

class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))

@login_required
def create_poll(request):
    if request.method == 'POST':
        form = PollForm(request.POST)
        if form.is_valid():
            # Сохраняем вопрос
            question = form.save(commit=False)
            question.pub_date = timezone.now()  # Устанавливаем дату публикации вручную
            question.save()
            
            # Получаем варианты ответов
            choices = request.POST.get('choices').splitlines()
            for choice_text in choices:
                if choice_text.strip():  # Проверка на пустые строки
                    Choice.objects.create(question=question, choice_text=choice_text.strip())
            return redirect('polls:index')  # После создания опроса перенаправляем на главную страницу
    else:
        form = PollForm()
    return render(request, 'polls/create_poll.html', {'form': form})

# Представление для регистрации
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('polls:index')  # Перенаправление на главную страницу после регистрации
    else:
        form = UserCreationForm()
    return render(request, 'polls/register.html', {'form': form})

# Представление для входа
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('polls:index')  # Перенаправление на главную страницу после входа
    else:
        form = AuthenticationForm()
    return render(request, 'polls/login.html', {'form': form})

# Представление для выхода
def logout_view(request):
    logout(request)
    return redirect('polls:index')  # Перенаправление на главную страницу после выхода