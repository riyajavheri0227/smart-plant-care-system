from django.shortcuts import render, redirect
from .models import User, Plant, AiScan, WateringReminder, ScheduleReminder, Contact, MyPlant, FavoritePlant, PushSubscription
import requests
from django.conf import settings
import base64
from datetime import timedelta
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from webpush import send_user_notification
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.db import IntegrityError


def home(request):
    return render(request,
'home_page.html')

def login_page(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email, password=password)

            request.session["username"] = user.name

            return redirect("dashboard")

        except User.DoesNotExist:
            return render(request, "login.html", {
                "error": "Invalid Email or Password"
            })

    return render(request, "login.html")

#from .models import User

def register_page(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password == confirm_password:

            try:
                user = User.objects.create(
                    name=name,
                    email=email,
                    phone=phone,
                    password=password
                )

                request.session["username"] = user.name

                return redirect("dashboard")

            except IntegrityError:
                messages.error(
                    request,
                    "This email is already registered. Please use another email."
                )

        else:
            messages.error(request, "Passwords do not match.")

    return render(request, "register.html")

@never_cache
def dashboard(request):
    username = request.session.get("username")

    if not username:
        return redirect("login")

    user = User.objects.get(name=username)

    ai_scan_count = AiScan.objects.filter(user=user).count()

    watering_count = WateringReminder.objects.filter(
    user=user,
    is_watered=False
).count()
    schedule_count = ScheduleReminder.objects.filter(
    user=user,
    is_done=False
).count()
    upcoming_care_count = watering_count + schedule_count
    myplants = MyPlant.objects.filter(user=user)
    favourite_count = FavoritePlant.objects.filter(user=user).count()
    from datetime import datetime

    missed_reminders = []

    current = datetime.now()

    # Missed Watering Reminders
    for reminder in WateringReminder.objects.filter(user=user, is_watered=False, missed_popup_shown=False):

      reminder_datetime = datetime.combine(
        reminder.watering_date,
        reminder.watering_time
    )

      if reminder_datetime < current:
         missed_reminders.append({
            "message": f"💧 You missed watering {reminder.plant_name}.",
            "id": reminder.id,
            "type": "watering"
        })

    # Missed Schedule Reminders
    for reminder in ScheduleReminder.objects.filter(user=user, is_done=False, missed_popup_shown=False):

       reminder_datetime = datetime.combine(
        reminder.schedule_date,
        reminder.schedule_time
    )

       if reminder_datetime < current:
          missed_reminders.append({
             "message": f"📅 You missed {reminder.task} for {reminder.plant_name}.",
             "id": reminder.id,
             "type": "schedule"
         })
          
    missed_ids = missed_reminders

    return render(request, "dashboard.html", {
        "username": username,
        "user": user,
        "ai_scan_count": ai_scan_count,
        "watering_count": watering_count,
        "schedule_count": schedule_count,
        "upcoming_care_count": upcoming_care_count,
        "myplants": myplants,
        "favourite_count": favourite_count,
        "missed_reminders": missed_reminders,
        "missed_ids": missed_ids,

    })

def search_page(request):

   plant = None
   message = "🌱 Search a plant to see information."
   added_plant_ids = []
   favorite_plant_ids = []

   guest_search_count = request.session.get("guest_search_count", 0)
   guest_search_time = request.session.get("guest_search_time")

   if request.method == "POST":

        if "username" not in request.session:
            if guest_search_time:
             last_search = timezone.datetime.fromisoformat(guest_search_time)

             if timezone.now() - last_search >= timedelta(minutes=30):
                request.session["guest_search_count"] = 0
                guest_search_count = 0

            if guest_search_count >= 3:
                return render(request, "search.html", {
                    "plant": None,
                    "message": "🔒 Please login or register to continue using Search."
                })

            request.session["guest_search_count"] = guest_search_count + 1
            guest_search_count += 1
            request.session["guest_search_time"] = timezone.now().isoformat()

        search = request.POST.get("q", "").strip().lower()
        

        aliases = {
            "rose": "Rosa lucieae",
            "tulsi": "Tulasi",
            "aloe vera": "Aloe vera",
            "mango": "Mango Plant",
        }

        search_name = aliases.get(search, search)

        try:
            plant = Plant.objects.get(name__iexact=search_name)
            message = None
            

        except Plant.DoesNotExist:
            message = "🌱 Plant information is not available yet."

   if "username" in request.session:
    user = User.objects.get(name=request.session["username"])

    added_plant_ids = list(
        MyPlant.objects.filter(user=user).values_list("plant_id", flat=True)
    )

    favorite_plant_ids = list(
        FavoritePlant.objects.filter(user=user).values_list("plant_id", flat=True)
    )

   return render(request, "search.html", {
    "plant": plant,
    "message": message,
    "added_plant_ids": added_plant_ids,
    "favorite_plant_ids": favorite_plant_ids,
})

from django.http import JsonResponse

def plant_suggestions(request):
    plants = Plant.objects.values_list("name", flat=True)
    return JsonResponse(list(plants), safe=False)

def ai_scan_page(request):

    plant_data = None

    if request.method == "POST":

        # Guest scan limit
        if "username" not in request.session:
            guest_scan_count = request.session.get("guest_scan_count", 0)
            guest_scan_time = request.session.get("guest_scan_time")

            if guest_scan_time:
                last_scan = timezone.datetime.fromisoformat(guest_scan_time)

                if timezone.now() - last_scan >= timedelta(minutes=30):

                 request.session["guest_scan_count"] = 0
                 guest_scan_count = 0

                 guest_scan_count = request.session.get("guest_scan_count", 0)

            if guest_scan_count >= 3:
                return render(request, "aiscan.html", {
                    "limit_reached": True
                })

            request.session["guest_scan_count"] = guest_scan_count + 1
            request.session["guest_scan_time"] = timezone.now().isoformat()
            if "username" in request.session:

             user = User.objects.get(name=request.session["username"])

             today = timezone.now().date()

            if user.ai_scan_date != today:
               user.ai_scan_date = today
               user.ai_scan_count = 0
               user.save()

            if user.ai_scan_count >= 20:
             return render(request, "aiscan.html", {
             "daily_limit_reached": True
          })

        image = request.FILES.get("plantImage")

        if image:

            url = f"https://my-api.plantnet.org/v2/identify/all?api-key={settings.PLANTNET_API_KEY}"

            files = {
                "images": ("plant.jpg", image.read(), image.content_type)
            }

            try:
              response = requests.post(
                 url,
                files=files,
                timeout=20
             )

              print(response.status_code)
              print(response.text)

              response.raise_for_status()

              api_result = response.json()

            except Exception:

                return render(request, "aiscan.html", {
                    "api_error": True
                })
            suggestions = api_result.get("results", [])

            # No plant found
            if not suggestions:

                plant_data = {
                    "name": "Plant not found",
                    "confidence": 0,
                    "watering": None,
                    "sunlight": None,
                    "soil": None,
                    "fertilizer": None,
                    "description": "No plant match found.",
                    "page": "",
                    "low_confidence": True,
                }

            else:

                plant = suggestions[0]
                score = plant.get("score", 0)

                common_names = plant.get("species", {}).get("commonNames", [])

                if common_names:
                    plant_name = common_names[0]
                else:
                    plant_name = plant.get(
                        "species", {}
                    ).get(
                        "scientificNameWithoutAuthor",
                        "Unknown"
                    )

                plant_name_lower = plant_name.lower()

                plant_name_map = {

                    "eggplant": "Brinjal",
                    "aubergine": "Brinjal",

                    "neem": "Neem",
                    "neem tree": "Neem",
                    "indian lilac": "Neem",
                    "azadirachta indica": "Neem",

                    "aloe vera": "Aloe vera",

                    "holy basil": "Tulasi",
                    "tulsi": "Tulasi",

                    "hibiscus": "Hibiscus",

                    "turmeric": "Turmeric",

                    "mango": "Mango Plant",
                    "mango tree": "Mango Plant",

                    "mint": "Mint",

                    "jasmine": "Jasmine",

                    "lucky bamboo": "Lucky Bamboo",

                    "money plant": "Money Plant",

                    "snake plant": "Snake Plant",

                    "lemon": "Lemon",

                    "coconut": "Coconut",

                    "rice": "Rice",

                    "wheat": "Wheat",

                    "lotus": "Lotus",

                    "sunflower": "Sunflower",

                    "watermelon": "Watermelon",
                }

                if "rosa" in plant_name_lower:
                    plant_name = "Rose"
                elif plant_name_lower in plant_name_map:
                    plant_name = plant_name_map[plant_name_lower]

                try:

                    plant_info = Plant.objects.get(name__iexact=plant_name)

                    page = plant_info.page or ""

                    plant_data = {
                        "name": plant_name,
                        "confidence": round(score * 100, 2),
                        "watering": plant_info.watering,
                        "sunlight": plant_info.sunlight,
                        "soil": plant_info.soil,
                        "fertilizer": plant_info.fertilizer,
                        "description": plant_info.description,
                        "page": page,
                        "low_confidence": score < 0.50,
                    }

                    if "username" in request.session:
                        user = User.objects.get(
                            name=request.session["username"]
                        )

                        AiScan.objects.create(
                            user=user,
                            plant_name=plant_name
                        )
                        user.ai_scan_count += 1
                        user.save()

                except Plant.DoesNotExist:

                    plant_data = {
                        "name": plant_name,
                        "confidence": round(score * 100, 2),
                        "watering": None,
                        "sunlight": None,
                        "soil": None,
                        "fertilizer": None,
                        "description": "Care information for this plant is not available in the database yet.",
                        "page": "",
                        "low_confidence": score < 0.50,
                    }

    return render(request, "aiscan.html", {
        "plant_data": plant_data
    })

def about_page(request):
    return render(request, 
'about.html')

def contact_page(request):

    message = None

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        user_message = request.POST.get("message")

        Contact.objects.create(
            name=name,
            email=email,
            message=user_message
        )

        message = "✅ Thank you! Your message has been sent successfully."

    return render(request, "contact.html", {
        "message": message
    })

def aloe_vera(request):
    return render(request, "aloe_vera.html")

def tulasi(request):
    return render(request, "tulasi.html")

def turmeric(request):
    return render(request, "turmeric.html")

def rose(request):
    return render(request, "rose.html")

def hibiscus(request):
    return render(request, "hibiscus.html")

def mango_plant(request):
    return render(request, "mango_plant.html")

def lemon(request):
    return render(request, "lemon.html")

def snake_plant(request):
    return render(request, "snake_plant.html")

def sunflower(request):
    return render(request, "sunflower.html")

def money_plant(request):
    return render(request, "money_plant.html")

def lotus(request):
    return render(request, "lotus.html")

def watermelon(request):
    return render(request, "watermelon.html")

def rice(request):
    return render(request, "rice.html")

def wheat(request):
    return render(request, "wheat.html")

def coconut(request):
    return render(request, "coconut.html")

def brinjal(request):
    return render(request, "brinjal.html")

def lucky_bamboo(request):
    return render(request, "lucky_bamboo.html")

def jasmine(request):
    return render(request, "jasmine.html")

def mint(request):
    return render(request, "mint.html")

def neem(request):
    return render(request, "neem.html")


def logout_page(request):
    request.session.flush()
    return redirect("login")

def watering_page(request):

    if "username" not in request.session:
        return redirect("login")

    user = User.objects.get(name=request.session["username"])

    reminder = None

    if request.GET.get("edit"):
        reminder = WateringReminder.objects.get(
            id=request.GET.get("edit"),
            user=user
        )

    if request.method == "POST":

        plant_name = request.POST.get("plant_name")
        watering_date = request.POST.get("watering_date")
        watering_time = request.POST.get("watering_time")
        repeat = request.POST.get("repeat")
        
        print("DATE =", watering_date)
        print("TIME =", watering_time)
        print("REPEAT =", repeat)

        if request.POST.get("reminder_id"):

            reminder = WateringReminder.objects.get(
                id=request.POST.get("reminder_id"),
                user=user
            )

            reminder.plant_name = plant_name
            reminder.watering_date = watering_date
            reminder.watering_time = watering_time
            reminder.repeat = repeat
            reminder.save()

        else:

            WateringReminder.objects.create(
                user=user,
                plant_name=plant_name,
                watering_date=watering_date,
                watering_time=watering_time,
                repeat=repeat
            )

        return redirect("watering")

    reminders = WateringReminder.objects.filter(
        user=user,
        is_watered=False
    ).order_by("watering_date", "watering_time")

    return render(request, "watering.html", {
        "reminders": reminders,
        "reminder": reminder,
    })

def edit_watering(request, id):

    if "username" not in request.session:
        return redirect("login")

    reminder = WateringReminder.objects.get(id=id)

    if request.method == "POST":

        reminder.plant_name = request.POST.get("plant_name")
        reminder.watering_date = request.POST.get("watering_date")
        reminder.watering_time = request.POST.get("watering_time")
        reminder.repeat = request.POST.get("repeat")

        reminder.save()

        return redirect("watering")

    return render(request, "edit_watering.html", {
        "reminder": reminder
    })
def delete_watering(request, id):

    if "username" not in request.session:
        return redirect("login")

    user = User.objects.get(name=request.session["username"])

    reminder = WateringReminder.objects.get(
        id=id,
        user=user
    )

    reminder.delete()

    return redirect("watering")
from django.utils import timezone

def mark_watered(request, id):

    if "username" not in request.session:
        return redirect("login")

    user = User.objects.get(name=request.session["username"])

    reminder = WateringReminder.objects.get(
        id=id,
        user=user
    )

    reminder.is_watered = True
    reminder.watered_on = timezone.now()
    reminder.save()

    return redirect("watering")


def schedule_page(request):

    if "username" not in request.session:
        return redirect("login")

    user = User.objects.get(name=request.session["username"])

    edit_id = request.GET.get("edit")
    schedule = None

    if edit_id:
        schedule = ScheduleReminder.objects.get(id=edit_id, user=user)

    if request.method == "POST":

        plant_name = request.POST.get("plant_name")
        task = request.POST.get("task")
        schedule_date = request.POST.get("schedule_date")
        schedule_time = request.POST.get("schedule_time")
        repeat = request.POST.get("repeat")

        if request.POST.get("schedule_id"):

            schedule = ScheduleReminder.objects.get(
                id=request.POST.get("schedule_id"),
                user=user
            )

            schedule.plant_name = plant_name
            schedule.task = task
            schedule.schedule_date = schedule_date
            schedule.schedule_time = schedule_time
            schedule.repeat = repeat
            schedule.save()

        else:

            ScheduleReminder.objects.create(
                user=user,
                plant_name=plant_name,
                task=task,
                schedule_date=schedule_date,
                schedule_time=schedule_time,
                repeat=repeat
            )

        return redirect("schedule")

    schedules = ScheduleReminder.objects.filter(
    user=user,
    is_done=False
).order_by("schedule_date", "schedule_time")

    return render(request, "schedule.html", {
        "schedules": schedules,
        "schedule": schedule
    })
def delete_schedule(request, id):

    if "username" not in request.session:
        return redirect("login")

    user = User.objects.get(name=request.session["username"])

    schedule = ScheduleReminder.objects.get(
        id=id,
        user=user
    )

    schedule.delete()

    return redirect("schedule")
def mark_schedule_done(request, id):

    if "username" not in request.session:
        return redirect("login")

    user = User.objects.get(name=request.session["username"])

    schedule = ScheduleReminder.objects.get(
        id=id,
        user=user
    )

    schedule.is_done = True
    schedule.done_on = timezone.now()
    schedule.save()

    return redirect("schedule")

def mark_missed_reminder_seen(request):
    if not request.session.get("username"):
        return redirect("login")

    user = User.objects.get(name=request.session.get("username"))

    from datetime import datetime

    current = datetime.now()

    # Mark missed watering reminders only
    for reminder in WateringReminder.objects.filter(
        user=user,
        is_watered=False,
        missed_popup_shown=False
    ):

        reminder_datetime = datetime.combine(
            reminder.watering_date,
            reminder.watering_time
        )

        if reminder_datetime < current:
            reminder.missed_popup_shown = True
            reminder.save()


    # Mark missed schedule reminders only
    for reminder in ScheduleReminder.objects.filter(
        user=user,
        is_done=False,
        missed_popup_shown=False
    ):

        reminder_datetime = datetime.combine(
            reminder.schedule_date,
            reminder.schedule_time
        )

        if reminder_datetime < current:
            reminder.missed_popup_shown = True
            reminder.save()


    return redirect("dashboard")

def addplant_page(request):

    if "username" not in request.session:
        return redirect("login")

    user = User.objects.get(name=request.session["username"])

    myplants = MyPlant.objects.filter(user=user)

    return render(request, "addplant.html", {
        "myplants": myplants
    })

def add_myplant(request, plant_id):

    if "username" not in request.session:
        return redirect("login")

    user = User.objects.get(name=request.session["username"])

    plant = Plant.objects.get(id=plant_id)

    MyPlant.objects.get_or_create(
        user=user,
        plant=plant
    )

    return redirect("addplant")

def delete_myplant(request, plant_id):

    if "username" not in request.session:
        return redirect("login")

    user = User.objects.get(name=request.session["username"])

    MyPlant.objects.filter(
        user=user,
        plant_id=plant_id
    ).delete()

    return redirect("addplant")

def favorite_plants(request):

    if "username" not in request.session:
        return redirect("login")

    user = User.objects.get(name=request.session["username"])

    favorite_plants = FavoritePlant.objects.filter(user=user)

    return render(request, "favorite_plants.html", {
        "favorite_plants": favorite_plants
    })

def add_favorite_plant(request, plant_id):

    if "username" not in request.session:
        return redirect("login")

    user = User.objects.get(name=request.session["username"])

    plant = Plant.objects.get(id=plant_id)

    FavoritePlant.objects.get_or_create(
        user=user,
        plant=plant
    )

    return redirect("favorite_plants")


def delete_favorite_plant(request, plant_id):

    if "username" not in request.session:
        return redirect("login")

    user = User.objects.get(name=request.session["username"])

    FavoritePlant.objects.filter(
        user=user,
        plant_id=plant_id
    ).delete()

    return redirect("favorite_plants")

def profile_page(request):

    username = request.session.get("username")

    if not username:
        return redirect("login")

    user = User.objects.get(name=username)

    return render(request, "profile.html", {
        "user": user
    })

def edit_profile(request):

    username = request.session.get("username")

    if not username:
        return redirect("login")

    user = User.objects.get(name=username)

    if request.method == "POST":

        if "delete_photo" in request.POST:
            if user.profile_photo:
                user.profile_photo.delete(save=False)
                user.profile_photo = None
                user.save()

            return redirect("profile")

        user.name = request.POST.get("name")

        user.status = request.POST.get("status")

        if request.FILES.get("profile_photo"):
            user.profile_photo = request.FILES["profile_photo"]

        user.save()

        request.session["username"] = user.name

        return redirect("profile")

    return render(request, "edit_profile.html", {
        "user": user
    })

@never_cache
def delete_account(request):

    username = request.session.get("username")

    if not username:
        return redirect("login")

    user = User.objects.get(name=username)

    if request.method == "POST":

        if user.profile_photo:
            user.profile_photo.delete(save=False)

        user.delete()

        request.session.flush()

        return redirect("register")

    return redirect("profile")

def forgot_password(request):

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")

        try:
            user = User.objects.get(
                name=name,
                email=email,
                phone=phone
            )

            request.session["reset_user_id"] = user.id

            return redirect("reset_password")

        except User.DoesNotExist:
            return render(request, "forgot_password.html", {
                "error": "The information you entered does not match our records."
            })

    return render(request, "forgot_password.html")

def reset_password(request):

    user_id = request.session.get("reset_user_id")

    if not user_id:
        return redirect("forgot_password")

    user = User.objects.get(id=user_id)

    if request.method == "POST":

        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            return render(request, "reset_password.html", {
                "error": "Passwords do not match."
            })

        user.password = password
        user.save()

        del request.session["reset_user_id"]

        return render(request, "login.html", {
    "success": "Password changed successfully. Please login with your new password."
})

    return render(request, "reset_password.html")

@csrf_exempt
def save_subscription(request):

    if request.method != "POST":
        return JsonResponse({"status": "failed"})

    if "username" not in request.session:
        return JsonResponse({"status": "login_required"})

    user = User.objects.get(name=request.session["username"])

    data = json.loads(request.body)

    endpoint = data["endpoint"]
    p256dh = data["keys"]["p256dh"]
    auth = data["keys"]["auth"]

    PushSubscription.objects.update_or_create(
        endpoint=endpoint,
        defaults={
            "user": user,
            "p256dh": p256dh,
            "auth": auth,
        },
    )

    return JsonResponse({"status": "success"})


# Create your views here.

