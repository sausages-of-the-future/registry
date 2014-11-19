import os
import glob
from datetime import datetime
import hashlib
from register import app
from mongoengine import StringField, PolygonField, DateTimeField, PointField, StringField, DictField, DynamicDocument, Document, ObjectIdField, BooleanField, URLField, ListField, ReferenceField
from mongoengine import signals
from mongoengine import DoesNotExist
import hashlib

avaliable_scopes = {'person:view': 'Permission to person ID and date of birth', 'personal_licence:view': 'View licences you hold', 'personal_licence:add': 'Issue a licence to you'}

class  RegisterBase(Document):
    meta = {'allow_inheritance': True}

    @property
    def uri(self):
        raise NotImplementedError

#Registers
class Person(RegisterBase):
    """
    A list of people and their dates of birth.
    """
    born_at = DateTimeField()

    @property
    def uri(self):
        return "%s/people/%s" % (app.config['BASE_URL'], str(self.id))

    def to_dict(self):
        return {'born_at': self.born_at.isoformat()}

class PersonalLicence(RegisterBase):
    """
    A list of licences that have been issued to people
    """
    person_uri = URLField(required=True)
    licence_type_uri = URLField(required=True)
    starts_at = DateTimeField(required=True)
    ends_at = DateTimeField(required=True)

    @property
    def uri(self):
        return "%s/personal-licence/%s" % (app.config['BASE_URL'], str(self.id))

    def to_dict(self):
        return {
                'uri': self.uri,
                'person_uri': self.person_uri,
                'licence_type_uri': self.licence_type_uri,
                'starts_at': self.starts_at.isoformat(),
                'ends_at': self.ends_at.isoformat()
                }

registry_classes = [Person, PersonalLicence, PersonalLicence]

