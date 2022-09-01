# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappe and contributors
# For license information, please see license.txt

import json
import os
import shlex
import sys
from subprocess import PIPE, Popen, check_output
from datetime import datetime,timedelta
import traceback
import frappe
import frappe
import shlex
import re
from subprocess import PIPE, STDOUT, Popen
from bench_manager.bench_manager.utils import _close_the_doc
from bench_manager.bench_manager.utils import safe_decode
from urllib.parse import parse_qs, urlparse

import frappe
from bench_manager.bench_manager.utils import (
	safe_decode,
	verify_whitelisted_call,
)
from frappe.model.document import Document
import json
import os
import dropbox
from rq.timeouts import JobTimeoutException

import frappe
from frappe import _
from frappe.integrations.offsite_backup_utils import (
	get_chunk_site,
	send_email,
	validate_file_size,
)
from frappe.integrations.utils import make_post_request
from frappe.model.document import Document
from frappe.utils import (
	cint,
	encode,
	get_url,
	get_request_site_address,
)
from frappe.utils.background_jobs import enqueue

ignore_list = [".DS_Store"]

class BenchSettings(Document):
	site_config_fields = [
		"background_workers",
		"shallow_clone",
		"admin_password",
		"auto_email_id",
		"auto_update",
		"frappe_user",
		"global_help_setup",
		"dropbox_access_key",
		"dropbox_secret_key",
		"gunicorn_workers",
		"github_username",
		"github_password",
		"mail_login",
		"mail_password",
		"mail_port",
		"mail_server",
		"use_tls",
		"rebase_on_pull",
		"redis_cache",
		"redis_queue",
		"redis_socketio",
		"restart_supervisor_on_update",
		"root_password",
		"serve_default_site",
		"socketio_port",
		"update_bench_on_update",
		"webserver_port",
		"file_watcher_port",
	]

	def set_attr(self, varname, varval):
		return setattr(self, varname, varval)

	def validate(self):
		self.sync_site_config()
		self.update_git_details()
		current_time = frappe.utils.time.time()
		if current_time - self.last_sync_timestamp > 10 * 60:
			sync_all(in_background=True)

	def sync_site_config(self):
		common_site_config_path = "common_site_config.json"
		with open(common_site_config_path, "r") as f:
			common_site_config_data = json.load(f)
			for site_config_field in self.site_config_fields:
				try:
					self.set_attr(site_config_field, common_site_config_data[site_config_field])
				except:
					pass

	def update_git_details(self):
		self.frappe_git_branch = safe_decode(
			check_output(
				"git rev-parse --abbrev-ref HEAD".split(), cwd=os.path.join("..", "apps", "frappe")
			)
		).strip("\n")

	@frappe.whitelist()
	def console_command(self, key, caller, app_name=None, branch_name=None):
		commands = {
			"bench_update": ["bench update"],
			"switch_branch": [""],
			"get-app": ["bench get-app {app_name}".format(app_name=app_name)],
		}
		frappe.enqueue(
			"bench_manager.bench_manager.utils.run_command",
			commands=commands[caller],
			doctype=self.doctype,
			key=key,
			docname=self.name,
		)


@frappe.whitelist()
def sync_sites():
	verify_whitelisted_call()
	site_dirs = update_site_list()
	site_entries = [x["name"] for x in frappe.get_all("Site")]
	create_sites = list(set(site_dirs) - set(site_entries))
	delete_sites = list(set(site_entries) - set(site_dirs))

	for site in create_sites:
		doc = frappe.get_doc({"doctype": "Site", "site_name": site, "developer_flag": 1})
		doc.insert()
		frappe.db.commit()

	for site in delete_sites:
		doc = frappe.get_doc("Site", site)
		doc.developer_flag = 1
		doc.save()
		doc.delete()
		frappe.db.commit()
	# frappe.msgprint('Sync sites completed')


