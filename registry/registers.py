from registry import app
from voluptuous import Schema
from mongoengine import StringField, DateTimeField, DictField, PolygonField, PointField, Document, BooleanField, URLField

avaliable_scopes = {
    'person:view': 'Permission to person ID and date of birth',
    'licence:view': 'View licences you hold',
    'licence:add': 'Issue a licence to you',
    'organisation:add': 'Create an organisation'
    }

class  RegisterBase(Document):
    meta = {'allow_inheritance': True}
    _slug = ''

    type_uri = URLField(required=True)

    @property
    def uri(self):
        return "%s/%s/%s" % (app.config['BASE_URL'], self._slug, str(self.id))

    def to_dict(self):
        raise NotImplementedError

#Registers
class Person(RegisterBase):
    """
    A list of people and their dates of birth
    """
    _slug = 'people'
    born_at = DateTimeField()

    def to_dict(self):
        return {'born_at': self.born_at.isoformat()}

class Organisation(RegisterBase):
    """
    A list of organsiations (companies, charities, trade unions, political parties)
    """
    name = StringField(required=True)
    created_at = DateTimeField()

    def to_dict(self):
        return {'name': self.name,
                'created_at': self.born_at.isoformat()
               }

class Notice(RegisterBase):
    """
    A list of notices (jobs, apprenticeships, product recalls, medical recalls, tenders, parking suspensions)
    """
    title = StringField(required=True)
    detail = StringField(required=True)
    created_at = DateTimeField(required=True)
    expires_at = DateTimeField()

    def to_dict(self):
        return {'name': self.name,
                'created_at': self.born_at.isoformat()
               }

class Address(RegisterBase):
    """
    A list of places
    """
    address = StringField(required=True)
    lat_lng = PointField(required=True)

class Area(RegisterBase):
    """
    A list of administrative and legal areas (land use, constituencies, police areas, conservation areas, property boundries)
    """
    polygon = PolygonField(required=True)

class Amenity(RegisterBase):
    """
    A list of facilities (schools, hospitals, libraries, fishing locations)
    """
    name = StringField(required=True)
    description = StringField(required=True)
    address_uri = URLField()
    opening_times = DictField()

    def to_dict(self):
        return {'name': self.name,
                'created_at': self.born_at.isoformat()
               }

class Licence(RegisterBase):
    """
    A list of licences that have been issued to people and organisations
    """
    person_uri = URLField(required=True)
    starts_at = DateTimeField(required=True)
    ends_at = DateTimeField(required=True)

    def to_dict(self):
        return {
                'uri': self.uri,
                'person_uri': self.person_uri,
                'type_uri': self.type_uri,
                'starts_at': self.starts_at.isoformat(),
                'ends_at': self.ends_at.isoformat()
                }

registry_classes = [Person, Licence, Organisation, Notice, Amenity, Address, Area]

