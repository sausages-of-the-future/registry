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
        organisation_type = prompt_choices(name='Organisation type', resolve=resolve_choice, choices=['central government', 'local government', 'devolved government', 'non-profit', 'commercial'])
        redirect_uri = prompt('OAuth redirect URI')
        for scope in registers.avaliable_scopes:
            if prompt_bool("Register for %s (%s)?" % (scope, registers.avaliable_scopes[scope].lower())):
                scopes.append(scope)

        client = auth.AuthClient.register_service(service_name, service_description, scopes, redirect_uri, organisation_type)

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

        with open("%s/addresses.json" % import_dir, 'rb') as json_file:
            addresses = json.loads(json_file.read().decode(encoding='UTF-8'))
            for address in addresses['addresses']:
                print(address)
                addr = registers.Address()
                addr.address = address['address']
                addr.lat_lng = address['lat_lng']
                addr.save()



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

    type_dict = {'organisations' : registers.Organisation, 'licences' : registers.Licence, 'notices': registers.Notice, 'visas': registers.Visa, 'dataprotection': registers.DataProtection, 'employers': registers.Employer, 'addresses': registers.Address} # add more as needed

    def run(self):
        object_keys = [key for key in self.type_dict.keys()]
        object_type = prompt("Object type (e.g. %s)" % object_keys).lower()
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


class GrantVisa(Command):
    """
    Grants a visa to a user
    """

    def _fake_passport_number(self):
        import random, string
        digits = string.digits
        number = random.sample(digits, 10)
        return ''.join(number)

    def run(self):
        email = prompt('email of user to grant visa to')
        visa_choices=[(1, 'Tier 1 (Entrepreneur) visa'),
                        (2, 'Tier 2 (General) visa'),
                            (3, 'Tier 5 (Temporary Worker)')]

        choice = prompt_choices(name='Visa type', resolve=int, choices=visa_choices)

        visa_type = visa_choices[choice-1][1]
        print("You have chosen:", visa_type)

        person = auth.AuthUser.objects(email=email).first()

        if not person:
            print('No user found for email', email)
            return

        from datetime import datetime, timedelta

        visa = registers.Visa()
        visa.issued_at = datetime.now()
        visa.expires_at = visa.issued_at + timedelta(weeks=52)
        visa.person_uri = person.person_uri
        visa.visa_type = visa_type
        visa.passport_number = self._fake_passport_number()
        visa.save()


class DeleteNonLoginPersons(Command):
    """
    Deletes People in db that aren't linked to auth user accounts.
    """
    def run(self):
        auth_users = auth.AuthUser.objects.all()
        people = registers.Person.objects.all()
        auth_users_person_id = [user.person_uri.split('/')[-1] for user in auth_users]

        for person in people:
            if str(person.id) not in auth_users_person_id:
                print("Delete person with id %s" % person.id)
                person.delete()
            else:
                print("Keep person with id %s" % person.id)


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
manager.add_command('grant-visa', GrantVisa())
manager.add_command('delete-non-login-people', DeleteNonLoginPersons())

if __name__ == "__main__":
    manager.run()
