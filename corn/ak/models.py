from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class Ak(AbstractUser):
    VIEW = [
        ('legal', 'Юрид/лицо'),
        ('IP', 'ИП'),
    ]
    view = models.CharField(max_length=25, choices=VIEW, default='legal', verbose_name='вид')
    name_firma = models.CharField(max_length=150, verbose_name='Наименование'),
    inn = models.CharField(
        verbose_name='ИНН',
        max_length=12,  # Максимум 12 символов для физлиц/ИП
        blank=True,
        null=True,
        unique=True,  # Гарантирует уникальность
        validators=[
            RegexValidator(
                regex=r'^\d{10,12}$',  # 10 или 12 цифр
                message='ИНН должен содержать 10 или 12 цифр'
            )
        ]
    )
    kPP = models.IntegerField(verbose_name='КПП', blank=True,null=True)
    Address = models.CharField(max_length=150, blank=True, verbose_name="Адрес")
    email = models.EmailField(verbose_name='mail')
    director = models.CharField(verbose_name='ФИО', blank=True, max_length=50)



    def __str__(self):
        return f"фирма: {self.name_firma} - директор: {self.director}"

class LoginPassword(models.Model):
    login = models.ForeignKey("Ak", on_delete=models.CASCADE, verbose_name='Логин')
    password = models.CharField(max_length=8 , verbose_name='Пароль')


