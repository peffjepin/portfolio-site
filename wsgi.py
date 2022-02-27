"""
this obviously is not a production ready application.
expecting the user to do the following server-side to prepare for production:

PREPARE THE ENVIRONMENT
    install flask app into venv
        cd /srv/mysite.com
        git clone https://github.com/me/this_repo
        python3 -m venv venv
        . venv/bin/activate
        python3 setup.py install

    one time setup (create log files with open rw permissions)
        (venv) sudo sitectl setup

    edit this file 
        you should initialize the repo with a live database
        you MUST define a wsgi app called "application" as shown below
        
    you're good to go. access sitectl cli from the venv


DEPLOYMENT
IMPORTANT: expecting deploy call to come from the directory containing
    this 'wsgi.py' file.
    (venv) sitectl deploy --production --host "127.0.0.1" --port 5000

KILL LIVE APP
    (venv) sitectl kill

PEEK AT LOGS
    (venv) sitectl logs access
    (venv) sitectl logs error

DEPLOY A NEW VERSION
    git pull ... (or whatever means of obtaining the up to date app)
    (venv) python3 setup.py install
    (venv) sitectl deploy -p

MORE
    (venv) sitectl --help
    (venv) logs --help
    (venv) deploy --help
    (venv) query --help
"""

from portfolio import app
from portfolio import repo


repo.init_debug()
application = app.create()

