from registry import app
from voluptuous import Schema
from mongoengine import (
    StringField,
    DateTimeField,
    DictField,
    PolygonField,
    ListField,
    PointField,
    Document,
    BooleanField,
    URLField,
    BooleanField
)

avaliable_scopes = {
    'person:view': 'View your full name and check your age',
    'licence:view': 'View licences you hold',
    'licence:add': 'Issue a licence to you',
    'vehicle:view': 'View details of cars and other vehicles registered to you',
    'address:view': 'View your current address',
    'income:view': 'View your PAYE income',
    'visa:view': 'View visas you hold',
    'visa:add': 'Issue a visa to you',
    'notice:add': 'Issue a notice',
    'organisation:add': 'Create an organisation',
    'bankruptcy:check': 'Check your details against the Bankruptcy Register',
    'insolvency:check': 'Check your details against the Insolvency Register',
    'dataprotection:add': 'Add your organsisation to the Data Protection Register',
    'employers:add': 'Add your organsisation to the Register of Employers',
    'tax:add': 'Register for taxes',
    }

class  RegisterBase(Document):
    meta = {'allow_inheritance': True}
    _slug = 'register_base'

    type_uri = URLField()

    @property
    def uri(self):
        return "%s/%s/%s" % (app.config['BASE_URL'], self._slug, str(self.id))

    def to_dict(self):
        return {'slug' : self._slug}

#Registers
class Person(RegisterBase):
    """
    A list of people and their dates of birth
    """
    _slug = 'people'
    born_at = DateTimeField()
    full_name = StringField()

    def to_dict(self):
        return {'born_at': self.born_at.isoformat(), 'full_name': self.full_name}

class Visa(RegisterBase):
    """
    A list of visas issued to people
    """
    _slug = 'visas'
    issued_at = DateTimeField()
    expires_at = DateTimeField()
    person_uri = URLField(required=True)
    visa_type = StringField()
    passport_number = StringField()

    def to_dict(self):
        return {
            'slug': self._slug,
            'uri': self.uri,
            'issued_at': self.issued_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'person_uri': self.person_uri,
            'visa_type': self.visa_type,
            'passport_number': self.passport_number
        }

class Organisation(RegisterBase):
    """
    A list of organsiations (companies, charities, trade unions, political parties)
    """
    _slug = 'organisations'
    name = StringField(required=True)
    organisation_type = StringField(required=True)
    activities = StringField()
    created_at = DateTimeField()
    directors = ListField()
    register_data = URLField()
    register_employer = URLField()
    register_construction = BooleanField()
    full_address = StringField()

    def to_dict(self):
        return {
                'uri': self.uri,
                'slug': self._slug,
                'name': self.name,
                'activities': self.activities,
                'organisation_type': self.organisation_type,
                'directors' : self.directors,
                'register_data' : self.register_data,
                'register_employer' : self.register_employer,
                'register_construction' : self.register_construction,
                'full_address': self.full_address
                }

class Notice(RegisterBase):
    """
    A list of notices (jobs, apprenticeships, product recalls, medical recalls, tenders, parking suspensions, licencing applications)
    """
    _slug = 'notices'

    title = StringField(required=True)
    detail = StringField(required=True)
    created_at = DateTimeField(required=True)
    expires_at = DateTimeField()
    issued_by_uri = URLField(required=True)
    subject_uri = URLField(required=True)
    subject_name = StringField(required=True)

    #TODO set expiry date

    def to_dict(self):
        return {
                'uri': self.uri,
                'slug': self._slug,
                'title': self.title,
                'detail': self.detail,
                'created_at': self.created_at.isoformat(),
                'issued_by_uri': self.issued_by_uri,
                'subject_uri': self.subject_uri,
                'subject_name': self.subject_name
        }

class List(RegisterBase):
    """
    Official lists
    """
    _slug = 'lists'
    name = StringField(required=True)
    list_data = ListField(DictField())

    def to_dict(self):
        return {'uri': self.uri, 'name': self.name, 'list_data': self.list_data, 'slug': self._slug}

class Address(RegisterBase):
    """
    A list of places
    """
    _slug = 'addresses'
    address = StringField(required=True)
    lat_lng = PointField(required=True)

    def to_dict(self):
        return {
                'uri': self.uri,
                'address': self.address,
                'lat_lng': self.lat_lng
                }

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
    _slug = 'licences'
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

class DataProtection(RegisterBase):
    """
    A list of organisation that collects and holds data about individuals
    """
    _slug = 'dataprotection'

    organisation_uri = URLField(required=True)
    registration_date = DateTimeField(required=True)

    def to_dict(self):
        return {
                'slug': self._slug,
                'uri': self.uri,
                'organisation_uri': self.organisation_uri,
                'type_uri': self.type_uri,
                'registration_date': self.registration_date.isoformat(),
        }

class Employer(RegisterBase):
    """
    A list of employers registered with HMRC
    """
    _slug = 'employers'

    organisation_uri = URLField(required=True)
    registration_date = DateTimeField(required=True)

    def to_dict(self):
        return {
                'uri': self.uri,
                'organisation_uri': self.organisation_uri,
                'type_uri': self.type_uri,
                'registration_date': self.registration_date.isoformat(),
        }

registry_classes = [Person, Licence, List, Organisation, Notice, Amenity, Address, Area, DataProtection, Employer, Visa, Address]