@frappe.whitelist()
def sync_apps():
	verify_whitelisted_call()
	app_dirs = update_app_list()
	app_entries = [x["name"] for x in frappe.get_all("App")]
	create_apps = list(set(app_dirs) - set(app_entries))
	delete_apps = list(set(app_entries) - set(app_dirs))
	create_apps = [app for app in create_apps if app != ""]
	delete_apps = [app for app in delete_apps if app != ""]

	for app in create_apps:
		doc = frappe.get_doc(
			{
				"doctype": "App",
				"app_name": app,
				"app_description": "lorem ipsum",
				"app_publisher": "lorem ipsum",
				"app_email": "lorem ipsum",
				"developer_flag": 1,
			}
		)
		doc.insert()
		frappe.db.commit()

	for app in delete_apps:
		doc = frappe.get_doc("App", app)
		doc.developer_flag = 1
		doc.save()
		doc.delete()
		frappe.db.commit()
	# frappe.msgprint('Sync apps completed')


def update_app_list():
	app_list_file = "apps.txt"
	with open(app_list_file, "r") as f:
		apps = f.read().split("\n")
	return apps


def update_site_list():
	site_list = []
	for root, dirs, files in os.walk(".", topdown=True):
		for name in files:
			if name == "site_config.json":
				site_list.append(str(root).strip("./"))
				break
	if "" in site_list:
		site_list.remove("")
	return site_list


@frappe.whitelist()
def sync_backups():
	verify_whitelisted_call()
	backup_dirs_data = update_backup_list()
	backup_entries = [x["name"] for x in frappe.get_all("Site Backup")]
	backup_dirs = [
		x["date"] + " " + x["time"] + " " + x["site_name"] + " " + x["stored_location"]
		for x in backup_dirs_data
	]
	create_backups = list(set(backup_dirs) - set(backup_entries))
	delete_backups = list(set(backup_entries) - set(backup_dirs))

	for date_time_sitename_loc in create_backups:
		date_time_sitename_loc = date_time_sitename_loc.split(" ")
		backup = {}
		for x in backup_dirs_data:
			if (
				x["date"] == date_time_sitename_loc[0]
				and x["time"] == date_time_sitename_loc[1]
				and x["site_name"] == date_time_sitename_loc[2]
				and x["stored_location"] == date_time_sitename_loc[3]
			):
				backup = x
				break
		doc = frappe.get_doc(
			{
				"doctype": "Site Backup",
				"site_name": backup["site_name"],
				"date": backup["date"],
				"time": backup["time"],
				"stored_location": backup["stored_location"],
				"public_file_backup": backup["public_file_backup"],
				"private_file_backup": backup["private_file_backup"],
				"hash": backup["hash"],
				"file_path": backup["file_path"],
				"developer_flag": 1,
			}
		)
		doc.insert()
		frappe.db.commit()

	for backup in delete_backups:
		doc = frappe.get_doc("Site Backup", backup)
		doc.developer_flag = 1
		doc.save()
		frappe.db.commit()
		doc.delete()
		frappe.db.commit()

