from django.db import models


class BorCalculator(models.Model):
    """ Выполняет расчет концентрации БК по полученным данным """

    # param_1 = models.FloatField()
    # param_2 = models.FloatField()

    # x = models.IntegerField()
    # y = models.IntegerField()

    @staticmethod
    def getter():
        """
        Получает из полей html страницы данные для расчета
        """
        pass

    @staticmethod
    def returner():
        """
        Производит расчет целевой концентрации БК
        """
        return 5 + 2
