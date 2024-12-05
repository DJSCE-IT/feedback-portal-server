from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin


admin.site.register(Batch)
admin.site.register(Subject)
admin.site.register(Otp)
admin.site.register(SubjectTheory)
admin.site.register(SubjectPractical)
admin.site.register(FeedbackUserConnector)
admin.site.register(FeedbackForm)
admin.site.register(FeedbackInstance)
admin.site.register(MetaInfo)


# Register your models here.
class MyUserModel(admin.StackedInline):
    model = MyUser
    can_delete = False
    verbose_name_plural="Myuser"

class CustomizedUserAdmin(UserAdmin):
    inlines = (MyUserModel,)

admin.site.unregister(User)
admin.site.register(User,CustomizedUserAdmin)    

#class OutstandingTokenAdmin(OutstandingTokenAdmin):
#    def has_delete_permission(self, *args, **kwargs):
#        return True
#admin.site.unregister(OutstandingToken)
#admin.site.register(OutstandingToken, OutstandingTokenAdmin)
