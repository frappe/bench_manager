import json

import requests

import frappe
from bench_manager.bench_manager.doctype.site.site import create_site
from frappe import _
from frappe.utils import get_datetime, get_datetime_str

AUTH_SERVER_BASE_URL = frappe.local.conf.get("auth_server_url")
DECAF_SERVER_BASE_URL = frappe.local.conf.get("decaf_server_url")
LOGIN_AUTHORIZE_ENDPOINT = frappe.local.conf.get("login_authorize_endpoint")
LOGIN_TOKEN_ENDPOINT = frappe.local.conf.get("login_token_endpoint")
LOGIN_API_ENDPOINT = frappe.local.conf.get("login_api_endpoint")
LOGIN_REDIRECT_URI = "/api/method/frappe.integrations.oauth2_logins.custom/bloomstack"
DECAF_AUTHORIZE_ENDPOINT = "/api/method/frappe.integrations.oauth2.authorize"
DECAF_TOKEN_ENDPOINT = "/api/method/frappe.integrations.oauth2.get_token"
DECAF_PROFILE_ENDPOINT = "/api/method/frappe.integrations.oauth2.openid_profile"
DECAF_REVOKATION_ENDPOINT = "/api/method/frappe.integrations.oauth2.revoke_token"


class AuthClientRegistrationError(frappe.ValidationError): pass
class DecafClientRegistrationError(frappe.ValidationError): pass
class SiteAlreadyExistsError(frappe.ValidationError): pass


@frappe.whitelist(allow_guest=True)
def setup_instance(company, token, site_url):
	"""
	While setting up a new Bloomstack instance, setup Bloomstack
	login integrations and an OAuth client for the company.

	Args:
		company (string): Name of the company
		token (string): A valid access token for creating the instance
		site_url (string): The base site URL for the instance to be created
	"""

	# TODO: setup client secret in bench manager
	# validate_secret(frappe.local.request.get('x-manager-secret'))

	validate_site_url(site_url)

	# TODO: get newly created site to setup SSO and OAuth Client on
	auth_client_info = register_auth_client(company, token, site_url)
	setup_social_login_keys(site_url, auth_client_info)

	oauth_client_info = setup_oauth_client(company)
	register_decaf_client(company, token, site_url, oauth_client_info)


def validate_site_url(site_url):
	"""
	Check if a site with the given URL is already instantiated.
	"""

	sites = frappe.get_all("Site", fields=["site_name"])

	if any([site.site_name in site_url for site in sites]):
		frappe.throw(_("An instance with that name already exists. Please use a different name."),
			exc=SiteAlreadyExistsError)
	else:
		create_site(
			site_name=site_url,
			install_erpnext=True,
			# TODO: get mariadb pass securely
			mysql_password="",
			admin_password=frappe.conf.get("admin_password"),
			key=get_datetime_str(get_datetime())
		)


def register_auth_client(company, token, site_url):
	"""
	Register the new site as a client on the specified authorization server.

	Returns:
		dict: Response object from the registration
	"""

	redirect_uris = [site_url + LOGIN_REDIRECT_URI]
	scopes = ["openid", "roles", "email", "profile"]

	url = AUTH_SERVER_BASE_URL + "/client/v1/create"
	headers = {
		'Authorization': 'Bearer {access_token}'.format(access_token=token),
		'Content-Type': 'application/json'
	}
	data = {
		"name": company,
		"isTrusted": "0",
		"autoApprove": True,
		"redirectUris": redirect_uris,
		"allowedScopes": scopes,
		"authenticationMethod": "PUBLIC_CLIENT"
	}

	response = requests.post(url, headers=headers, data=json.dumps(data))

	if not response.ok:
		frappe.throw(_("There was a server error while trying to register the site"), exc=AuthClientRegistrationError)

	client_info = response.json()
	return client_info


def setup_social_login_keys(site_url, client_info):
	"""
	On successful client registration, generate two Social Login Keys:
		- Bloomstack: enabled by default, primary login method
		- Frappe: disabled by default, backup login method
	"""

	# create a login key for Bloomstack, enabled by default
	scopes = " ".join(client_info.get("allowedScopes"))
	response_type = "code"
	auth_url_data = json.dumps(dict(scope=scopes, response_type=response_type))

	bloomstack_social_login_key = frappe.new_doc("Social Login Key")
	bloomstack_social_login_key.update({
		"enable_social_login": True,
		"provider_name": "Bloomstack",
		"client_id": client_info.get("clientId"),
		"client_secret": client_info.get("clientSecret"),
		"base_url": AUTH_SERVER_BASE_URL,
		"authorize_url": LOGIN_AUTHORIZE_ENDPOINT,
		"redirect_url": LOGIN_REDIRECT_URI,
		"access_token_url": LOGIN_TOKEN_ENDPOINT,
		"api_endpoint": LOGIN_API_ENDPOINT,
		"auth_url_data": auth_url_data
	})
	bloomstack_social_login_key.insert()

	# create a login key for Frappe, disabled by default
	frappe_social_login_key = frappe.new_doc("Social Login Key")
	frappe_social_login_key.get_social_login_provider("Frappe", initialize=True)
	frappe_social_login_key.enable_social_login = False
	frappe_social_login_key.custom_base_url = False
	frappe_social_login_key.base_url = site_url
	frappe_social_login_key.insert()


def setup_oauth_client(company):
	"""
	Create an OAuth client on the instance to interface with middleware Frappe server.

	Returns:
		object: OAuth Client instance
	"""

	oauth_client = frappe.new_doc("OAuth Client")
	oauth_client.update({
		"app_name": company,
		"skip_authorization": True,
		"scopes": "all openid",
		"redirect_uris": DECAF_SERVER_BASE_URL + "/frappe/callback",
		"default_redirect_uri": DECAF_SERVER_BASE_URL + "/frappe/callback"
	})
	oauth_client.insert()
	return oauth_client


def register_decaf_client(company, token, site_url, client_info):
	"""
	Register the instance's OAuth Client with the middleware Frappe server.
	"""

	url = DECAF_SERVER_BASE_URL + "/frappe/v1/connect_client"
	headers = {
		'Authorization': 'Bearer {access_token}'.format(access_token=token),
		'Content-Type': 'application/json'
	}
	data = {
		"name": company,
		"clientId": client_info.client_id,
		"clientSecret": client_info.client_secret,
		"authServerURL": site_url,
		"profileURL": site_url + DECAF_PROFILE_ENDPOINT,
		"tokenURL": site_url + DECAF_TOKEN_ENDPOINT,
		"authorizationURL": site_url + DECAF_AUTHORIZE_ENDPOINT,
		"revocationURL": site_url + DECAF_REVOKATION_ENDPOINT,
		"scope": client_info.scopes.split(" ")
	}

	response = requests.post(url, headers=headers, data=json.dumps(data))

	if not response.ok:
		frappe.throw(_("There was a server error while trying to create the site"), exc=DecafClientRegistrationError)
