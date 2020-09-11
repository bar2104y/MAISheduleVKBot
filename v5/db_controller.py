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
    type = CharField(max_length=10)
    number = SmallIntegerField()
    teacher = ForeignKeyField(Teachers, verbose_name='lessons', null=True)
    room = ForeignKeyField(Rooms, related_name='lessons', null=True)
    group = ForeignKeyField(Groups, related_name='lessons')

    class Meta:
        database = db


class Controller:
    @staticmethod
    def get_teacher_id(fio):
        if fio != '':
            fio = str(fio).split()

            teacher = Teachers.select().where(Teachers.first_name == fio[1],
                                              Teachers.second_name == fio[2],
                                              Teachers.surname == fio[0])

            if teacher.count() == 0:
                res = Teachers.create(first_name=fio[1], second_name=fio[2], surname=fio[0])
                return res.id
            else:
                return teacher[0].id

    @staticmethod
    def get_subject_id(name):
        if name != '':
            name = str(name).lower()
            subject = Subjects.select().where(Subjects.name == name)

            if subject.count() == 0:
                res = Subjects.create(name=name)
                return res.id
            else:
                return subject[0].id

    @staticmethod
    def get_room_id(name):
        if name != '':
            name = str(name).lower()
            subject = Rooms.select().where(Rooms.name == name)

            if subject.count() == 0:
                res = Rooms.create(name=name)
                return res.id
            else:
                return subject[0].id

    @staticmethod
    def get_group_id(name):
        if name != '':
            subject = Groups.select().where(Groups.group == name)

            if subject.count() == 0:
                res = Groups.create(group=name)
                return res.id
            else:
                return subject[0].id

    @staticmethod
    def save_lesson(subject, day, type, number, teacher, room, group):
        lesson = Lessons.select().where(Lessons.day == day,
                                        Lessons.number == number,
                                        Lessons.group == group)

        if lesson.count() == 0:
            res = Lessons.create(subject=subject,
                                 day=day,
                                 type=type,
                                 number=number,
                                 teacher=teacher,
                                 room=room,
                                 group=group)
            return res.id
        else:
            lesson[0].update({Lessons.subject: subject,
                              Lessons.type: type,
                              Lessons.teacher: teacher,
                              Lessons.room: room}).where(Lessons.day == day,
                                                         Lessons.number == number,
                                                         Lessons.group == group)
            return lesson[0].id


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

