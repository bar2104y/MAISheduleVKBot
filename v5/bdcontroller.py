from peewee import *

db = SqliteDatabase('Base.db')


class Rooms(Model):
    name = CharField(max_length=20, unique=True)
    description = TextField(null=True)

    class Meta:
        database = db


class Teachers(Model):
    photo = TextField(null=True)
    first_name = CharField(max_length=30)
    second_name = CharField(max_length=30)
    surname = CharField(max_length=30)
    description = TextField(null=True)
    # reviews = ManyToManyField()

    class Meta:
        database = db


class Subjects(Model):
    name = CharField(max_length=120)
    description = TextField(null=True)

    class Meta:
        database = db


class Groups(Model):
    group = CharField(max_length=14, unique=True)

    class Meta:
        database = db


class Users(Model):
    vk_id = IntegerField(unique=True)
    group = ForeignKeyField(Groups, related_name='users')
    notification = BooleanField(default=True)

    class Meta:
        database = db


class Lessons(Model):
    subject = ForeignKeyField(Subjects, verbose_name="lessons")
    day = DateField()
    number = SmallIntegerField()
    teacher = ForeignKeyField(Teachers, verbose_name='lessons', null=True)
    room = ForeignKeyField(Rooms, related_name='lessons', null=True)
    group = ForeignKeyField(Groups, related_name='lessons')

    class Meta:
        database = db


def init():
    Rooms.create_table()
    Teachers.create_table()
    Subjects.create_table()
    Groups.create_table()
    Users.create_table()
    Lessons.create_table()
    print("ok")
    return


if __name__ == "__main__":
    init()

