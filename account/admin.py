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


class StudentAdmin(admin.ModelAdmin):
    list_display = ('userID','name', 'user','DOB')
    search_fields = ('name',)
    
class StudentInline(admin.TabularInline):
    model = Student
    extra = 0


class TeacherAdmin(admin.ModelAdmin):
    list_display = ('userID','name', 'user','DOB')
    search_fields = ('name',)
    
class TeacherInline(admin.TabularInline):
    model = Teacher
    extra = 0

    
class ClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'department', 'year', 'section')
    search_fields = ('id', 'department__name', 'year', 'section')
    ordering = ['department__name', 'year', 'section']
    inlines = [StudentInline]
    
class ClassInline(admin.TabularInline):
    model = Class
    extra = 0

class MembershipInline(admin.TabularInline):
    model = Subject.department.through
    
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name', 'department__name')
    
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')
    search_fields = ('name', 'id')
    ordering = ['name']
    inlines = [ClassInline, TeacherInline, MembershipInline]
    
class AssignAdmin(admin.ModelAdmin):
    list_display = ('class_id', 'subject', 'teacher')
    search_fields = ('class_id__department__name', 'class_id__id', 'subject__name', 'teacher__name')
    ordering = ['class_id__department__name', 'class_id__id', 'subject__code']
    raw_id_fields = ['class_id', 'subject', 'teacher']
    
class UpdatesAdmin(admin.ModelAdmin):
    list_display = ('id', 'title','description', 'showto')
    search_fields = ('title',)


class TeacherFeedbackAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'feed','student')
    search_fields = ('teacher__name',)
    ordering = [ 'teacher__name', 'feed']
    

class StudentFeedbackAdmin(admin.ModelAdmin):
    list_display = ('student', 'feed','teacher')
    search_fields = ('student__name',)
    ordering = [ 'student__name', 'feed']


admin.site.register(Subject, SubjectAdmin)
admin.site.register(AssignClass, AssignAdmin)
admin.site.register(User, UserModelAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(Update, UpdatesAdmin)
admin.site.register(TeacherFeedback, TeacherFeedbackAdmin)
admin.site.register(StudentFeedback, StudentFeedbackAdmin)
