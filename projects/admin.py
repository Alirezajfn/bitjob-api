from django.contrib import admin

from .models import Category, Tag, Project, ProjectFile


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    list_filter = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class ProjectFileInline(admin.TabularInline):
    model = ProjectFile
    extra = 1


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'owner', 'budget', 'deadline', 'status', 'created_at')
    list_filter = ('status', 'category', 'owner')
    search_fields = ('title', 'description', 'owner__username')
    autocomplete_fields = ['category', 'owner']
    inlines = [ProjectFileInline]
    filter_horizontal = ('tags',)
    list_editable = ('status', 'budget', 'deadline')


class ProjectFileAdmin(admin.ModelAdmin):
    list_display = ('project', 'file', 'uploaded_at')
    search_fields = ('project__title',)


# Register your models with the admin site
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectFile, ProjectFileAdmin)
