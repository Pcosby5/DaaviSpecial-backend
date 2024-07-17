from django.contrib import admin
from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered
# from .models import User, UserAdmin

# Attempt to register all models
models = apps.get_models()

for model in models:
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass

# Alternatively, if you only want to handle the User model:
# try:
#     admin.site.register(User, UserAdmin)
# except AlreadyRegistered:
#     pass
