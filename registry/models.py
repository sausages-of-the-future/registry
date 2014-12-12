import json
import os
import hashlib
import requests
import uuid

from schematics.models import Model
from schematics.types.serializable import serializable
from schematics.transforms import blacklist

from schematics.types import (
    StringType,
    DateTimeType,
    BaseType,
    FloatType,
    DateType,
    URLType,
    UUIDType
)

from schematics.types.compound import (
     ModelType,
     ListType
)

class MongoBodgeType(BaseType):
    def to_native(self, value):
        return str(value)

headers = {'content-type': 'application/json'}

def uid(key=None):
    "Create uid for a key"
    if (key == None):
        key = os.urandom(32).encode('hex')
    u = hashlib.sha256()
    u.update(key.encode('utf-8'))
    return u.hexdigest()

# class Fields(Model):

#     class Options:
#         serialize_when_none=False

#     salt = StringType()
#     name = StringType()
#     urn = StringType()
#     type = StringType()
#     sameAs = StringType()
#     location = StringType()
#     streetAddress = StringType()
#     addressLocality = StringType()
#     addressRegion = StringType()
#     postalCode = StringType()
#     addressCountry = StringType()
#     longitude = FloatType()
#     latitude = FloatType()
#     easting = StringType()
#     northing = StringType()
#     ngr = StringType()
#     instrument = StringType()
#     startTime = StringType()
#     value = StringType()
#     unitCode = StringType()
#     telephone = StringType()
#     email = StringType()
#     honorificPrefix = StringType()
#     head = StringType()
#     foundedDate = DateTimeType()
#     dissolutionDate = DateTimeType()
#     birthDate = DateType()


class ThingModel(Model):

    class Options:
        serialize_when_none=False

    uid = StringType()
    _id = MongoBodgeType()
    type = StringType(required=True)
    tags = ListType(StringType(), required=False)
    # fields = ModelType(Fields)

    # set these after construction?
    created = DateTimeType()
    previousVersion = StringType()
    signature = StringType()


from flask import current_app

class LicenseFields(Model):

    class Options:
        roles = {'public': blacklist('id')}

    issuedFor = StringType(required=True)
    validFrom = DateType(required=True)
    validUntil = DateType(required=True)


class LicenceModel(ThingModel):
    """
    A licence that has been issued to a person or an organisation
    """
    class Options:
        serialize_when_none=False
        namespace = "http://things.gov.local/things" # get from config

    fields = ModelType(LicenseFields)

    def save(self):
        try:
            r = requests.post(self.Options.namespace, data=json.dumps(self.to_primitive()), headers=headers)
            from flask import current_app
            current_app.logger.info("RETURNED DATA = %s" % r.json())
        except Exception as e:
            current_app.logger.info(e)

    @classmethod
    def find_by_user(cls, user_id):
        url = '%s/Licence?issuedFor=%s' % (cls.Options.namespace, user_id)
        r = requests.get(url, headers=headers)
        return r.json()

    @classmethod
    def find_by_id(cls, _id):
        url = '%s/licence/%s.json' % (cls.Options.namespace, _id)
        r = requests.get(url, headers=headers)
        from flask import current_app
        current_app.logger.info("RETURNED DATA = %s" % r.json())
        return r.json()
