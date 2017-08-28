# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappé and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from subprocess import check_output, Popen, PIPE
import os, re, json, time
from  bench_manager.bench_manager.utils import console_command

class Site(Document):
	site_config_fields = ["maintenance_mode", "pause_scheduler", "db_name", "db_password",
		"developer_mode", "limits"]
	limits_fields = ["emails", "expiry", "space", "space_usage"]
	space_usage_fields = ["backup_size", "database_size", "files_size", "total"]

	def get_attr(self, varname):
		return getattr(self, varname)

	def set_attr(self, varname, varval):
		return setattr(self, varname, varval)

	def validate(self):
		if self.get("__islocal"):
			if self.developer_flag == 0:
				self.create_site(self.key)
			site_config_path = self.site_name+'/site_config.json'
			while not os.path.isfile(site_config_path):
				time.sleep(2)
			self.developer_flag = 0
			self.sync_site_config()
			self.app_list = 'frappe'
		else:
			if self.developer_flag == 0:
				self.update_app_list()
				self.sync_site_config()
				# self.update_site_config()

	def create_site(self, key):
		site_list = check_output("ls".split()).split("\n")
		if self.site_name in site_list:
			frappe.throw("Site: "+ self.site_name+ " already exists, but most\
				likely there isn't a log of this site. Please click sync to\
				refresh your site list!")
		else:
			console_command(doctype=self.doctype, docname=self.site_name, key=key, bench_command='new-site')

	def on_trash(self):
		if self.developer_flag == 0:
			site_list = check_output("ls", shell=True).split("\n")
			if self.site_name in site_list:
				# console_command(docname=self.site_name, key=key, bench_command='drop-site')
				check_output("bench drop-site "+self.site_name,
					shell=True, cwd='..')
			else:
				frappe.throw("Site: "+ self.site_name+ " doesn't exists! Please\
					click sync to refresh your site list!")
		else:
			pass

	def update_app_list(self):
		self.app_list = '\n'.join(self.get_installed_apps())

	def get_installed_apps(self):
		terminal = check_output("bench --site "+self.site_name+" list-apps",
			shell=True, cwd='..')
		return terminal.strip('\n').split('\n')

	def update_site_config(self):

		site_config_path = self.site_name+'/site_config.json'
		common_site_config_path = 'common_site_config.json'

		with open(site_config_path, 'r') as f:
			site_config_data = json.load(f)
		with open(common_site_config_path, 'r') as f:
			common_site_config_data = json.load(f)

		for site_config_field in self.site_config_fields:

			if self.get_attr(site_config_field) == None or self.get_attr(site_config_field) == '':
				frappe.msgprint(site_config_field)
				if site_config_data.get(site_config_field) != None:
					site_config_data.pop(site_config_field)
				self.set_attr(site_config_field,
					common_site_config_data[site_config_field])

			elif (not common_site_config_data.get(site_config_field) or self.get_attr(site_config_field) != common_site_config_data[site_config_field]):
				site_config_data[site_config_field] = self.get_attr(site_config_field)
				# frappe.msgprint()
			elif self.get_attr(site_config_field) == common_site_config_data[site_config_field]:
				if site_config_data.get(site_config_field) != None:
					site_config_data.pop(site_config_field)

			os.remove(site_config_path)
			with open(site_config_path, 'w') as f:
					json.dump(site_config_data, f, indent=4)

	def sync_site_config(self):
		if os.path.isfile(self.site_name+'/site_config.json'):
			site_config_path = self.site_name+'/site_config.json'
			with open(site_config_path, 'r') as f:
				site_config_data = json.load(f)
				for site_config_field in self.site_config_fields:
					try:
						self.set_attr(site_config_field,
							site_config_data[site_config_field])
					except:
						pass
		else:
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
	removable_apps = frappe.get_doc(doctype, docname).app_list.split('\n')
	removable_apps.remove('frappe')
	return removable_apps