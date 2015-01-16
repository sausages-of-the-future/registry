from flask.ext.script import Manager, Command, prompt_bool, prompt, prompt_pass, prompt_choices
from mongoengine import connect
from registry import app, registers, auth
from datetime import datetime
import os
import json

def resolve_choice(value):
    return value

import_dir = '%s/import-data' % os.path.dirname(os.path.abspath(__file__))

class RegisterService(Command):
    """
    Register a new service, returns a client ID and a client secret
    that you need to copy into the client app
    """
    def run(self):
        scopes = []
        service_name = prompt('Service name')
        service_description = prompt('Description')
        service_organisation_type = prompt_choices(name='Organisation type', resolve=resolve_choice, choices=['central government', 'local government', 'devolved government', 'non-profit', 'commercial'])
        redirect_uri = prompt('OAuth redirect URI')
        for scope in registers.avaliable_scopes:
            if prompt_bool("Register for %s (%s)?" % (scope, registers.avaliable_scopes[scope].lower())):
                scopes.append(scope)

        client = auth.AuthClient.register_service(service_name, service_description, scopes, redirect_uri, service_organisation_type)

        print("You client ID is: %s" % client.client_id)
        print("You client secret is: %s" % client.client_secret)

class DeregisterService(Command):
    """
    Register a new service, returns a client ID and a client secret
    that you need to copy into the client app
    """
    def run(self):
        client_id = prompt('Client ID')
        client = auth.AuthClient.objects.filter(client_id=client_id)[0]
        grants = auth.AuthGrant.objects.filter(client=client)
        tokens = auth.AuthToken.objects.filter(client=client)
        for grant in grants:
            grant.delete()
        for token in tokens:
            token.delete()
        client.delete()

class ResetAll(Command):
    """
    Remove *everything* from mongodb
    """
    def run(self):
        if prompt_bool('Reset everything?'):
            db = connect(app.config['MONGODB_DB'])
            db.drop_database(app.config['MONGODB_DB'])

class ListClients(Command):
    """
    List all the clients (for setup purposes only)
    """
    def run(self):
        clients =  auth.AuthClient.objects.all()
        for client in clients:
            print("\n")
            print(client.name)
            print("ID: %s" % client.client_id)
            print("Secret: %s" % client.client_secret)
            print("Scopes: %s" % client._default_scopes)
            print("URI: %s" % client._redirect_uris)

class ImportData(Command):
    """
    Import all the data needed for a demo
    """
    def run(self):
        registers.List.objects.delete()

        # list of occupations
        with open("%s/shortage-occupation-list.json" % import_dir, 'rb') as json_file:
            job_list = json.loads(json_file.read().decode(encoding='UTF-8'))
            list_ = registers.List()
            list_.name="Shortage occupation list"
            list_.list_data = job_list['jobs']
            list_.save()

        #Amenities - libraries
        with open("%s/libraries.json" % import_dir, 'rb') as json_file:
            libraries = json.loads(json_file.read().decode(encoding='UTF-8'))



class CreateUser(Command):
    """
    Create an Auth user and a Person (which are intentionally seperate things),
    then create an asociation between them
    """
    def run(self):
        full_name = prompt('Full name')
        email = prompt('User email')
        password = prompt_pass('User password')
        born_at = prompt('Date of birth eg 1978-05-01')

        person = registers.Person()
        person.born_at = datetime.strptime(born_at, '%Y-%m-%d')
        person.full_name = full_name
        person.save()

        user = auth.AuthUser.create_user(email, password)
        user.person_uri = person.uri
        user.save()


class DeleteObject(Command):
    """
    Deletes the object in db for a give mongo object id
    """
    def run(self):
        object_id = prompt('Object ID')
        object = registers.RegisterBase.objects.filter(id=object_id)[0]
        object.delete()

class DeleteObjectByType(Command):
    """
    Deletes the object in db for a give register type - be careful
    """

    type_dict = {'organisations' : registers.Organisation, 'licences' : registers.Licence} # add more as needed

    def run(self):
        object_type = prompt("Object type (e.g. organisation)").lower()
        type_class = self.type_dict.get(object_type)
        if not type_class:
            print("Can't find type to delete %s" % type_class)
        else:
            objects = type_class.objects.all()
            for object in objects:
                print("Deleting %s" % object.id)
                object.delete()
            else:
                print("No objects of type %s found" % object_type)

#register commands
manager = Manager(app)
manager.add_command('register-service', RegisterService())
manager.add_command('deregister-service', DeregisterService())
manager.add_command('reset-all', ResetAll())
manager.add_command('create-user', CreateUser())
manager.add_command('list-clients', ListClients())
manager.add_command('import-data', ImportData())
manager.add_command('delete-object', DeleteObject())
manager.add_command('delete-object-type', DeleteObjectByType())

if __name__ == "__main__":
    manager.run()
