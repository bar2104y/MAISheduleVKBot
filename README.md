# MAISheduleVKBot

Бот, отправляющий расписание Вашей группы в вк

## Что могёт
 * Запоминает номер группы и перед каждой парой говорит что и где
 * По слову расписание отправляет расписание на два дня вперед (ближайшие два учебных дня, по возможности - сегодня + завтра)
 * Отвечает на запрос о помощи

## Используемые дополнительные пакеты
 * pip install lxml
 * pip install bs4
 * pip install vk_api
 * pip install peewee
 
## Содержимое config.py
```python3
token='***********e5************55e02c****b845'
group_vk='186093930'
```


## Структура БД
### Разрабатывается вторая версия бота, актуальная информация тут https://miro.com/app/board/o9J_kljEdEQ=/


Знаю что криво, но и бот на коленке написан
```sql
CREATE TABLE `users` (
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	`user_id`	TEXT,
	`group_number`	TEXT
);
```
```sql
CREATE TABLE `data` (
	`group_id`	TEXT,
	`day_i`	TEXT,
	`time`	TEXT,
	`type`	TEXT,
	`name`	TEXT,
	`room`	TEXT
);
```

## Roadmap
 * Привязать все сообщения бота к четким командам
 * Реорганизовать структуру хранения данных
 * Изменить настройки профиля
 * Сделать удобный интерфейс для быстрого создания ботов для разных платформ
 

