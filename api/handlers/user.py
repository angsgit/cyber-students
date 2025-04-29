from tornado.web import authenticated
from .auth import AuthHandler
from api.handlers.encryption import decrypt_field


class UserHandler(AuthHandler):

    @authenticated
    def get(self):
        self.set_status(200)
        self.response['email'] = self.current_user.get('email')

        encrypted_display = self.current_user.get('displayName')
        if encrypted_display:
            self.response['displayName'] = decrypt_field(encrypted_display)

        encrypted_phone = self.current_user.get('phone')
        if encrypted_phone:
            self.response['phone'] = decrypt_field(encrypted_phone)

        encrypted_disability = self.current_user.get('disability')
        if encrypted_disability:
            self.response['disability'] = decrypt_field(encrypted_disability)

        self.write_json()