def update_backup_list():
	all_sites = []
	archived_sites = []
	sites = []
	for root, dirs, files in os.walk("../archived_sites/", topdown=True):
		archived_sites.extend(dirs)
		break
	archived_sites = ["../archived_sites/" + x for x in archived_sites]
	all_sites.extend(archived_sites)
	for root, dirs, files in os.walk("../sites/", topdown=True):
		for site in dirs:
			if os.path.isfile("../sites/{}/site_config.json".format(site)):
				sites.append(site)
		break
	sites = ["../sites/" + x for x in sites]
	all_sites.extend(sites)

	response = []

	backups = []
	for site in all_sites:
		backup_path = os.path.join(site, "private", "backups")
		backup_files = (
			safe_decode(
				check_output(shlex.split("ls ./{backup_path}".format(backup_path=backup_path)))
			)
			.strip("\n")
			.split("\n")
		)
		backup_files = [file for file in backup_files if "database.sql" in file]
		for backup_file in backup_files:
			inner_response = {}
			date_time_hash = backup_file.rsplit("-", 1)[0]
			file_path = backup_path + "/" + date_time_hash
			inner_response["site_name"] = site.split("/")[2]
			inner_response["stored_location"] = site.split("/")[1]
			inner_response["private_file_backup"] = os.path.isfile(
				backup_path + "/" + date_time_hash + "_private_files.tar"
			)
			inner_response["public_file_backup"] = os.path.isfile(
				backup_path + "/" + date_time_hash + "_files.tar"
			)
			inner_response["file_path"] = file_path[3:]
			try:
				inner_response["date"] = get_date(date_time_hash)
				inner_response["time"] = get_time(date_time_hash)
				inner_response["hash"] = get_hash(date_time_hash)
			except IndexError as e:
				inner_response["date"] = str(datetime.now().date())
				inner_response["time"] = str(datetime.now().time())
				inner_response["hash"] = " "
				traceback.print_exception(*sys.exc_info())
			response.append(inner_response)
	return response


def get_date(date_time_hash):
	return date_time_hash[:4] + "-" + date_time_hash[4:6] + "-" + date_time_hash[6:8]


def get_time(date_time_hash):
	time = date_time_hash.split("_")[1]
	return time[0:2] + ":" + time[2:4] + ":" + time[4:6]


def get_hash(date_time_hash):
	return date_time_hash.split("-")[1]


@frappe.whitelist()
def sync_all(in_background=False):
	if not in_background:
		frappe.msgprint("Sync has started and will run in the background...")
	verify_whitelisted_call()
	frappe.enqueue(
		"bench_manager.bench_manager.doctype.bench_settings.bench_settings.sync_sites"
	)
	frappe.enqueue(
		"bench_manager.bench_manager.doctype.bench_settings.bench_settings.sync_apps"
	)
	frappe.enqueue(
		"bench_manager.bench_manager.doctype.bench_settings.bench_settings.sync_backups"
	)
	frappe.set_value(
		"Bench Settings", None, "last_sync_timestamp", frappe.utils.time.time()
	)


@frappe.whitelist()
def setup_and_restart_nginx(root_password):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    commands = [
		"bench setup nginx --yes"
	]
    commands.append(f"echo '{root_password}' | sudo -S service nginx restart")
    run_command(commands,"Bench Settings",dt_string)
    
def run_command(commands, doctype, key, cwd="..", docname=" ", after_command=None):
	start_time = frappe.utils.time.time()
	console_dump = ""
	logged_command = " && ".join(commands)
	logged_command += (
		" "  # to make sure passwords at the end of the commands are also hidden
	)
	sensitive_data = ["--mariadb-root-password", "--admin-password", "--root-password"]
	for password in sensitive_data:
		logged_command = re.sub("{password} .*? ".format(password=password), "", logged_command, flags=re.DOTALL)
	the_password = logged_command.split("'")[1].split("'")[0]
	logged_command = logged_command.replace(the_password,"******")
	doc = frappe.get_doc(
		{
			"doctype": "Bench Manager Command",
			"key": key,
			"source": doctype + ": " + docname,
			"command": logged_command,
			"status": "Ongoing",
		}
	)
	doc.insert()
	frappe.db.commit()
	frappe.publish_realtime(
		key,
		"Executing Command:\n{logged_command}\n\n".format(logged_command=logged_command),
		user=frappe.session.user,
	)
	try:
		for command in commands:
			terminal = Popen(
				shlex.split(command), stdin=PIPE, stdout=PIPE, stderr=STDOUT, cwd=cwd
			)
			for c in iter(lambda: safe_decode(terminal.stdout.read(1)), ""):
				frappe.publish_realtime(key, c, user=frappe.session.user)
		if terminal.wait():
			_close_the_doc(
				start_time, key, console_dump, status="Failed", user=frappe.session.user
			)
		else:
			_close_the_doc(
				start_time, key, console_dump, status="Success", user=frappe.session.user
			)
	except Exception as e:
		_close_the_doc(
			start_time,
			key,
			status="Failed",
			user=frappe.session.user,
		)
	finally:
		frappe.db.commit()
		# hack: frappe.db.commit() to make sure the log created is robust,
		# and the _refresh throws an error if the doc is deleted
		frappe.enqueue(
			"bench_manager.bench_manager.utils._refresh",
			doctype=doctype,
			docname=docname,
			commands=commands,
		)


