#!/bin/bash
source /vagrant/script/dev-env-functions
source ../environment.sh
init_virtual_env "registry"
python manage.py register-service
deactivate
