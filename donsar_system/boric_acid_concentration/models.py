from django.db import models


class Album(models.Model):
    album_file = models.FileField(upload_to='albums/', verbose_name='Альбом')


class BorCalculator(models.Model):
    """ Выполняет расчет концентрации БК по полученным данным """

    param_1 = models.FloatField(null=True)
    param_2 = models.FloatField(null=True)

    @staticmethod
    def returner(x, y):
        """
        Производит расчет целевой концентрации БК
        """
        return x + y
