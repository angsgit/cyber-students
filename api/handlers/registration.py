from tornado.escape import json_decode, utf8
from tornado.gen import coroutine
import bcrypt
from api.conf import AES_KEY
from .base import BaseHandler
from api.handlers.encryption import encrypt_field


class RegistrationHandler(BaseHandler):

    @coroutine
    def post(self):
        try:
            body = json_decode(self.request.body)
            email = body['email'].lower().strip()
            if not isinstance(email, str):
                raise Exception()
            password = body['password']
            if not isinstance(password, str):
                raise Exception()

            # HASH THE PASSWORD and decode the utf8 string for storing in db
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            display_name = body.get('displayName')
            if display_name is None:
                display_name = email
            if not isinstance(display_name, str):
                raise Exception()
        except Exception as e:
            self.send_error(400, message='You must provide an email address, password and display name!')
            return

        phone = body.get('phone', '')
        if not isinstance(phone, str):
            phone = str(phone)

        disability = body.get('disability', '')
        if not isinstance(disability, str):
            disability = str(disability)

        address = body.get('address', '')
        if not isinstance(address, str):
            address = str(address)

        dob = body.get('dob', '')
        if not isinstance(dob, str):
            dob = str(dob)

        if not email:
            self.send_error(400, message='The email address is invalid!')
            return

        if not password:
            self.send_error(400, message='The password is invalid!')
            return

        if not display_name:
            self.send_error(400, message='The display name is invalid!')
            return

        user = yield self.db.users.find_one({
          'email': email
        }, {})

        if user is not None:
            self.send_error(409, message='A user with the given email address already exists!')
            return


        # Encrypt fields:
        display_name_encrypted = encrypt_field(display_name)
        phone_encrypted = encrypt_field(phone)
        disability_encrypted = encrypt_field(disability)
        address_encrypted = encrypt_field(address)
        dob_encrypted = encrypt_field(dob)

        #---------------------------------------------------------------------------

        yield self.db.users.insert_one({
            'email': email,
            'password': hashed_password,
            'displayName': display_name_encrypted,
            'phone': phone_encrypted,
            'disability': disability_encrypted,
            'address': address_encrypted,
            'dob': dob_encrypted
        })

        self.set_status(200)
        self.response['email'] = email
        self.response['displayName'] = display_name

        self.write_json()
