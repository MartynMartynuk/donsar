from django.db import models
from django.db.models import PROTECT


class Album(models.Model):
    album_file = models.FileField(upload_to='', verbose_name='Альбом НФХ')
    title = models.CharField(max_length=255, verbose_name='Название таблицы', null=True)
    content = models.JSONField(verbose_name='Значения в таблице', null=True)
    block = models.ForeignKey('Block', on_delete=PROTECT, null=True, verbose_name='Блок и загрузка')


class Block(models.Model):
    block_number = models.IntegerField(db_index=True, verbose_name='Номер блока')
    batch_number = models.IntegerField(db_index=True, verbose_name='Номер загрузки')

    def __str__(self):
        return f'Блок {self.block_number} загрузка {self.batch_number}'


class CalculationResult(models.Model):
    critical_curve = models.JSONField()
    setting_curve = models.JSONField()
    water_exchange_curve = models.JSONField()
    start_time = models.IntegerField()
    stop_time = models.DateTimeField()  #ToDo вроде нигде не используется, надо бы убрать
    stop_conc = models.FloatField()
    exp_exchange_curve = models.JSONField(null=True)
    block = models.CharField(max_length=15, null=True)
