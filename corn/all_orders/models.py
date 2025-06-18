from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from counterparties.models import Counterparties
from django.contrib.auth.models import User
from django.conf import settings


class ExpenseOrder(models.Model):
    ORDER_STATUS = (
        ('draft', 'Черновик'),
        ('approved', 'Утвержден'),
        ('executed', 'Исполнен'),
        ('canceled', 'Отменен'),
    )

    number = models.CharField('Номер ордера', max_length=50, unique=True)
    date = models.DateField('Дата ордера', default=timezone.now)
    recipient = models.ForeignKey(Counterparties, on_delete=models.CASCADE, verbose_name='Получатель')
    amount = models.DecimalField('Сумма', max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    basis = models.TextField('Основание')
    comment = models.TextField('Комментарий', blank=True)
    status = models.CharField('Статус', max_length=20, choices=ORDER_STATUS, default='draft')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    created_by = models.ForeignKey(

        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_expense_orders',
        verbose_name='Кем создан'
    )
    approved_by = models.ForeignKey(

        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='approved_expense_orders',
        verbose_name='Кем утвержден',
        null=True,
        blank=True
    )


    def __str__(self):
        return f'Расходный ордер №{self.number} от {self.date}'

    def save(self, *args, **kwargs):
        if not self.number:
            # Генерация номера ордера при создании
            last_order = ExpenseOrder.objects.order_by('-id').first()
            last_number = int(last_order.number.split('/')[-1]) if last_order else 0
            self.number = f'РКО-{self.date.strftime("%Y%m%d")}/{last_number + 1}'
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Расходный кассовый ордер'
        verbose_name_plural = 'Расходные кассовые ордера'
        ordering = ['-date', '-number']
