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

        encrypted_address = self.current_user.get('address')
        if  encrypted_address:
            self.response['address'] = decrypt_field(encrypted_address)

        encrypted_dob = self.current_user.get('dob')
        if encrypted_dob:
            self.response['dob'] = decrypt_field(encrypted_dob)

        self.write_json()


