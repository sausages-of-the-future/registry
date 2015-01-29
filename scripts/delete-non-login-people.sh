#!/bin/bash
source /vagrant/script/dev-env-functions
source_app_environment "registry"
init_virtual_env "registry"
python manage.py delete-non-login-people
deactivate