def backup_sites_with_daily_option():
    site_list = frappe.get_list("Site",filters={"frequency":"Daily","auto_backup":1,"dropbox_backup":0})
    if site_list:
        create_backup(site_list)
        
def backup_sites_with_weekly_option():
    site_list = frappe.get_list("Site",filters={"frequency":"Weekly","auto_backup":1,"dropbox_backup":0})
    if site_list:
        create_backup(site_list)

def backup_sites_with_monthly_option():
    site_list = frappe.get_list("Site",filters={"frequency":"Monthly","auto_backup":1,"dropbox_backup":0})
    if site_list:
        create_backup(site_list)


def dropbox_backup_sites_with_daily_option():
    site_list = frappe.get_list("Site",filters={"frequency":"Daily","auto_backup":1,"dropbox_backup":1})
    if site_list:
        take_dropbox_backup(site_list)
        
def dropbox_backup_sites_with_weekly_option():
    site_list = frappe.get_list("Site",filters={"frequency":"Weekly","auto_backup":1,"dropbox_backup":1})
    if site_list:
        take_dropbox_backup(site_list)

def dropbox_backup_sites_with_monthly_option():
    site_list = frappe.get_list("Site",filters={"frequency":"Monthly","auto_backup":1,"dropbox_backup":1})
    if site_list:
        take_dropbox_backup(site_list)

def create_backup(site_list):
    from bench_manager.bench_manager.utils import run_command
    for i in site_list:
        site_doc = frappe.get_doc("Site",i.name)
        key = datetime.now() + timedelta(seconds=1)
        commands=["bench --site {site_name} backup --with-files".format(site_name=i.name)]
        doctype=site_doc.doctype
        key=key.strftime("%Y/%m/%d, %H:%M:%S")
        docname=i.name
        run_command(commands, doctype, key, docname)


def take_dropbox_backup(site_list):
	"""Enqueue longjob for taking backup to dropbox"""
	enqueue(
		"bench_manager.bench_manager.doctype.bench_settings.bench_settings.take_backup_to_dropbox",
		site_list = site_list,
		queue="long",
		timeout=1500,
	)
	frappe.msgprint(_("Queued for backup. It may take a few minutes to an hour."))


def take_backup_to_dropbox(site_list,retry_count=0, upload_db_backup=True):
	try:
		backup_to_dropbox(site_list,upload_db_backup)
		if cint(frappe.db.get_value("Bench Settings", None, "send_email_for_successful_backup")):
			send_email(True, "Dropbox", "Bench Settings", "send_notifications_to")
	except JobTimeoutException:
		if retry_count < 2:
			args = {
				"retry_count": retry_count + 1,
				"upload_db_backup": False,  # considering till worker timeout db backup is uploaded
			}
			enqueue(
				"bench_manager.bench_manager.doctype.bench_settings.bench_settings.take_backup_to_dropbox",
				queue="long",
				timeout=1500,
				**args
			)
	except Exception:
		error_message = frappe.get_traceback()
		send_email(False, "Dropbox", "Bench Settings", "send_notifications_to", error_message)


