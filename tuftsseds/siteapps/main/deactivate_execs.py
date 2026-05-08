from .models import ExecMembers

def check_and_deactivate_active_members():
    execs = ExecMembers.objects.filter(active=True)
    for execmember in execs:
        execmember.deactivate()
    
    