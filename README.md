# Choosy Table

## Purpose:
Choosy Table is were People of Color can share and view their hiring and corporate experiences.  Before we lend our talents to any company we should know how they treat us during and after the interview process.  This app will empower POC to engage businesses whom value our collaboration and community.

## Tech Stack:
Backend/Frontend - Python3/Flask

Persistent Storage - MongoDB 

## Requirements:
Google APIs account

MongoDB Compass

Execute `pip3 install -r requirements.txt`

## Getting Started:
Export the following required variables to your environment:

* SECRET_KEY - Needed to keep the Flask client-side sessions secure 

* #### The following variables are set from configuring OAuth via [Google APIs](https://support.google.com/googleapi/answer/6158857?hl=en&ref_topic=7013279):
* GOOGLE_OAUTH_CLIENT_ID - Client ID generated from your OAuth credentials

* GOOGLE_OAUTH_CLIENT_SECRET - Client Secret generated fromyoru OAuth credentials

#### The following variables come from configuring your MongoDB instance:
MONGO_DBNAME - Name of mongo database

MONGO_URI - URI to your mongodb instance

OAUTHLIB_INSECURE_TRANSPORT - Normally, OAuthLib will raise an InsecureTransportError if you attempt to use OAuth2 over HTTP, rather than HTTPS. Setting this environment variable will prevent this error from being raised. This is mostly useful for local testing, or automated tests. ***Never set this variable in production.***

OAUTHLIB_RELAX_TOKEN_SCOPE - Accounts for Google changing the requested OAuth scopes on you

Then start the app:
`/usr/bin/python3 /PATH/TO/YOUR/mongo.py`