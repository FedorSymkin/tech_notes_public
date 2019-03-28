from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import render, redirect
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
)
from . import models
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from . import forms


"""
Демонстрация работы с пользователями
"""


def home(request):
    # Это костыльная менюшка для простой навигации. Она кривая, но для текущего примера это не важно.

    # request.user - это заранее определённая переменная, где всё про пользователя,
    # сеесии, куки, пароли и проч - уже спрятано под капотом
    if request.user.is_authenticated:
        login_action = 'logout'
    else:
        login_action = 'login'

    return HttpResponse('''
        <a href='{who_am_i}'>who_am_i</a><br/>
        <a href='{blog}'>blog</a><br/>
        <a href='{register}'>register</a><br/>
        <a href='{login_action}'>{login_action_name}</a><br/>
    '''.format(
        who_am_i=reverse('who_am_i'),
        blog=reverse('blog'),
        register=reverse('register'),
        login_action=reverse(login_action),
        login_action_name=login_action,
    ))


# Демонстрация декоратора login_required. Если никто не залогинен - средиректит сначала на логин
@login_required
def who_am_i(request):
    return HttpResponse('You are: {}'.format(request.user.username))


def register(request):
    # TODO в скринкасте, по которому я этот делал стоит вот такой вот ручной обработчик, а не какой-то стандартный
    # view из django. Погуглил - не нашёл другого сходу. Но интуитивно кажется, что всё таки какой-то
    # стандартный view для такой тривиальной вещи как регистрация пользователя должен быть
    if request.method == 'POST':

        # А вот стандартная форма для регистрации в django почти есть -
        # UserRegisterForm унаследован он UserCreationForm
        form = forms.UserRegisterForm(request.POST)

        # а вообще всё также как с формами
        if form.is_valid():
            form.save()
            return redirect('login')

    else:
        form = forms.UserRegisterForm()

    # Тонкий момент - в это место можно попасть 2 способами:
    #   * Просто когда создаём нового пользоватея. Тогда будет пустая форма
    #   * Если что-то ввели неправильно - тогда тут будет форма уже с некоторыми данными и дополнительным текстом,
    #       что поправьте вот это (в данном случае форма создана строкой form = forms.UserRegisterForm(request.POST).
    #       Так вот здесь из коробки тщательно проверяются пароли - например длина. А если ввести пароль 12345678
    #       оно скажет "This password is too common". Круто!
    return render(request, 'register.html', {'form': form})


class AllPostsView(LoginRequiredMixin, ListView):
    # Здесь в отличие от примеров про views добавляется базовый класс LoginRequiredMixin -
    # работает аналогично @login_required только для классов, а не для функций
    model = models.Post
    template_name = 'posts_list.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']


class NewPostView(LoginRequiredMixin, CreateView):
    model = models.Post
    template_name = 'edit_post.html'
    fields = ['title', 'content']

    def get_success_url(self):
        return reverse('blog')

    def form_valid(self, form):
        # Здесь, в отличие от предыдущих примеров, мы не проверяем данные,
        # а наоборот немного добавляем их. У модели Post есть поле author.
        # На фронте оно не заполняется - потому что юзер загогинен, и ему не нужно каждый раз писать автора.
        # Но перед сохранением данных в базу это поле надо заполнить используя текущую сессию
        form.instance.author = self.request.user
        return super().form_valid(form)


class UpdatePostView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    # Здесь подмешивается ещё один базовый класс - UserPassesTestMixin.
    # Нужно не только проверить что пользователь залогинен (LoginRequiredMixin), а также то, что
    # сообщение редактирует его автор и никто другой. Для этог опереопределяем test_func,
    # которая пришла из UserPassesTestMixin.
    # При попытке отредактировать чужой пост например http://127.0.0.1:8000/blog/update_post/3/
    # получим 403 Forbidden

    model = models.Post
    template_name = 'edit_post.html'
    fields = ['title', 'content']

    def get_success_url(self):
        return reverse('blog')

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True

        return False
