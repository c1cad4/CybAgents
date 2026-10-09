# CybAgents

сами агенты: их роли, инструменты, память в рамках задач, настройки, жизненный цикл и протоколы взаимодействия.

## Реализовано

Неизменяемый контракт агента и явные memory.remember/memory.recall capabilities. Произвольное исполнение кода отсутствует; взаимодействие через вызовы ограниченных методов памяти.

## Проверка

```bash
python3 -m unittest discover -s tests -v
```


## Интеграция

[Сквозной API и UI](https://github.com/c1cad4/CybCore) · [Карта экосистемы](https://github.com/c1cad4/cybOS)

## Advisor

Advisor использует агента с memory.recall для чтения знаний, ограничивает контекст
и вызывает переданный адаптер модели. Во время сетевого вызова SQLite-соединение
закрыто. В CybCore это подключено к /ask; адаптер и ошибки протокола находятся
в CybCore/local_model.py. Capabilities копируются в immutable tuple.
