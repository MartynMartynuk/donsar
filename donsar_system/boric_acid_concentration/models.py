from django.db import models


class BorCalculator(models.Model):
    """ Выполняет расчет концентрации БК по полученным данным """

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
        :param x:
        :param y:
        :return:
        """
        return 5+2
