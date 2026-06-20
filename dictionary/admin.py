from django.contrib import admin

from .models import CommonWord, Learner, LearningStat, UserWord

admin.site.register(Learner)
admin.site.register(CommonWord)
admin.site.register(UserWord)
admin.site.register(LearningStat)
