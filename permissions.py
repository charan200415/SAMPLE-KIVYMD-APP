from kivy.utils import platform
from kivy.clock import Clock
from kivy.logger import Logger

if platform == 'android':
    from android.permissions import request_permissions, check_permission, Permission

class AndroidPermissions:
    def __init__(self, callback):
        self.permission_callback = callback
        
        if platform == 'android':
            self.permissions = [
                Permission.INTERNET,
                Permission.ACCESS_NETWORK_STATE,
                Permission.ACCESS_WIFI_STATE
            ]
            Clock.schedule_once(self.check_permissions, 0)
        else:
            Clock.schedule_once(lambda dt: callback(), 0)

    def check_permissions(self, dt):
        if platform == 'android':
            if all([check_permission(p) for p in self.permissions]):
                self.permission_callback()
            else:
                request_permissions(self.permissions, self.permission_callback)
