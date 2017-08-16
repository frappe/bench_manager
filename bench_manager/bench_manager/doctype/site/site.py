# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappé and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json
from subprocess import check_output, Popen, PIPE
import re
import os

class Site(Document):
	site_config_fields = ["auto_update", "background_workers", "developer_mode",
		"file_watcher_port", "frappe_user", "gunicorn_workers",
		"rebase_on_pull", "redis_cache", "redis_queue", "redis_socketio", 
		"restart_supervisor_on_update", "serve_default_site", "shallow_clone",
		"socketio_port", "update_bench_on_update", "webserver_port",
		"root_password", "admin_password", "db_name", "db_password"]

	def get_attr(self, varname):
		return getattr(self, varname)

	def set_attr(self, varname, varval):
		return setattr(self, varname, varval)

	def validate(self):
		if self.get("__islocal"):
			if self.bypass_flag == 0:
				self.create_site()
			self.bypass_flag = 0
			self.sync_site_config()
			self.update_app_list()
		else:
			if self.bypass_flag == 0:
				self.update_app_list()
				self.update_site_config()
				self.sync_site_config()

	def create_site(self):
		site_list = check_output("ls", shell=True).split("\n")
		if self.site_name in site_list:
			frappe.throw("Site: "+ self.site_name+ " already exists, but most\
				likely there isn't a log of this site. Please click sync to\
				refresh your site list!")
		else:
			check_output("bench new-site "+self.site_name,
				shell=True, cwd='..')

	def on_trash(self):
		if self.bypass_flag == 0:
			site_list = check_output("ls", shell=True).split("\n")
			if self.site_name in site_list:
				check_output("bench drop-site "+self.site_name,
					shell=True, cwd='..')
			else:
				frappe.throw("Site: "+ self.site_name+ " doesn't exists! Please\
					click sync to refresh your site list!")
			return
		else:
			pass

	def update_app_list(self):
		self.app_list = '\n'.join(self.get_installed_apps())

	def get_installed_apps(self):
		terminal = Popen("bench --site "+self.site_name+" console",
			stdout=PIPE, stdin=PIPE, shell=True, cwd='..')
		out, error = terminal.communicate("frappe.get_installed_apps()\nexit()")
		out = out.split('\n')
		return re.findall("u\'(.*?)\'", out[9])

	def update_site_config(self):
		site_config_path = self.site_name+'/site_config.json'
		common_site_config_path = 'common_site_config.json'
		with open(site_config_path, 'r') as f:
			site_config_data = json.load(f)

		for site_config_field in self.site_config_fields:
			site_config_data[site_config_field] = self.get_attr(site_config_field)

		os.remove(site_config_path)
		with open(site_config_path, 'w') as f:
		    json.dump(site_config_data, f, indent=4)

	def sync_site_config(self):
		try:
			site_config_path = self.site_name+'/site_config.json'
			common_site_config_path = 'common_site_config.json'
			with open(common_site_config_path, 'r') as f:
				common_site_config_data = json.load(f)
				for site_config_field in self.site_config_fields:
					try:
						self.set_attr(site_config_field, common_site_config_data[site_config_field])
					except:
						pass
			with open(site_config_path, 'r') as f:
				site_config_data = json.load(f)
				for site_config_field in self.site_config_fields:
					try:
						self.set_attr(site_config_field, site_config_data[site_config_field])
					except:
						pass
		except:
			frappe.throw("Hey developer, the site you're trying to create an \
				instance of doesn't actually exist. You could consider setting \
				bypass flag to 0 to actually create the site")

@frappe.whitelist()
def get_installable_apps(doctype, docname):
	app_list_file = 'apps.txt'
	with open(app_list_file, "r") as f:
		apps = f.read().split('\n')
	installed_apps = frappe.get_doc(doctype, docname).app_list.split('\n')
	installable_apps = set(apps) - set(installed_apps)
	return [x for x in installable_apps]

@frappe.whitelist()
def get_removable_apps(doctype, docname):
	return frappe.get_doc(doctype, docname).app_list.split('\n')

@frappe.whitelist()
def install_app(doctype, docname, app_name):
	check_output("bench --site "+frappe.get_doc(doctype, docname).site_name+" install-app "+app_name, shell=True, cwd='..')	
	frappe.get_doc(doctype, docname).update_app_list()

