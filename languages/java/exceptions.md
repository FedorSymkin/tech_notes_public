# Исключения в java
## Meta
* Всё тривиально и ожидаемо
```java
public class App {
    public static void main(String[] args) {
        try {
            throw new Exception();
        } catch (RuntimeException e) {
            System.err.println("catch RuntimeException");
        } catch (Exception e) {
            System.err.println("catch Exception");
        } catch (Throwable e) {  // это - обработка любого исключения. Они в джаве все от Throwable
            System.err.println("catch Throwable");
        } finally {
            //выполняется в любом случае (опционально)
        }
        System.err.println("next statement");
    }
}
```
* Тип эксепшена проверяется в рантайме сверху вниз
* Нельзя ставить catch потомка после предка - не скопмилится
```java
public class App {
    public static void main(String[] args) {
        try {
        } catch (Exception e) {
        } catch (RuntimeException e) {
        }
    }
}
>> COMPILATION ERROR: Exception 'java.lang.RuntimeException' has alredy been caught
```
* Перевыброс внутри блока catch допускается. Есть фича как это сделать, чтобы не терять контекст предыдущего исключения:

```java
catch (SQLException original) {
    var е = new ServletException("database error");
    e.initCause(original);
    throw е;
}
```
* В общем случае исключения работают гораздо медленнее, чем простая проверка ифом


* Есть 2 ветки исключений, наследованных от Throwable - Error и Exception. Error - то про ошибки в кишках JVM (например нет памяти). Exception - пользовательские ошибки

## Объявление исключений в методах
* ``public void DoSomething(String name) throws FileNotFoundException``
* Т.е. это исключения, которые могут лететь наружу (если не перехвачено внутри)
* Для чего это - если объявлено throws, в вызывающем коде обязательно его обработать, иначе не скомпилится. 
* Можно не конкретное исключение, а абстрактного предка, например ``IOException``
* Наследников исключения Error объявлять не обязательно - это и так подразумевается

## try с ресурсами
* Это аналог with в питоне или деструктора в C++:
* Сабж:
```java
try (Resource res = new Resource(...) ) {
   // работаем c res
}
```
* В конце в любом случае будет вызыван метод res.close, т.е. ресурно должен наследовать интерфейс AutoClosable
* Есть ещё Closable - он throws IOException
* Сюда же можно добавлять catch-и

## assert
* ``assert x > 0`` или ``assert x > 0 : "bad x"``
* Это отладочная штука, по умолчанию выключена. Чтобы включить надо запускать java с параметром ``-enaleassertions МуАрр
``

## Ещё разные тонкости
* Выстрел в ногу с finally и return
```java
public int foo() {
    try {
        return 42;
    }
    finally {
        return 0;  // метод вернёт 0! Потому что finally вызывается сначала! Не надо делать return в finally!
    } 
}
```
* Для отладки: у исключений есть printStackTrace, getStackTrace. А также см. класс StackWalker



