from django.conf import settings
from django.db import models

NULLABLE = {'blank': True, 'null': True}


class Client(models.Model):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    comment = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, **NULLABLE)
    is_active = models.BooleanField(default=True, verbose_name='Активный')

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'Клиент'  # Настройка для наименования одного объекта
        verbose_name_plural = 'Клиенты'  # Настройка для наименования набора объектов


class Mailing(models.Model):
    start_time = models.DateTimeField()
    frequency_choices = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    frequency = models.CharField(max_length=10, choices=frequency_choices)
    status_choices = [
        ('created', 'Created'),
        ('started', 'Started'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=10, choices=status_choices)
    recipients = models.ManyToManyField(Client)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, **NULLABLE)

    class Meta:
        verbose_name = 'Рассылки'  # Настройка для наименования одного объекта
        verbose_name_plural = 'Рассылки'  # Настройка для наименования набора объектов


class Message(models.Model):
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, **NULLABLE)

    class Meta:
        verbose_name = 'Сообщение'  # Настройка для наименования одного объекта
        verbose_name_plural = 'Сообщения'  # Настройка для наименования набора объектов


class Log(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20)
    response = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Лог'  # Настройка для наименования одного объекта
        verbose_name_plural = 'Логи'  # Настройка для наименования набора объектов
