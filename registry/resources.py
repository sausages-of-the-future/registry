from flask import request, current_app, abort
from flask.ext.restful import reqparse, abort, Resource, inputs
from mongoengine import DoesNotExist, ValidationError
from registry import api, registers, app, oauth

from registry.models import LicenceModel, LicenseFields
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
            return LicenceModel.find_by_id(_id)
        else:
            return abort(403)

class LicenceList(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        super(LicenceList, self).__init__()

    def options(self):
        pass

    @oauth.require_oauth('licence:view')
    def get(self):
        return LicenceModel.find_by_user(request.oauth.user.pk)

    @oauth.require_oauth('licence:add')
    def post(self):

        self.parser.add_argument('type_uri', type=inputs.url, required=True, location='json', help="Must be a valid URI")
        self.parser.add_argument('starts_at', type=inputs.date, required=True, location='json', help="Must be a valid date eg ISO 2013-01-01")
        self.parser.add_argument('ends_at', type=inputs.date, required=True, location='json', help="Must be a valid date eg ISO 2013-01-01")
        self.parser.add_argument('licence_type', type=str, required=True, location='json', help="The type of licence")
        args = self.parser.parse_args()

        fields = LicenseFields()
        fields.issuedFor = str(request.oauth.user.pk)
        fields.validFrom = args['starts_at']
        fields.validUntil = args['ends_at']
        licence = LicenceModel()
        licence.fields = fields
        licence.type = 'Licence'
        licence.tags = [args['licence_type']]

        try:
            licence.save()
        except Exception as e:
            current_app.logger.debug('exception %s' % e)
            return "Failed", 500

        return "OK", 201


class OrganisationList(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        super(OrganisationList, self).__init__()

    def options(self):
        pass

    def get(self):
        result = []
        organisations = registers.Organisation.objects(person_uri=request.oauth.user.person_uri)
        for organisation in organisations:
            result.append(organisation.to_dict())
        return result

    @oauth.require_oauth('organisation:add')
    def post(self):

        #this would be gov only, for a particular user
        self.parser.add_argument('type_uri', type=inputs.url, required=True, location='json', help="Must be a valid URI")
        self.parser.add_argument('name', required=True, location='json', help="An organisaiton must have a name")
        args = self.parser.parse_args()

        organisation = registers.Organisation()
        organisation.name = args['name']
        organisation.type_uri = args['type_uri']

        try:
            organisation.save()
        except ValidationError:
            return "Failed", 500
        return organisation.uri, 201


#routes
api.add_resource(About, '/about')
api.add_resource(Person, '/people/<string:_id>')
api.add_resource(PersonList, '/people')
api.add_resource(Licence, '/licences/<string:_id>')
api.add_resource(LicenceList, '/licences')
api.add_resource(OrganisationList, '/organisations')
