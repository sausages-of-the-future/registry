**Set up users and services in this application**

Users / people:

To create a user (also creates a person) run:

```
scripts/create-user.sh
```

Registering a service:

```
scripts/register-service-sh
```

**Deploy to heroku**

Make sure you have [installed the heroku toolbelt](https://toolbelt.heroku.com/)

*Note if you add anthing to environment.sh or environment_private.sh then add those config items to the heroku app as well*

For example
```
heroku config:set SETTINGS='config.Config'

```

If you make changes, push to github first and then push to heroku master

To set up heroku master as a remote :

```
heroku git:remote -a registry-gov
```

The you can:

```
git push heroku master
```

But again, please make sure your changes are in github master first. Then all will be synced up nicely
