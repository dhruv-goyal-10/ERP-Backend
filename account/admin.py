from django.contrib import admin
from account.models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class UserModelAdmin(BaseUserAdmin):
  # The fields to be used in displaying the User model.
  # These override the definitions on the base UserModelAdmin
  # that reference specific fields on auth.User.
  list_display = ('userID','email', 'name', 'is_admin','is_tea','is_stu')
  list_filter = ('is_admin',)
  fieldsets = (
      ('User Credentials', {'fields': ('userID', 'password')}),
      ('Personal info', {'fields': ('name', 'email')}),
      ('Permissions', {'fields': ('is_admin','is_tea','is_stu',)}),
  )
  # add_fieldsets is not a standard ModelAdmin attribute. UserModelAdmin
  # overrides get_fieldsets to use this attribute when creating a user.
  add_fieldsets = (
      (None, {
          'classes': ('wide',),
          'fields': ('userID','email', 'name', 'password1', 'password2'),
      }),
  )
  search_fields = ('email',)
  ordering = ('email',)
  filter_horizontal = ()


# Now register the new UserModelAdmin...


class StudentAdmin(admin.ModelAdmin):
    list_display = ('userID','name', 'user','DOB')
    search_fields = ('name',)



class TeacherAdmin(admin.ModelAdmin):
    list_display = ('userID','name', 'user','DOB')
    search_fields = ('name',)


class UpdatesAdmin(admin.ModelAdmin):
    list_display = ('id', 'title','description', 'showto')
    search_fields = ('title',)
    
    
class KlassAdmin(admin.ModelAdmin):
    list_display = ('id', 'department', 'semester', 'section')
    search_fields = ('id', 'department__name', 'semester', 'section')
    ordering = ['department__name', 'semester', 'section']
    
    
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')
    search_fields = ('name', 'id')
    ordering = ['name']
    

admin.site.register(Subject)
admin.site.register(AssignClass)
admin.site.register(User, UserModelAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Klass, KlassAdmin)
admin.site.register(Update, UpdatesAdmin)