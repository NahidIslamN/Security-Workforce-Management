from django.contrib import admin
from .models import *
admin.site.register(CustomUser)
admin.site.register(LicencesType)
admin.site.register(LicencesModel)
admin.site.register(CertificateModel)
admin.site.register(CertificateType)
admin.site.register(BankCardinfo)

admin.site.register(GaurdRating)
admin.site.register(ComapnyRating)


admin.site.register(JobApplications)

admin.site.register(CompanyModel)

admin.site.register(JobModel)

admin.site.register(EngagementModel)

admin.site.register(Images)


admin.site.register(SubscribtionPlan)
admin.site.register(Benefits)
admin.site.register(Invoices)
admin.site.register(OperativeNote)





