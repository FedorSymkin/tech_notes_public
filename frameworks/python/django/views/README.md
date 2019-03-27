# django generic views

* В ряде стандартных случаев в качестве обработчиков на указанные пути можно использовать не функции, а стандартные view-классы django
* Примеры таких случаев - создать/поменять/добавить/посмотреть данные какой-то одной таблицы в БД
* Эти классы - новый уровень абстракции, ещё выше чем формы из примера forms
* Использовать так: 
    * наследуемся от нужного класса (например ListView - посмотреть список всех записей, DetailView - посмотреть одну запись и т.д.)
    * В почти декларативном стиле описываем там подробности - куда чего и как смотреть
    * В качестве обработчика в url говорим MyClass.as_view()