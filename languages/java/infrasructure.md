# Инфраструктура вокруг java
## Пакеты
* ``package com.myproj.mypack;`` в начале файла (опционально)
*  Импортируем классы либо ``import com.myproj.mypack.MyClass`` либо можно * вместо MyClass, т.е. все
* А ещё можно без импорта использовать класс, если тип обозначать полностью: ``com.myproj.mypack.MyClass``
* Статический импорт - см. раздел с основами
* Структура директорий повторяет структуру названия пакета, а Имя файла ``.java`` - любое
* Если не указать package, пакет будет безымянным, его импортировать нельзя

## Компиляция и выполнение, простейший случай
* Сначала ставится java development kit - набор программ для работы java. Например openJDK под GPL лицензией 
* В него входит как минимум виртуальная машина java (для JDK она назвыается HotStop) и компилятор в байткод javac
* javac компилирует файл ``.java`` в файл ``.class`` (аналогично тому, как C++ компилирует ``.cpp`` в ``.o``). Пример ``javac Calculator.java``
* Выполняем скомпилированный код: ``java Calculator <параметры>``

## Компиляция и выполнение, случай с пакетами
* ``javac -d bin src/ru/javarush/Calculator.java`` - в директории bin создаётся такая же структура
* ``java -classpath ./bin ru.javarush.Calculator <параметры>`` -  classpath - это root откуда искать скомпилированные файлы, аналог PYTHONPATH

## Точка входа в программу
* В файле который передаётся джаве не запуск, самый первый public класс с любым названием должен содержать ``public static void main(String[] args)`` - это и есть точка входа

## jar
* jar-файл это zip-архив, в котором хранятся class-файлы. Его можно рассматривать как единый "бинарник" для запуска java-программы или подключения в виде библиотеки
* TODO как запустить java с точкой входа в jar файле из консоли
* TODO как собрать jar в IDE?
* TODO как подключить jar в виде библиотеки?

## Компиляция и выполнение из IDE
* Ниже будет про использование IDEA 
* При создании дефалтового проекта, проектного файла со списков всех java-исходников нет. IDEA просто смотрит что есть в директориях
* При этом из IDEA вообще не вызывается javac как отдельный процесс, вместо этого используется API внутри java (т.е. IDE сама на java) - https://stackoverflow.com/questions/43855119/how-can-i-see-the-javac-command-intellij-idea-uses-to-compile-my-code
* При старте приложения из IDEA команда на старт примерно такая:
```
/usr/lib/jvm/java-1.8.0-openjdk-amd64/bin/java -javaagent:/home/baggins/idea-IU-202.7660.26/lib/idea_rt.jar=44385:/home/baggins/idea-IU-202.7660.26/bin -Dfile.encoding=UTF-8 -classpath <много путей к стандартным либам>:/home/baggins/IdeaProjects/hw/out/production/hw com.test.Main
```
* ``home/baggins/IdeaProjects/hw/out/production/hw`` - путь к корню hello world проекта
* com.test.Main - точка входа
* javaagent: в программу подключается специальный jar, который может в реалтайме делать всякие манипуляции с байт-кодом. В данном примере IDE вставляет свой jar, скорее всего для отладки. **Важно** - второй процесс java при этом не создаётся, всё внутри одного
* Как быстро делать Makefile-ы для java (аналог проектного файла например cmake - TODO разобраться)

## Just-in-time компиляция
* Это по сути кэширование: наиболее частно используемые участки байткода компилируются в машинный код и кэшируются в памяти. Это происходит на лету в реалтайме. Улучшает производительность.

## Сборка мусора
См. раздел base