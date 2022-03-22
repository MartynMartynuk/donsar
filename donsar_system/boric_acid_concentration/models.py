from django.db import models


class BorCalculator(models.Model):
    """ Выполняет расчет концентрации БК по полученным данным """

    param_1 = models.FloatField()
    param_2 = models.FloatField()

    # x = models.IntegerField()
    # y = models.IntegerField()

    @staticmethod
    def getter():
        """
        Получает из полей html страницы данные для расчета
        """
        pass

    def returner(self, x, y):
        """
        Производит расчет целевой концентрации БК
        :param x:
        :param y:
        :return:
        """
        return x + y
