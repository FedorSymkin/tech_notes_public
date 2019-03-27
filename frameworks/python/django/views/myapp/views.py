"""
Демонстрация концепции views.
В предыдущих примерах в качестве обработчиков запросов стояли просто функции,
которые возвращали HttpResponse или HttpResponseBadRequest.

Внутри этих обработчиков также использовались django-вские формы.

Здесь показывается, что для стандартных ситуаций
(когда мы работаем с данными таблицы по принципу создать/поменять/удалить/посмотреть)
есть классы django, которые выполняют всю эту рутинную работу и позволяют писать почти
в декларативном стиле.

Т.е. мы уже не делаем функцию-обработчик запроса по определённому пути, а наследуется
от встроенного класса, и у него зовём as_view в качестве обработчика (см. urls.py)
"""

from django.http import HttpResponse, HttpResponseBadRequest
from django.urls import reverse
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from . import models
from django.views.decorators.csrf import csrf_exempt


def home(request):
    # Это костыльная менюшка для простой навигации. Она кривая, но для текузего примера это не важно.
    return HttpResponse('''
        First make default data:
        <form method="POST" action="{make_data}">
            <button type="submit">CREATE</button>
        </form>

        <br/><br/><br/>
        After that, test views:<br>

        <a href='{employee_list}'>employee_list</a><br/>
        <a href='{employee_create}'>new employee</a><br/>
    '''.format(
        make_data=reverse('make_data'),
        employee_list=reverse('employee_list'),
        employee_create=reverse('employee_create'),
    ))


@csrf_exempt
def make_data(request):
    # это вспомогательный обработчик на /make_data - создать тестовые данные.
    if request.method == "POST":
        models.make_default_data()
        return HttpResponse('default data created, <a href="{}">return back</a>'.format(reverse('home')))


# =============================================================================
# А вот здесь начинается основной смысл примера

class EmployeeListView(ListView):
    # Вот так декларативно мы объявляем что у нас есть обработчик на /employees (см. urls.py),
    # т.е. посмотреть все employyes.
    # Здесь автоматически запрашивается из БД список объектов (для заданой модели)

    # говорим какой модели (таблице) данных соответствует наш view
    model = models.Employee

    # как рендерить его в html. Кстати это опционально. Если нет, возьмёт некоторое стандартное название.
    # Но сам файл html нужен
    template_name = 'employee_list.html'

    # Это имя объекта через которое мы можем получить доступ данных изнутри шаблона html.
    # Возможно тоже опционально (если отсутвтует - будет стандартное какое-то). Но это не проверял
    context_object_name = 'employees'

    # Ещё одна опциональная штука - как сортировать.
    # Наверняка есть как фиьльтровать и проч. настройки запроса в БД
    ordering = ['first_name']


class EmployeeDetailsView(DetailView):
    # посмотреть один employee. Как эта штука узнаёт, какой именно?
    # см подробнее в urls.py
    model = models.Employee
    template_name = 'employee_details.html'


class EmployeeCreateView(CreateView):
    # сабж
    model = models.Employee

    # employee_form называется потому что ещё на edit этот же html
    template_name = 'employee_form.html'

    # обязательное поле
    fields = ['first_name', 'surname', 'department']

    def get_success_url(self):
        # это куда редиректить пользователя в случае удачного создания
        return reverse('employee_list')

    def form_valid(self, form):
        # демонстрация того, как можно проверять полученные данные перед добавлением в базу
        post = self.request.POST
        if post.get('first_name').lower() == 'bill' and post.get('surname').lower() == 'gates':
            return HttpResponseBadRequest('Bill Gates cannot be an employee. He has made all money he wanted to make')

        return super().form_valid(form)


class EmployeeUpdateView(UpdateView):
    # Здесь прямо полная копипаста из примера выше.
    # Чтобы не усложнять понимание примера оставляю так, но вообще можно конечно упростить
    # например вынести это в отдельный класс, а сюда добавить его как mixin в список базовых классов
    model = models.Employee
    template_name = 'employee_form.html'

    fields = ['first_name', 'surname', 'department']

    def get_success_url(self):
        return reverse('employee_list')

    def form_valid(self, form):
        post = self.request.POST
        if post.get('first_name').lower() == 'bill' and post.get('surname').lower() == 'gates':
            return HttpResponseBadRequest('Bill Gates cannot be an employee. He has made all money he wanted to make')

        return super().form_valid(form)


class EmployeeDeleteView(DeleteView):
    model = models.Employee
    template_name = 'employee_delete.html'

    # Тонкий момент: с одной стороны можно написать success_url = ... как переменную,
    # и если написать success_url='/' - будет работать, но вот reverse на этой стадии не работает.

    def get_success_url(self):
        return reverse('employee_list')