@frappe.whitelist()
def get_dropbox_authorize_url():
	app_details = get_dropbox_settings(redirect_uri=True)
	dropbox_oauth_flow = dropbox.DropboxOAuth2Flow(
		consumer_key=app_details["app_key"],
		redirect_uri=app_details["redirect_uri"],
		session={},
		csrf_token_session_key="dropbox-auth-csrf-token",
		consumer_secret=app_details["app_secret"],
	)

	auth_url = dropbox_oauth_flow.start()

	return {"auth_url": auth_url, "args": parse_qs(urlparse(auth_url).query)}


@frappe.whitelist()
def get_redirect_url():
	if not frappe.conf.dropbox_broker_site:
		frappe.conf.dropbox_broker_site = "https://dropbox.erpnext.com"
	url = "{0}/api/method/dropbox_erpnext_broker.www.setup_dropbox.get_authotize_url".format(
		frappe.conf.dropbox_broker_site
	)

	try:
		response = make_post_request(url, data={"site": get_url()})
		if response.get("message"):
			return response["message"]

	except Exception:
		frappe.log_error()
		frappe.throw(
			_(
				"Something went wrong while generating dropbox access token. Please check error log for more details."
			)
		)


def backup_to_dropbox(site_list,upload_db_backup=True):
	if not frappe.db:
		frappe.connect()

	# upload database
	dropbox_settings = get_dropbox_settings()

	if not dropbox_settings["access_token"]:
		access_token = generate_oauth2_access_token_from_oauth1_token(dropbox_settings)

		if not access_token.get("oauth2_token"):
			return (
				"Failed backup upload",
				"No Access Token exists! Please generate the access token for Dropbox.",
			)

		dropbox_settings["access_token"] = access_token["oauth2_token"]
		set_dropbox_access_token(access_token["oauth2_token"])

	dropbox_client = dropbox.Dropbox(
		oauth2_access_token=dropbox_settings["access_token"], timeout=None
	)

	if upload_db_backup:
			if site_list:
				create_backup(site_list)
				sync_backups()
				for i in site_list:
					last_doc = frappe.get_list("Site Backup", filters={'site_name':i.name}, fields=['file_path'], order_by="creation desc",limit = 1)[0]
					list_string = last_doc.file_path.split('/')
					list_string.pop(0)
					list_string.insert(0, '.')
					string_list = ("/".join(list_string))
					upload_file_to_dropbox(string_list+"-database.sql.gz", f"/{i.name}", dropbox_client)
					upload_file_to_dropbox(string_list+"-site_config_backup.json", f"/{i.name}", dropbox_client)
					upload_file_to_dropbox(string_list+"-private-files.tar", f"/{i.name}", dropbox_client)
					upload_file_to_dropbox(string_list+"-files.tar", f"/{i.name}", dropbox_client)

def upload_file_to_dropbox(filename, folder, dropbox_client):
	"""upload files with chunk of 15 mb to reduce session append calls"""
	if not os.path.exists(filename):
		return

	create_folder_if_not_exists(folder, dropbox_client)
	file_size = os.path.getsize(encode(filename))
	chunk_size = get_chunk_site(file_size)

	mode = dropbox.files.WriteMode.overwrite

	f = open(encode(filename), "rb")
	path = "{0}/{1}".format(folder, os.path.basename(filename))

	try:
		if file_size <= chunk_size:
			dropbox_client.files_upload(f.read(), path, mode)
		else:
			upload_session_start_result = dropbox_client.files_upload_session_start(f.read(chunk_size))
			cursor = dropbox.files.UploadSessionCursor(
				session_id=upload_session_start_result.session_id, offset=f.tell()
			)
			commit = dropbox.files.CommitInfo(path=path, mode=mode)

			while f.tell() < file_size:
				if (file_size - f.tell()) <= chunk_size:
					dropbox_client.files_upload_session_finish(f.read(chunk_size), cursor, commit)
				else:
					dropbox_client.files_upload_session_append(
						f.read(chunk_size), cursor.session_id, cursor.offset
					)
					cursor.offset = f.tell()
	except dropbox.exceptions.ApiError as e:
		if isinstance(e.error, dropbox.files.UploadError):
			error = "File Path: {path}\n".format(path=path)
			error += frappe.get_traceback()
			frappe.log_error(error)
		else:
			raise


