from datetime import datetime
from flask import request, current_app
from flask.ext.restful import reqparse, abort, Resource, inputs
from mongoengine import DoesNotExist, ValidationError
from registry import api, registers, app, oauth
#from flask_restful.utils import cors

def mongo_get_or_abort(_id, cls):
    try:
        return cls.objects.get(id=_id)
    except ValidationError:
        abort(404, message="%s %s does not exist" % (cls._class_name, _id))
    except DoesNotExist:
        abort(404, message="%s %s does not exist" % (cls._class_name, _id))

class About(Resource):
    """A bit of a hack for getting details associated with the token"""
    def options(self):
        pass

    @oauth.require_oauth()
    def get(self):
        return {'person': request.oauth.user.person_uri}

class Person(Resource):

    def options(self):
        pass

    def put(self):
        return "Forbidden", 403

    def delete(self):
        return "Forbidden", 403

    @oauth.require_oauth('person:view')
    def get(self, _id):
        person = mongo_get_or_abort(_id, registers.Person)
        if person.uri == request.oauth.user.person_uri:
            return person.to_dict(), 200
        else:
            return 'Unauthorized', 401

class PersonList(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        super(People, self).__init__()

    def options(self):
        pass

    def get(self):
        return "Forbidden", 403

    @oauth.require_oauth('people:add')
    def post(oauth, self):
        #this would be gov only
        return "Not Implemented", 501

class Licence(Resource):

    def options(self):
        pass

    @oauth.require_oauth()
    def get(self, _id):

        valid_view_scope, req = oauth.verify_request(['licence:view'])
        if valid_view_scope:
            licence = mongo_get_or_abort(_id, registers.Licence)
            #if belongs to use token, then we can return more info
            #todo: return different data for each of these states
            if licence.person_uri == request.oauth.user.person_uri:
                return licence.to_dict()
            else:
                return licence.to_dict()
        else:
            return mongo_get_or_abort(_id, registers.Licence).to_dict()


class LicenceList(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        super(LicenceList, self).__init__()

    def options(self):
        pass

    @oauth.require_oauth('licence:view')
    def get(self):
        result = []
        licences = registers.Licence.objects(person_uri=request.oauth.user.person_uri)
        for licence in licences:
            result.append(licence.to_dict())
        return result

    @oauth.require_oauth('licence:add')
    def post(self):

        self.parser.add_argument('type_uri', type=inputs.url, required=True, location='json', help="Must be a valid URI")
        self.parser.add_argument('starts_at', type=inputs.date, required=True, location='json', help="Must be a valid date eg ISO 2013-01-01")
        self.parser.add_argument('ends_at', type=inputs.date, required=True, location='json', help="Must be a valid date eg ISO 2013-01-01")
        args = self.parser.parse_args()

        licence = registers.Licence()

        licence.person_uri = request.oauth.user.person_uri
        licence.type_uri = args['type_uri']
        licence.starts_at = args['starts_at']
        licence.ends_at = args['ends_at']

        try:
            licence.save()
        except ValidationError as e:
            current_app.logger.debug('exception %s' % e)
            return "Failed", 500

        return licence.uri, 201

class List(Resource):

    def options(self):
        pass

    def put(self):
        return "Forbidden", 403

    def delete(self):
        return "Forbidden", 403

    def get(self, _id):
        list_ = mongo_get_or_abort(_id, registers.List)
        return list_.to_dict()

class ListList(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        super(ListList, self).__init__()

    def options(self):
        pass

    def get(self):
        result = []
        lists = registers.List.objects()
        for list_ in lists:
            result.append(list_.to_dict())
        return result

    def post(oauth, self):
        return "Forbidden", 403

class Organisation(Resource):

    def options(self):
        pass

    def put(self):
        return "Forbidden", 403

    def delete(self):
        return "Forbidden", 403

    def get(self, _id):
        organisation = mongo_get_or_abort(_id, registers.Organisation)

        # taking a short cut and swap in director names for the moment
        # look again at this access and how it's mediated as www app that
        # is first client of this end point, does not have permissions to view
        # person register and therefore can't resolve a person url
        director_names = []
        for person_uri in organisation.directors:
            person_id = person_uri.split('/')[-1]
            person = registers.Person.objects(id=person_id).first()
            director_names.append(person.full_name)

        # this is for the preceding hack
        organisation.directors = director_names
        return organisation.to_dict()

class OrganisationList(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        super(OrganisationList, self).__init__()

    def options(self):
        pass

    def get(self):
        result = []
        organisations = registers.Organisation.objects()
        for organisation in organisations:
            result.append(organisation.to_dict())
        return result

    @oauth.require_oauth('organisation:add')
    def post(self):

        #this would be gov only, for a particular user
        self.parser.add_argument('name', required=True, location='json', help="An organisaiton must have a name")
        self.parser.add_argument('organisation_type', required=True, location='json', help="An organisaiton must type")
        self.parser.add_argument('activities',  location='json')
        self.parser.add_argument('register_data', type=inputs.boolean, location='json')
        self.parser.add_argument('register_employer', type=inputs.boolean,location='json')
        self.parser.add_argument('register_construction', type=inputs.boolean, location='json')

        args = self.parser.parse_args()

        from flask import current_app
        current_app.logger.info('GOT THE FOLLOWING %s' % args)

        organisation = registers.Organisation()
        organisation.name = args['name']
        organisation.organisation_type = args['organisation_type']
        organisation.activities = args['activities']
        organisation.created_at = datetime.now()

        organisation.directors.append(request.oauth.user.person_uri)
        # store the name and create directorship record from Person
        # to the organisation?

        register_data = args['register_data']
        register_employer = args['register_employer']

        organisation.register_construction = args['register_construction']
        # alternatively store person resource name?

        #TODO save record to DataProtection and Employers Register if
        # register_data and register_employer are true
        # maybe store link from org to data protection registration record
        # as well instead of boolean above?

        try:
            organisation.save()

            if register_data:
                data_protection = registers.DataProtection()
                data_protection.organisation_uri = organisation.uri
                data_protection.registration_date = datetime.now()
                data_protection.save()
                organisation.register_data = data_protection.uri
                organisation.save()

            if register_employer:
                employer_registration = registers.Employer()
                employer_registration.organisation_uri = organisation.uri
                employer_registration.registration_date = datetime.now()
                employer_registration.save()
                organisation.register_employer = employer_registration.uri
                organisation.save()

        except ValidationError as e:
            current_app.logger.info('WAT %s' % e)
            return "Failed", 500
        return organisation.uri, 201


class DataProtection(Resource):

    def options(self):
        pass

    def put(self):
        return "Forbidden", 403

    def delete(self):
        return "Forbidden", 403

    def get(self, _id):
        return mongo_get_or_abort(_id, registers.DataProtection).to_dict()


class DataProtectionList(Resource):

    def options(self):
        pass

    def post(oauth, self):
        return "Not Implemented", 501

    def get(self):
        return "Forbidden", 403


class Employer(Resource):

    def options(self):
        pass

    def put(self):
        return "Forbidden", 403

    def delete(self):
        return "Forbidden", 403

    def get(self, _id):
        return mongo_get_or_abort(_id, registers.Employer).to_dict()


class EmployerList(Resource):

    def options(self):
        pass

    def post(oauth, self):
        return "Not Implemented", 501

    def get(self):
        return "Forbidden", 403


#routes
api.add_resource(About, '/about')
api.add_resource(Person, '/people/<string:_id>')
api.add_resource(PersonList, '/people')
api.add_resource(Licence, '/licences/<string:_id>')
api.add_resource(LicenceList, '/licences')
api.add_resource(List, '/lists/<string:_id>')
api.add_resource(ListList, '/lists')
api.add_resource(OrganisationList, '/organisations')
api.add_resource(Organisation, '/organisations/<string:_id>')
api.add_resource(DataProtectionList, '/dataprotection')
api.add_resource(DataProtection, '/dataprotection/<string:_id>')
api.add_resource(EmployerList, '/employers')
api.add_resource(Employer, '/employers/<string:_id>')
