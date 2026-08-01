from django.contrib import admin
from .models import User, Plant, Contact, MyPlant

admin.site.register(User)
admin.site.register(Plant)
admin.site.register(Contact)
admin.site.register(MyPlant)
# Register your models here.
