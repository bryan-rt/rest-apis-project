import functools

user = {'username': 'bryan', 'access_level': 'admin'}

def make_secure(access_level):
    def decorator(func):
        @functools.wraps(func)
        def secure_function(*args, **kwargs):
            if user['access_level'] != access_level:
                raise PermissionError(f"Sorry {user['username']}, you do not have {access_level} permission to access this function.")
            return func(*args, **kwargs)
        return secure_function
    return decorator

@make_secure('admin')
def get_admin_password():
    return "admin_password: 123"

@make_secure('guest')
def get_dashboard_password():
    return "dashboard_password: 456"

print(get_admin_password())
#print(get_dashboard_password())