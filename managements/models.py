from django.db import models


class PaymentController(models.Model):
    is_percentage_guard = models.BooleanField(default=False)
    is_percentage_company = models.BooleanField(default=False)

    percentage_company = models.IntegerField()
    percentage_guard = models.IntegerField()

    min_referral_user_of_company = models.IntegerField()
    min_referral_user_of_guard = models.IntegerField()

    total_free_days_company = models.IntegerField()
    total_free_days_guard = models.IntegerField()



    def delete(self, using = ..., keep_parents = ...):
        
        raise Exception("Deletion is not allowed for this object.")
    
    def __str__(self):
        return f'Controler-{self.id}'

