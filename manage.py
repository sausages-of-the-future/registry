from flask.ext.script import Manager, Command, prompt_bool, prompt, prompt_pass, prompt_choices
from mongoengine import connect
from registry import app, registers, auth
from datetime import datetime

class RegisterService(Command):
    """
    Register a new service, returns a client ID and a client secret
    that you need to copy into the client app
    """
    def run(self):
        scopes = []
        service_name = prompt('Service name')
        service_description = prompt('Description')
        redirect_uri = prompt('OAuth redirect URI')
        for scope in registers.avaliable_scopes:
            if prompt_bool("Register for %s (%s)?" % (scope, registers.avaliable_scopes[scope].lower())):
                scopes.append(scope)

        client = auth.AuthClient.register_service(service_name, service_description, scopes, redirect_uri)

        print "You client ID is: %s" % client.client_id
        print "You client secret is: %s" % client.client_secret

class ResetAll(Command):
    """
    Remove *everything* from mongodb
    """
    def run(self):
        if prompt_bool('Reset everything?'):
            db = connect(app.config['MONGODB_DB'])
            db.drop_database(app.config['MONGODB_DB'])

class CreateUser(Command):
    """
    Create an Auth user and a Person (which are intentionally seperate things),
    then create an association between them
    """
    def run(self):
        email = prompt('User email')
        password = prompt_pass('User password')
        born_at = prompt('Date of birth eg 1978-05-01')

        person = registers.Person()
        person.born_at = datetime.strptime(born_at, '%Y-%m-%d')
        person.save()

        user = auth.AuthUser.create_user(email, password)
        user.person_uri = person.uri
        user.save()

#register commands
manager = Manager(app)
manager.add_command('register-service', RegisterService())
manager.add_command('reset-all', ResetAll())
manager.add_command('create-user', CreateUser())

if __name__ == "__main__":
    manager.run()