def create_folder_if_not_exists(folder, dropbox_client):
	try:
		dropbox_client.files_get_metadata(folder)
	except dropbox.exceptions.ApiError as e:
		# folder not found
		if isinstance(e.error, dropbox.files.GetMetadataError):
			dropbox_client.files_create_folder(folder)
		else:
			raise


def get_dropbox_settings(redirect_uri=False):
	if not frappe.conf.dropbox_broker_site:
		frappe.conf.dropbox_broker_site = "https://dropbox.erpnext.com"
	settings = frappe.get_doc("Bench Settings")
	app_details = {
		"app_key": settings.app_access_key or frappe.conf.dropbox_access_key,
		"app_secret": settings.get_password(fieldname="app_secret_key", raise_exception=False)
		if settings.app_secret_key
		else frappe.conf.dropbox_secret_key,
		"access_token": settings.get_password("dropbox_access_token", raise_exception=False)
		if settings.dropbox_access_token
		else "",
		"access_key": settings.get_password("dropbox_access_key", raise_exception=False),
		"access_secret": settings.get_password("dropbox_access_secret", raise_exception=False),
		"file_backup": settings.file_backup,
	}

	if redirect_uri:
		app_details.update(
			{
				"redirect_uri": get_request_site_address(True)
				+ "/api/method/bench_manager.bench_manager.doctype.bench_settings.bench_settings.dropbox_auth_finish"
				if settings.app_secret_key
				else frappe.conf.dropbox_broker_site
				+ "/api/method/dropbox_erpnext_broker.www.setup_dropbox.generate_dropbox_access_token",
			}
		)

	if not app_details["app_key"] or not app_details["app_secret"]:
		raise Exception(_("Please set Dropbox access keys in your site config"))

	return app_details


@frappe.whitelist()
def dropbox_auth_finish(return_access_token=False):
	app_details = get_dropbox_settings(redirect_uri=True)
	callback = frappe.form_dict
	close = '<p class="text-muted">' + _("Please close this window") + "</p>"

	dropbox_oauth_flow = dropbox.DropboxOAuth2Flow(
		consumer_key=app_details["app_key"],
		redirect_uri=app_details["redirect_uri"],
		session={"dropbox-auth-csrf-token": callback.state},
		csrf_token_session_key="dropbox-auth-csrf-token",
		consumer_secret=app_details["app_secret"],
	)

	if callback.state or callback.code:
		token = dropbox_oauth_flow.finish({"state": callback.state, "code": callback.code})
		if return_access_token and token.access_token:
			return token.access_token, callback.state

		set_dropbox_access_token(token.access_token)
	else:
		frappe.respond_as_web_page(
			_("Dropbox Setup"),
			_("Illegal Access Token. Please try again") + close,
			indicator_color="red",
			http_status_code=frappe.AuthenticationError.http_status_code,
		)

	frappe.respond_as_web_page(
		_("Dropbox Setup"), _("Dropbox access is approved!") + close, indicator_color="green"
	)


def set_dropbox_access_token(access_token):
    frappe.db.set_value("Bench Settings", None, "dropbox_access_token", access_token)
    frappe.db.commit()


def generate_oauth2_access_token_from_oauth1_token(dropbox_settings=None):
	if not dropbox_settings.get("access_key") or not dropbox_settings.get("access_secret"):
		return {}

	url = "https://api.dropboxapi.com/2/auth/token/from_oauth1"
	headers = {"Content-Type": "application/json"}
	auth = (dropbox_settings["app_key"], dropbox_settings["app_secret"])
	data = {
		"oauth1_token": dropbox_settings["access_key"],
		"oauth1_token_secret": dropbox_settings["access_secret"],
	}

	return make_post_request(url, auth=auth, headers=headers, data=json.dumps(data))