@frappe.whitelist()
def remove_app(doctype, docname, app_name):
	terminal = Popen("bench --site "+frappe.get_doc(doctype, docname).site_name+" uninstall-app "+app_name, stdin=PIPE, shell=True, cwd='..')
	terminal.communicate("y\n")
	frappe.get_doc(doctype, docname).update_app_list()

@frappe.whitelist()
def backup_site(doctype, docname):
	terminal = check_output("bench --site "+frappe.get_doc(doctype, docname).site_name+" backup --with-files", shell=True, cwd='..')
	return str(terminal)

@frappe.whitelist()
def restore_options(doctype, docname):
	all_sites = []
	archived_sites = []
	sites = []
	for root, dirs, files in os.walk("../archived_sites/", topdown=True):
		archived_sites.extend(dirs)
		break
	archived_sites = ["../archived_sites/"+x for x in archived_sites]
	all_sites.extend(archived_sites)
	for root, dirs, files in os.walk("../sites/", topdown=True):
		for site in dirs:
			files_list = check_output("cd ../sites/"+site+" && ls", shell=True).split("\n")
			if 'site_config.json' in files_list:
				sites.append(site)
		break
	sites = ["../sites/"+x for x in sites]
	all_sites.extend(sites)


	response = []

	backups = []
	for site in all_sites:
		backup_path = os.path.join(site, "private", "backups")
		backup_files = check_output("cd "+backup_path+" && ls *database.sql*", shell=True).strip('\n').split('\n')
		for backup_file in backup_files:
			inner_response = {}
			date_time_hash = backup_file.rsplit('_', 1)[0]
			inner_response['path'] = backup_path
			inner_response['site_name'] = site.split('/')[2]
			inner_response['location'] = site.split('/')[1]
			inner_response['date'] = get_date(date_time_hash)
			inner_response['time'] = get_time(date_time_hash)
			inner_response['hash'] = get_hash(date_time_hash)
			inner_response['public_files'] = os.path.isfile(backup_path+'/'+date_time_hash+"_files.tar")
			inner_response['private_files'] = os.path.isfile(backup_path+'/'+date_time_hash+"_private_files.tar")
			response.append(inner_response)
	return response

def get_date(date_time_hash):
	months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
	date = int(date_time_hash.split('_')[0])
	return str(date % 100) + ' ' +str(months[(date/100)%100 - 1]) + ' ' + str(date / 10000)

def get_time(date_time_hash):
	time = date_time_hash.split('_')[1]
	return time[0:2]+':'+time[2:4]+':'+time[4:6]

def get_hash(date_time_hash):
	return date_time_hash.split('_')[2]


@frappe.whitelist()
def restore_backup(doctype, docname, backup_name, with_public_files, with_private_files):
	backup_vars = backup_name.split(' * ')
	file_path = ''
	if backup_vars[3] == '(archived_sites)':
		file_path += 'archived_sites/'
	else:
		file_path += 'sites/'
	file_path += backup_vars[0]+'/private/backups/'
	file_path += revert_date(backup_vars[1])+'_'+revert_time(backup_vars[2])+'_'+revert_hash(backup_vars[4])
	sql_file_path = file_path+'_database.s*'
	public_tar_path = file_path+'_files.tar'
	private_tar_path = file_path+'_private_files.tar'
	
	str_to_exec = "bench --site "+frappe.get_doc(doctype, docname).site_name+" --force restore " + sql_file_path
	if os.path.isfile(public_tar_path) and with_public_files == 'true':
		str_to_exec += " --with-public-files " + public_tar_path
	if os.path.isfile(private_tar_path) and with_private_files == 'true':
		str_to_exec += " --with-private-files " + private_tar_path
	
	terminal = check_output(str_to_exec, shell=True, cwd='..')
	return str(terminal)

def revert_date(date):
	months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
	date = date.split(' ')
	if months.index(date[1]) < 10:
		mid = '0'+str(months.index(date[1]) + 1)
	else:
		mid = str(months.index(date[1]) + 1)
	return str(date[2]+mid+date[0])

def revert_time(time):
	time = time.strip('hrs').split(':')
	new_time = ''.join(time)
	return new_time

def revert_hash(hash):
	return str(hash.strip("'"))