"""
URL configuration for smartplantcare project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

print("SMART PLANT CARE URLS LOADED")
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from website import views
from django.urls import include, path
from website.serviceworker import service_worker

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home, name='home'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("profile/", views.profile_page, name="profile"),
    path('search/', views.search_page, name='search'),
    path("plant-suggestions/", views.plant_suggestions, name="plant_suggestions"),
    path('aiscan/', views.ai_scan_page, name='aiscan'),
    path('about/', views.about_page, name='about'),
    path('contact/', views.contact_page, name='contact'),
    path("aloe_vera/", views.aloe_vera, name="aloe_vera"),
    path("tulasi/", views.tulasi, name="tulasi"),
    path("turmeric/", views.turmeric, name="turmeric"),
    path("hibiscus/", views.hibiscus, name="hibiscus"),
    path("mango_plant/", views.mango_plant, name="mango_plant"),
    path("rose/", views.rose, name="rose"),
    path("logout/", views.logout_page, name="logout"),
    path("watering/", views.watering_page, name="watering"),
    path("watering/delete/<int:id>/", views.delete_watering, name="delete_watering"),
    path("schedule/", views.schedule_page, name="schedule"),
    path("watering/edit/<int:id>/", views.edit_watering, name="edit_watering"),
    path("watering/watered/<int:id>/", views.mark_watered, name="mark_watered"),
    path("schedule/delete/<int:id>/", views.delete_schedule, name="delete_schedule"),
    path('mark-schedule-done/<int:id>/', views.mark_schedule_done, name='mark_schedule_done'),
    path("addplant/", views.addplant_page, name="addplant"),
    path("add-myplant/<int:plant_id>/", views.add_myplant, name="add_myplant"),
    path("delete-myplant/<int:plant_id>/", views.delete_myplant, name="delete_myplant"),
    path("favorite-plants/", views.favorite_plants, name="favorite_plants"),
    path("add-favorite-plant/<int:plant_id>/", views.add_favorite_plant, name="add_favorite_plant"),
    path("delete-favorite-plant/<int:plant_id>/", views.delete_favorite_plant, name="delete_favorite_plant"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path("delete-account/", views.delete_account, name="delete_account"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("reset-password/", views.reset_password, name="reset_password"),
    path("lemon/", views.lemon, name="lemon"),
    path("snake_plant/", views.snake_plant, name="snake_plant"),
    path("sunflower/", views.sunflower, name="sunflower"),
    path("money_plant/", views.money_plant, name="money_plant"),
    path("lotus/", views.lotus, name="lotus"),
    path("watermelon/", views.watermelon, name="watermelon"),
    path("rice/", views.rice, name="rice"),
    path("wheat/", views.wheat, name="wheat"),
    path("coconut/", views.coconut, name="coconut"),
    path("brinjal/", views.brinjal, name="brinjal"),
    path("neem/", views.neem, name="neem"),
    path("mint/", views.mint, name="mint"),
    path("jasmine/", views.jasmine, name="jasmine"),
    path("lucky_bamboo/", views.lucky_bamboo, name="lucky_bamboo"),
    path("serviceworker.js", service_worker, name="service_worker"),
    path('save-subscription/', views.save_subscription, name='save_subscription'),
    path("mark-missed-reminder-seen/", views.mark_missed_reminder_seen, name="mark_missed_reminder_seen"),
    

    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
