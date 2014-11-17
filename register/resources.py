import json
import glob
import os
import imp
import re
import inspect
from flask import make_response, request
from flask.ext.restful import reqparse, abort, Api, Resource, inputs
from mongoengine import DoesNotExist, ValidationError
from register import api, models, app, oauth
from flask_restful.utils import cors

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
    def get(oauth, self):
        return {'person': oauth.user.person_uri}

class Person(Resource):

    def options(self):
        pass

    def put(self):
        return "Forbidden", 403

    def delete(self):
        return "Forbidden", 403

    @oauth.require_oauth('person:view')
    def get(oauth, self, _id):
        person = mongo_get_or_abort(_id, models.Person)
        if person.uri == oauth.user.person_uri:
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

class PersonalLicence(Resource):

    def options(self):
        pass

    @oauth.require_oauth()
    def get(oauth, self, _id):
        valid_view_scope, req = oauth.verify_request(['personal_licence:view'])
        if valid_view_scope:
            personal_licence = mongo_get_or_abort(_id, models.PersonalLicence).to_dict()
            #if belongs to use token, then we can return more info
            if persoanl_licence.person_uri == oauth.user.person_uri:
                return personal_licence.to_dict()
            else:
                return responal_licence.to_dict()
        else:
            return mongo_get_or_abort(_id, models.PersonalLicence).to_dict()


class PersonalLicenceList(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        super(PersonalLicenceList, self).__init__()

    def options(self):
        pass

    @oauth.require_oauth('personal_licence:view')
    def get(oauth, self):
        result = []
        personal_licences = models.PersonalLicence.objects(person_uri=oauth.user.person_uri)
        for personal_licence in personal_licences:
            result.append(personal_licence.to_dict())
        print json.dumps(result)
        return result

    @oauth.require_oauth('personal_licence:add')
    def post(oauth, self):

        #this would be gov only, for a particular user
        self.parser.add_argument('licence_type_uri', type=inputs.url, required=True, location='json', help="Must be a valid URI")
        self.parser.add_argument('starts_at', type=inputs.date, required=True, location='json', help="Must be a valid date eg ISO 2013-01-01")
        self.parser.add_argument('ends_at', type=inputs.date, required=True, location='json', help="Must be a valid date eg ISO 2013-01-01")
        args = self.parser.parse_args()

        personal_licence = models.PersonalLicence()
        personal_licence.person_uri = oauth.user.person_uri
        personal_licence.licence_type_uri = args['licence_type_uri']
        personal_licence.starts_at = args['starts_at']
        personal_licence.ends_at = args['ends_at']

        try:
            personal_licence.save()
        except ValidationError, e:
            return "Failed", 500
        return personal_licence.uri, 201

#routes
api.add_resource(About, '/about')
api.add_resource(PersonList, '/people')
api.add_resource(Person, '/people/<string:_id>')
api.add_resource(PersonalLicenceList, '/personal-licences')
api.add_resource(PersonalLicence, '/personal-licences/<string:_id>')
