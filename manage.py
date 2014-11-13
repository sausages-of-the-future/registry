from flask.ext.script import Manager, Command, prompt_bool, prompt, prompt_pass, prompt_choices
from mongoengine import connect
from register import app, models
from datetime import datetime

class RegisterService(Command):

    def run(self):
        scopes = []
        service_name = prompt('Service name')
        service_description = prompt('Description')
        redirect_uri = prompt('OAuth redirect URI')
        for scope in models.avaliable_scopes:
            if prompt_bool("Register for %s (%s)?" % (scope, models.avaliable_scopes[scope].lower())):
                scopes.append(scope)

        client = models.AuthClient.register_service(service_name, service_description, scopes, redirect_uri)

        print "You client ID is: %s" % client.client_id
        print "You client secret is: %s" % client.client_secret

class ResetAll(Command):

    def run(self):
        if prompt_bool('Reset everything?'):
            db = connect(app.config['MONGODB_SETTINGS']['DB'])
            db.drop_database(app.config['MONGODB_SETTINGS']['DB'])

class CreateUser(Command):

    def run(self):
        email = prompt('User email')
        password = prompt_pass('User password')
        born_at = prompt('Date of birth eg 1978-05-01')

        person = models.Person()
        person.born_at = datetime.strptime(born_at, '%Y-%m-%d')
        person.save()

        user = models.AuthUser.create_user(email, password)
        user.person_uri = person.uri
        user.save()

manager = Manager(app)
manager.add_command('register-service', RegisterService())
manager.add_command('reset-all', ResetAll())
manager.add_command('create-user', CreateUser())

if __name__ == "__main__":
    manager.run()
