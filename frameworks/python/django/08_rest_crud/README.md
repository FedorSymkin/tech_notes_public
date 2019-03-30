# Create, Retrieve, Update, Delete with Django REST framework

* Retrieve, Update, Delete - похожие операции. У них url общий `/post/<id>`, а у Retrieve и Update возвращаемый результат тоже общий.
* Поэтому эти 3 операции делаются через один класс view
* По интерфейсу обращения они различаются только методом HTTP
* Create - формально отдельная операция (url другой `/post/new`), её можно сделать через отдельный view, но можно и в качестве примеси (доп. базового класса) в RetrieveUpdateDeleteView