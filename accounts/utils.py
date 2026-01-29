def is_teacher(user):
    return user.profile.role == 'teacher'

def is_student(user):
    return user.profile.role == 'student'

