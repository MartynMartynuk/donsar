from django.db import models


class Album(models.Model):
    album_file = models.FileField(upload_to='', verbose_name='Альбом НФХ')
    # album_tables = models.JSONField(null=True)


class BorCalculator(models.Model):
    """ Выполняет расчет концентрации БК по полученным данным """

    power_before_stop = models.IntegerField(null=True, verbose_name='Мощность ЯР до остановки (% от Nном)')
    effective_days_worked = models.IntegerField(null=True, verbose_name='Число отработанных эффективных суток')
    rod_height_before_stop = models.IntegerField(null=True, verbose_name='Подъем стержней до останова (%)')
    crit_conc_before_stop = models.FloatField(null=True, verbose_name='Критическая концентарация БК до останова')
    start_time = models.FloatField(null=True, verbose_name='Время, через которое '
                                                           'будет осуществляться запуск (часов)')
