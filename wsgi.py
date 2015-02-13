#!/usr/bin/env python

import sys, traceback, logging, json, httplib2, urllib

import bottle as bt
import oauth_config as auth

from google.appengine.ext import ndb
from google.appengine.api import users

## Setup & Config
##
import config
bt.TEMPLATE_PATH.append('./static/')

# Set the log level high so that all is logged/
#
logger = logging.getLogger('wsgi')
logger.setLevel(logging.DEBUG)

sfdcAuth = ''
headers = ''
h = httplib2.Http()
queryURI = ''
	
def application(environ, start_response):
  return bt.default_app().wsgi(environ,start_response)
	
@bt.hook('after_request')
def enable_cors():
  bt.response.headers['Access-Control-Allow-Origin'] = '*'


# Salesforce OAuth Login. 
#
@bt.route("/") 
def index():
  try:
    retVal = 'index : '
    
    loginURL = auth.LOGIN_URI
    loginArgs = {'response_type' : 'code', 'client_id' : auth.CLIENT_ID, 'redirect_uri' : auth.REDIRECT_URI}
    loginURL += 'services/oauth2/authorize?'+urllib.urlencode(loginArgs)
    
    retVal += loginURL
    
    return ('<html><body> <h1>%s</h1><a href="%s">login</a></body></html>' % (retVal, loginURL))
  
  except:
    logger.warning(traceback.print_exc())
    return('<html><head><meta HTTP-EQUIV="REFRESH" content="0; url=/html/Error.html"></head></html>')
    raise

# Salesforce Auto
#
@bt.route("/autoLogin")
def sfdcLogin():
  try:
    return('<html><head><meta HTTP-EQUIV="REFRESH" content="0; url=html/SalesForce_Login_II.html"></head></html>')
  except:
    logger.warning(traceback.print_exc())
    return('<html><head><meta HTTP-EQUIV="REFRESH" content="0; url=/html/Error.html"></head></html>')
    raise		
		
# Salesforce Canvas URL
#		
@bt.route("/SalesforceOAuth")
def SalesforceLogin():
  try:
    retVal = 'SalesforceOAuth : '
    
    args = bt.request.query_string
    loginURL = bt.request.query['loginUrl']
    body = bt.request.body.readline()
    
    loginArgs = {'response_type' : 'code', 'client_id' : auth.CLIENT_ID, 'redirect_uri' : auth.REDIRECT_URI}
    loginURL += 'services/oauth2/authorize?'+urllib.urlencode(loginArgs)
    
    retVal += loginURL
    
    return ('<html><body> <h1>%s</h1><a href="%s">login</a></body></html>' % (retVal, loginURL))
  
  except:
    logger.warning(traceback.print_exc())
    return('<html><head><meta HTTP-EQUIV="REFRESH" content="0; url=/html/Error.html"></head></html>')
    raise

# Callback OAuth
#		
@bt.route("/Callback")
def SalesforceLogin():
  try:
    
    args = bt.request.url
    code = bt.request.query['code']
    code = urllib.unquote(code)
    loginArgs = {'grant_type' : 'authorization_code',
                 'client_id' : auth.CLIENT_ID,
                 'client_secret' :  auth.CLIENT_SECRET,
                 'redirect_uri' : auth.REDIRECT_URI,
                 'code' : code}
    
    loginURL = auth.LOGIN_URI+'services/oauth2/token'
    
    resp, content = h.request(loginURL, "POST", urllib.urlencode(loginArgs))
    logger.warning(resp)
    logger.warning(content)
    
    if resp['status'] == '200':
      contentObj = json.loads(content)
      logger.warning(contentObj)
      
      auth.ACCESS_TOKEN = contentObj['access_token']
      auth.INSTANCE_URL = contentObj['instance_url']
      auth.ISSUED_AT = contentObj['issued_at']
      
      # Build the HTTP header
      #
      global sfdcAuth
      sfdcAuth = "OAuth " + auth.ACCESS_TOKEN
      global headers
      headers = {'Authorization': sfdcAuth,
					  'X-PrettyPrint': '1',
                 'Content-Type': 'application/json'}
      apiURI = auth.INSTANCE_URL+'/services/data/'
      
      # A raw request to the URI gets a list of the API version available.
      #
      resp, content = h.request(apiURI, method="GET", headers=headers)
      logger.warning(resp)
      logger.warning(content)
      
      # The response is 'application/json' we need to change it into a Python Object
      #
      pyObj = json.loads(content)

      # Assume the last entry is the most resent version and get the URI path.
      #
      URI = auth.INSTANCE_URL + pyObj[-1]['url']
    
      # Hit the version URI for a list of the resources avilable. We want to 'query'
      #
      resp, content = h.request(URI, method="GET", headers=headers)
      logger.warning(resp)
      logger.warning(content)
    
      pyObj = json.loads(content)
      global queryURI
      queryURI = auth.INSTANCE_URL + pyObj['query']

      
    return('<html><head><meta HTTP-EQUIV="REFRESH" content="0; url=/sfdcQuery"></head></html>')
  
  except:
    logger.warning(traceback.print_exc())
    return('<html><head><meta HTTP-EQUIV="REFRESH" content="0; url=/html/Error.html"></head></html>')
    raise

		
# Do some SFDC stuff
#
@bt.route("/sfdcQuery")
def sfdcQuery():
  try:
    retVal = '<!DOCTYPE html><html><body>'
    retVal += '<b>Instance URL : </b>' + auth.INSTANCE_URL + '<br><br>'
    
    # Construct the query to append to the queryURI
    #
    if 'queryStr' in bt.request.query:
      queryStr = bt.request.query['queryStr']
    else:
      queryStr = "SELECT Id, Name FROM Account LIMIT 5"
    query = urllib.urlencode({'q':queryStr})
    URI = queryURI+"?"+query
    resp, content = h.request(URI, method="GET", headers=headers)
    logger.warning(resp)
    logger.warning(content)
    
    retVal += '<form name="sfdcQuery" action="sfdcQuery" method="get"><table>'
    retVal += '<tr><td><textarea rows="3" cols="80" name="queryStr">' + queryStr + '</textarea></td></tr>'
    retVal += '<tr><td><input type="submit" value="Submit"></td></tr>'
    retVal += '<tr><td><textarea rows="30" cols="80">' +content+ '</textarea></td></tr>'
    retVal += '</table></form>'
    retVal += '</body></html>'
    
    return(retVal)
  
  except:
    logger.warning(traceback.print_exc())
    return('<html><head><meta HTTP-EQUIV="REFRESH" content="0; url=/html/Error.html"></head></html>')
    raise

if __name__ == "__main__":
  bt.run(server="gae", debug=True)
