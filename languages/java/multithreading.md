# Многопоточность в java
## Простой пример
* Унаследоваться от интерфейса Runnable (можно в виде лямбда-выражения) и передать объект в конструктор Thread
```java
Runnable r = () -> {
    try {
        // isInterrupted - фича из коробки, станет true когда поток прервут снаружи
        while ( ! Thread.currentThread().isInterrupted() ) {
            //код
        }    
    }
    catch (InterruptedException е) {
        // а сюда попадём, если поток прерван снаружи в момент блокирующего вызова
    }
}
var t = new Thread(r);
t.start();
```
* Либо унаследоваться от класса Thread (тоже метод run)
* Передать параметр в поток - либо полем наследнике Runnable, либо через анонимный класс, там можно захватывать переменные (замыкание т.е.)
```java
   final X parameter = ...; // the final is important
   Thread t = new Thread(new Runnable() {
       p = parameter;
       public void run() { 
         ...
       };
   };
   t.start();
```
* ``yield()`` - отдать время CPU другому потоку
* ``t.setDaemon(true)`` - detach потока (станет фоновым, не джойнится в конце программы)

## Состояние потоков
* NEW
* RUNNABLE (после вызова start)
* BLOCKED - ждём мьютекса
* WAITING - ждём события
* TIMED_WAITING - ждём события с таймаутом
* TERMINATED - run закончился

## Остановка потока снаружи
* ``stop/suspend/resume`` - не рекомендуется, это грубая остановка прямо сейчас
* ``interrupt()`` - либо взводит флаг ``.isInterrupted()`` (его можно проверять внутри run), либо, если поток в блокирующем вызове приводит к выбросу InterruptedException внутри потока.
* Тонкость: ``interrupted()`` vs ``isInterrupted()``: первое сбрасывает флаг прерывания, второе нет. А ещё interrupted - статический, работает только для текущего потока.

## Примитивы синхронизации
* ``java.util.concurrent.locks.Lock`` - мьютекс
* ``java.util.concurrent.locks.ReentrantLock`` - мьютекс, который можно брать повторно в том же потоке
* Через try с ресурсами локи брать нельзя. К сожалению придётся делать освобождение каждый раз через finally? TODO: погуглить, может быть не обязательно.
* ``java.util.concurrent.locks.Condition`` - условная переменная, она же Event. Как обычно: signal, signalAll, await (можно с таймаутом). 
* **Важно** - TODO: при использовании Condition могут быть дедлоки, если в неправильном порядке вызывать await, signal, signalAll. Перед использованием разобраться в теме (везде по-разному, нужно разобраться как с этим именно в джаве)
* Атомарные переменные - см. классы Atomicinteger, AtomicLong и т.д. Исполбуются атомарные инструкции процессора.
* ThreadLocal - создать переменную, у которой для каждого потока будет своя копия
```java
public static final ThreadLocal<SimpleDateFormat> dateFormat = ThreadLocal.withInitial( () -> new SimpleDateFormat("yyyy-ММ-dd") );
...
String dateStamp = dateFormat.get().format(new Date());
```

* TODO: ReadWrite lock есть? (Это когда exclusive на запись и shared на чтение)
* TODO семафор есть?

## Слово synchronized
* У каждого объекта в java есть встроенный Lock и встроенный Condition
* Если объявить метод объекта со словом **synchronized**, то любой поток в него входящий захватывает этот встроенный Lock (т.е. получается что два метода synchronized имеют общий лок - уточнить)
* У объектов также есть методы wait и notifyAll - это управление встроенным Condition
* Со статическими методами тоже можно - тогда будет использоваться встроенные блокировки класса, не объекта
* synchronized блоки кода
```java
private Object lock = new Object();  //любой объект
synchronized (obj) { // захвытвается встроенный лок объекта
    //код
}
```

## Future
* Простой пример
```java
Callable<Integer> task = <создаётся объект интерфейса Callable>;
var futuretask = new FutureTask<Integer>(task);
var t = new Thread(futuretask); //так можно, потому что FutureTask реализует интерфейс Runnable
t.start();

...

Integer result = task.get();  // здесь блокируемся
```
* А ещё фьючи умеют callback-и, которые вызываются в момент завершения операции, и их можно сцеплять в цепочки, типа такого
```java
//TODO подробнее разобраться
CompletableFuture.completedFuture(url)
    .thenComposeAsync(this::readPage, executor)
    .thenApply(this::getimageURLs)
    .thenCompose(this::getimages)
    .thenAccept(this::saveimages);
```


## Пул потоков
TODO - в java есть большой выбор классов, реализующих воркеры потоков в разных видах. Разробраться и написать. В частности есть такая штука, как вилочное соединение - распараллеливание задач на рекурсивно одинаковые подзадачи

## Исключения в потоках
* Если из run поткоа полетит наружу исключение - оно обработается дефалтовым обработчиком. По умолчанию он пишет в stderr исключение
* Можно переопределить свой дефалтовый обработчик

## Под капотом
* По умолчанию потоки в java - это реальные потоки ОС, особой магии на стороне JVM нет
* Когда-то были green threads, типа JVM сама менеджерила потоки, но сейчас этого нет.

## Процессы
* см. класс ProcessBuilder
* Можно делать пайпы как в bash: ``ProcessBuilder.startPipeline``