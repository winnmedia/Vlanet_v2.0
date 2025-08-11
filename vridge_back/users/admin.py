from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.db.models import Count
from . import models
from projects.models import Project


@admin.register(models.User)
class UserAdmin(UserAdmin):
    list_display = (
        "id",
        "username",
        "nickname",
        "login_method",
        "get_status",
        "get_project_count",
        "date_joined",
    )

    list_display_links = (
        "id",
        "nickname",
        "date_joined",
    )

    list_filter = (
        "is_staff",
        "is_active",
        "is_superuser",
    )

    search_fields = (
        "id",
        "username",
    )

    search_help_text = "id or email"

    fieldsets = (
        (
            "",
            {
                "fields": UserAdmin.fieldsets[0][1]["fields"]
                + (
                    "login_method",
                    "email_secret",
                ),
            },
        ),
        (
            "",
            {
                "fields": ("nickname",),
            },
        ),
        (
            "",
            {
                "fields": (
                    "date_joined",
                    "last_login",
                ),
            },
        ),
        (
            "",
            {
                "classes": ("collapse",),
                "fields": (
                    "is_staff",
                    "is_active",
                    "is_superuser",
                ),
            },
        ),
    )

    readonly_fields = ["date_joined", "last_login"]
    ordering = ("-date_joined",)

    def get_form(self, request, obj=None, **kwargs):
        form = super(UserAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields["username"].label = "ID"
        return form
    
    def get_status(self, obj):
        if obj.is_superuser:
            return format_html('<span style="color: #ff4545; font-weight: bold;"> </span>')
        elif obj.is_staff:
            return format_html('<span style="color: #0059db; font-weight: bold;"></span>')
        elif obj.is_active:
            return format_html('<span style="color: #27ae60;"></span>')
        else:
            return format_html('<span style="color: #e74c3c;"></span>')
    get_status.short_description = ''
    
    def get_project_count(self, obj):
        owned = obj.projects.count()
        # Members       
        from projects.models import Members
        member = Members.objects.filter(user=obj).count()
        total = owned + member
        return format_html(
            '<span style="color: #0059db; font-weight: bold;">{}</span> <small>(: {}, : {})</small>',
            total, owned, member
        )
    get_project_count.short_description = ''


@admin.register(models.EmailVerify)
class EmailVerifyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "__str__",
        "updated",
        "created",
    )

    list_display_links = list_display


@admin.register(models.UserMemo)
class UserMemoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "__str__",
        "updated",
        "created",
    )

    list_display_links = list_display


@admin.register(models.UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "company",
        "position",
        "phone",
        "has_profile_image",
        "updated",
    )
    
    list_display_links = ("id", "user")
    
    search_fields = ("user__username", "user__nickname", "company", "position")
    
    list_filter = ("company", "position", "updated")
    
    def has_profile_image(self, obj):
        return format_html(
            '<span style="color: {};">{}</span>',
            "#27ae60" if obj.profile_image else "#e74c3c",
            "" if obj.profile_image else ""
        )
    has_profile_image.short_description = " "
    
    fieldsets = (
        ("", {
            "fields": ("user",)
        }),
        (" ", {
            "fields": ("profile_image", "bio", "phone", "company", "position")
        }),
        (" ", {
            "fields": ("created", "updated"),
            "classes": ("collapse",)
        }),
    )
    
    readonly_fields = ("created", "updated")
