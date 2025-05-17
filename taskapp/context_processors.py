from .models import Project, ProjectMember

def user_projects(request):
    if request.user.is_authenticated:
        projects = Project.objects.filter(projectmember__user=request.user).distinct()
        projects_with_members = []
        for project in projects:
            members = ProjectMember.objects.filter(project=project)
            projects_with_members.append({
                'project': project,
                'members': members
            })
        return {'projects_with_members': projects_with_members}
    return {}
