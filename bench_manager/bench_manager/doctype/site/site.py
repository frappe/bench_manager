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
			self.create_site()		
			self.sync_site_config()
		else:
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
			check_output("cd .. && bench new-site "+self.site_name,
				shell=True)

	def on_trash(self):
		site_list = check_output("ls", shell=True).split("\n")
		if self.site_name in site_list:
			check_output("cd .. && bench drop-site "+self.site_name,
				shell=True)
		else:
			frappe.throw("Site: "+ self.site_name+ " doesn't exists! Please\
				click sync to refresh your site list!")
		return

	def update_app_list(self):
		self.app_list = '\n'.join(self.get_installed_apps())

	def get_installed_apps(self):
		terminal = Popen("cd .. && bench --site "+self.site_name+" console", stdout=PIPE, stdin=PIPE, shell=True)
		out, error = terminal.communicate("frappe.get_installed_apps()\nexit()")
		out = out.split('\n')
		return re.findall("u\'(.*?)\'", out[9])

	def update_site_config(self):
		site_config_path = self.site_name+'/site_config.json'
		common_site_config_path = 'common_site_config.json'
		with open(common_site_config_path, 'r') as f:
			common_site_config_data = json.load(f)
		with open(site_config_path, 'r') as f:
			site_config_data = json.load(f)

		for site_config_field in self.site_config_fields:
			site_config_data[site_config_field] = self.get_attr(site_config_field)

		os.remove(site_config_path)
		with open(site_config_path, 'w') as f:
		    json.dump(site_config_data, f, indent=4)

	def sync_site_config(self):
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

	def add_app(self):
		pass

	def remove_app(self):
		pass