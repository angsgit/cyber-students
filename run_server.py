from logging import basicConfig, INFO, info
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from api.conf import PORT
from api.app import Application

def main():
    basicConfig(level=INFO)

    http_server = HTTPServer(Application())
    http_server.listen(PORT)

    info('Starting server on port ' + str(PORT) + '...')
    IOLoop.current().start()

if __name__ == '__main__':
    main()

# REG SYNTAX FOR WINDOWS PS
# curl -X POST 'http://localhost:4000/students/api/registration' -H 'Content-Type: application/json' -d '{"email":"angad@angad.com","password":"test","displayName":"ANGAD", "phone":"12345", "disability":"none"}'

#LOGIN SYNTAX FOR WINDOWS PS
# curl -X POST -H "Content-Type: application/json" -d '{"email":"angad@angad.com","password":"test"}' http://localhost:4000/students/api/login

# DISPLAY PROFILE
# curl -H "X-TOKEN: INSERT_TOKEN" http://localhost:4000/students/api/user