from django.db import models
from django.db.models import PROTECT


class Album(models.Model):
    album_file = models.FileField(upload_to='', verbose_name='Альбом НФХ')
    title = models.CharField(max_length=255, verbose_name='Название таблицы', null=True)
    content = models.JSONField(verbose_name='Значения в таблице', null=True)
    block = models.ForeignKey('Block', on_delete=PROTECT, null=True, verbose_name='Блок и загрузка')


class Block(models.Model):
    block_number = models.IntegerField(db_index=True)
    batch_number = models.IntegerField(db_index=True)

    def __str__(self):
        return f'Блок {self.block_number} загрузка {self.batch_number}'


class BorCalculator(models.Model):
    """ Выполняет расчет концентрации БК по полученным данным """

    power_before_stop = models.IntegerField(verbose_name='Мощность ЯР до остановки (% от Nном)')
    effective_days_worked = models.IntegerField(verbose_name='Число отработанных эффективных суток')
    rod_height_before_stop = models.IntegerField(verbose_name='Подъем стержней до останова (%)')
    crit_conc_before_stop = models.FloatField(verbose_name='Критическая концентрация БК до останова')
    start_time = models.FloatField(verbose_name='Время, через которое '
                                                'будет осуществляться запуск (часов)')
    block = models.ForeignKey('Block', on_delete=PROTECT, null=True, verbose_name='Блок и загрузка')
