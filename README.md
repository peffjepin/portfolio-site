# portfolio-site

A simple portfolio website.

Self hosted using nginx, gunicorn, and MySQL. Ssl certificate from Let's Encrypt.

https://peffjepin.com


# The code

It's mostly just html, there is not much to mention. 

I did put a little extra work into the cli.py module. I have plans to write a python boilerplate generation project, and 
intend on using this project as a model for a flask-app.

Once you install this package into a virtual environment you will have the `sitectl` cli available.

The wsgi.py file has a docstring explaining how to quickly deploy a production app with the cli.

```sh
# deploy the app in development mode
sitectl deploy -d

# setup production logs (one time)
sudo sitectl setup

# deploy in production with gunicorn
# (this will exec the wsgi.py file in the cwd to create the wsgi application)
sitectl deploy -p --host 127.0.0.1 --port 5000 --other-options

# kill a production app running in the background
sitectl kill

# look at logs (using tail -f)
# default length is something like 25
sitectl logs access --length=100
sitectl logs error

# query contact messages from database
# this will prompt for db credentials
# I haven't generalized this command in any way, so its specificically targetting MySQL
sitectl query

# or provide them here
sitectl -db-addr mysite.com --db-user user --db-pass password query
# you will be prompted for any credentials that are not provided from the cli
sitectl -A mysite.com query

# the development deployment uses an in memory sqlite backend, though it could be told to use MySQL
sitectl -A mysql.address -U mysql.user deploy -d
```
