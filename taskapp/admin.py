from django.contrib import admin
from .models import TaskMakerUser, Project, Task, Comment, File, ProjectMember, Reminder


admin.site.register(TaskMakerUser)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Comment)
admin.site.register(File)
admin.site.register(ProjectMember)
admin.site.register(Reminder)

