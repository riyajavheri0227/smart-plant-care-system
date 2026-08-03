from django.contrib import admin
from .models import (
    User,
    Plant,
    Contact,
    MyPlant,
    AiScan,
    WateringReminder,
    ScheduleReminder,
    FavoritePlant,
    PushSubscription,
)

admin.site.site_header = "🌱 Smart Plant Care Admin"
admin.site.site_title = "Smart Plant Care"
admin.site.index_title = "Welcome to Smart Plant Care Admin"

admin.site.register(User)
admin.site.register(Plant)
admin.site.register(Contact)
admin.site.register(MyPlant)
admin.site.register(AiScan)
admin.site.register(WateringReminder)
admin.site.register(ScheduleReminder)
admin.site.register(FavoritePlant)
admin.site.register(PushSubscription)