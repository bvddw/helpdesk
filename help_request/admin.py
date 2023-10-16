from django.contrib import admin
from .models import HelpRequest, DeclinedRequest

admin.site.register(HelpRequest)
admin.site.register(DeclinedRequest)