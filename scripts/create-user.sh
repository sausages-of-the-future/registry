#!/bin/bash
source /vagrant/script/dev-env-functions
source ../environment.sh
workon "registry"
python manage.py create-user
deactivate
