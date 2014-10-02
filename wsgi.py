#!/usr/bin/env python

import sys, traceback, logging, json, httplib2, urllib

import bottle as bt
import oauth_config as auth

from google.appengine.ext import ndb
from google.appengine.api import users

# Set the log level high so that all is logged/
#
logging.basicConfig(level=logging.DEBUG)

# A basic Google datastore object. After running the app 
# open the SDK console -> Datastore Viewer. 
#	
class Visitor(ndb.Model):
	name = ndb.StringProperty()
	createdDT = ndb.DateTimeProperty(auto_now_add=True)
	lastVisitDT = ndb.DateTimeProperty(auto_now=True)
	email = ndb.StringProperty()

	
def application(environ, start_response):
	return bt.default_app().wsgi(environ,start_response)
	
@bt.hook('after_request')
def enable_cors():
	bt.response.headers['Access-Control-Allow-Origin'] = '*'


# The site's home page. 
#
@bt.route("/") 
def index():
	try:
		retVal = 'index : '

		loginURL = auth.LOGIN_URI
		
		loginArgs = {'response_type' : 'code',
					 'client_id' : auth.CLIENT_ID,
					 'redirect_uri' : auth.REDIRECT_URI}
		
		loginURL += 'services/oauth2/authorize?'+urllib.urlencode(loginArgs)
		
		retVal += loginURL
		
		return ('<html><body> <h1>%s</h1><a href="%s">login</a></body></html>' 
					% (retVal, loginURL))

	except:
		logging.warning(traceback.print_exc())
		return('<html><head><meta HTTP-EQUIV="REFRESH" content="0; url=/html/Error.html"></head></html>')
		raise
		
# Salesforce OAuth
#		
@bt.route("/SalesforceOAuth")
def SalesforceLogin():
	try:
		retVal = 'SalesforceOAuth : '
		
		args = bt.request.query_string
		loginURL = bt.request.query['loginUrl']
		body = bt.request.body.readline()
		
		loginArgs = {'response_type' : 'code',
					 'client_id' : auth.CLIENT_ID,
					 'redirect_uri' : auth.REDIRECT_URI}
		
		loginURL += 'services/oauth2/authorize?'+urllib.urlencode(loginArgs)
		
		retVal += loginURL
		
		return ('<html><body> <h1>%s</h1><a href="%s">login</a></body></html>' 
					% (retVal, loginURL))

	except:
		logging.warning(traceback.print_exc())
		return('<html><head><meta HTTP-EQUIV="REFRESH" content="0; url=/html/Error.html"></head></html>')
		raise

# Callback OAuth
#		
@bt.route("/Callback")
def SalesforceLogin():
	try:
		retVal = 'Callback : <br>'
		
		args = bt.request.url
		code = bt.request.query['code']
		code = urllib.unquote(code)
		loginArgs = {'grant_type' : 'authorization_code',
					 'client_id' : auth.CLIENT_ID,
					 'client_secret' :  auth.CLIENT_SECRET,
					 'redirect_uri' : auth.REDIRECT_URI,
					 'code' : code}
		
		loginURL = auth.LOGIN_URI+'services/oauth2/token'
			
		h = httplib2.Http()
			
		resp, content = h.request(loginURL, "POST", urllib.urlencode(loginArgs))
		logging.warning(resp)
		logging.warning(content)
		
		if resp['status'] == '200':
			contentObj = json.loads(content)
			logging.warning(contentObj)

			auth.ACCESS_TOKEN = contentObj['access_token']
			auth.INSTANCE_URL = contentObj['instance_url']
			auth.ISSUED_AT = contentObj['issued_at']

			retVal += 'ID           : ' + contentObj['id'] + '<br>'
						
		return('<html><head><meta HTTP-EQUIV="REFRESH" content="0; url=/sfdcQuery"></head></html>')

	except:
		logging.warning(traceback.print_exc())
		return('<html><head><meta HTTP-EQUIV="REFRESH" content="0; url=/html/Error.html"></head></html>')
		raise

		
# Do some SFDC stuff
#
@bt.route("/sfdcQuery")
def sfdcQuery():
	try:
		retVal = '<!DOCTYPE html><html><body><h1>OAuth : </h1>'
		retVal += '<b>Instance URL : </b>' + auth.INSTANCE_URL + '<br><br>'

		h = httplib2.Http()
		# Build the HTTP header
		#
		sfdcAuth = "OAuth " + auth.ACCESS_TOKEN
		headers = {'Authorization': sfdcAuth, 
				   'X-PrettyPrint': '1',
				   'Content-Type': 'application/json'}
				   
		apiURI = auth.INSTANCE_URL+'/services/data/'
		
		resp, content = h.request(apiURI, method="GET", headers=headers)
		logging.warning(resp)
		logging.warning(content)
		
		pyObj = json.loads(content)
		URI = auth.INSTANCE_URL + pyObj[-1]['url']
		resp, content = h.request(URI, method="GET", headers=headers)
		logging.warning(resp)
		logging.warning(content)

		pyObj = json.loads(content)
		URI = auth.INSTANCE_URL + pyObj['query']
		query = urllib.urlencode({"q":"SELECT Id, Name, SFDC_Account_ID__c FROM Account LIMIT 5"})
		URI += "?"+query
		resp, content = h.request(URI, method="GET", headers=headers)
		logging.warning(resp)
		logging.warning(content)
		
		retVal += '<b>' + URI + '</b><br>'
		retVal += '<textarea rows="30" cols="80">' +content+ '</textarea>'
		
		retVal += '</body></html>'
		return(retVal)
	except:
		logging.warning(traceback.print_exc())
		return('<html><head><meta HTTP-EQUIV="REFRESH" content="0; url=/html/Error.html"></head></html>')
		raise

		
if __name__ == "__main__":
	bt.run(server="gae", debug=True)