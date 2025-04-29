from json import dumps
from logging import info
from tornado.escape import json_decode, utf8
from tornado.gen import coroutine
import bcrypt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os
import base64
from api.conf import AES_KEY


from .base import BaseHandler

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

    # Get AES key from conf.py
        key = AES_KEY

#---------------------------------------------------------------------------
        # --- Encrypt displayName ---

        # Generate random IV
        iv = os.urandom(16)

        # Pad the data
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(display_name.encode('utf-8')) + padder.finalize()

        # Encrypt
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        # Save IV + ciphertext together (encode for storage)
        display_name_encrypted = base64.b64encode(iv + ciphertext).decode('utf-8')

# ---------------------------------------------------------------------------
        # --- Encrypt PHONE ---

        phone_number = body.get('phone', '')  # Optional, in case not provided
        if not isinstance(phone_number, str):
            phone_number = str(phone_number)  # Ensure it is a string before encrypting

        iv_phone = os.urandom(16)

        padder = padding.PKCS7(128).padder()
        padded_phone = padder.update(phone_number.encode('utf-8')) + padder.finalize()

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv_phone), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext_phone = encryptor.update(padded_phone) + encryptor.finalize()

        phone_encrypted = base64.b64encode(iv_phone + ciphertext_phone).decode('utf-8')

        yield self.db.users.insert_one({
            'email': email,
            'password': hashed_password,
            'displayName': display_name_encrypted,
            'phone': phone_encrypted
        })

        self.set_status(200)
        self.response['email'] = email
        self.response['displayName'] = display_name

        self.write_json()
