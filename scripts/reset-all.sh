#!/bin/bash
source /vagrant/script/dev-env-functions
source ../environment.sh
create_virtual_env "registry"
python manage.py reset-all
deactivate
