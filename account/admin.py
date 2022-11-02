from django.contrib import admin
from account.models import User, Student, Teacher
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
admin.site.register(User, UserModelAdmin)

class StudentAdmin(admin.ModelAdmin):
    list_display = ('userID','name', 'user','DOB')
    search_fields = ('name',)

admin.site.register(Student, StudentAdmin)

class TeacherAdmin(admin.ModelAdmin):
    list_display = ('userID','name', 'user','DOB')
    search_fields = ('name',)
admin.site.register(Teacher, TeacherAdmin)