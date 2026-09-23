from django.contrib import admin

from .models import FoundingMember, Notice, OrganizationInformation, SliderItem


admin.site.register(OrganizationInformation)
admin.site.register(Notice)
admin.site.register(FoundingMember)
admin.site.register(SliderItem)