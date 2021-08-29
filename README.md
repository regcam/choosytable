# Choosy Table

## Purpose:
Choosy Table is where People of Color share and analyze their corporate & interviews experiences.  This app provides the statistical chances a PoC receives an offer for a particular role.  Before we lend our talents to any company, we should know how they treat us.  

## Tech Stack:
Backend/Frontend - Flask (Python3)

Persistent Storage - MongoDB 

WSGI Server - Gunicorn

Caching - Memcached

## Requirements:
* [Homebrew](https://docs.brew.sh/Installation)

* Python 3: `brew install python`

* [Google API](console.developers.google.com/)

* [MongoDB](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-os-x/)

* Gunicorn: `brew install gunicorn`

* Install Python dependencies (at root of the repo): `pip3 install -r requirements.txt`

## Getting Started:
1. Export the following required variables to your environment:

    * SECRET_KEY - Needed to keep the Flask client-side sessions secure 

    #### The following variables are set from configuring OAuth via [Google APIs](https://support.google.com/googleapi/answer/6158857?hl=en&ref_topic=7013279):
    * GOOGLE_OAUTH_CLIENT_ID - Client ID generated from your OAuth credentials

    * GOOGLE_OAUTH_CLIENT_SECRET - Client Secret generated fromyoru OAuth credentials

    #### The following variables come from configuring your MongoDB instance:
    * MONGO_DBNAME - Name of mongo database

    * MONGO_URI - URI to your mongodb instance

    * OAUTHLIB_INSECURE_TRANSPORT - Normally, OAuthLib will raise an InsecureTransportError if you attempt to use OAuth2 over HTTP, rather than HTTPS. Setting this environment variable will prevent this error from being raised. This is mostly useful for local testing, or automated tests. ***Never set this variable in production.***

    * OAUTHLIB_RELAX_TOKEN_SCOPE - Accounts for Google changing the requested OAuth scopes on you

2. Then start the app locally:
`gunicorn -w 1 --bind 127.0.0.1:8080 app:app`

## TODO
*Data Structure*
