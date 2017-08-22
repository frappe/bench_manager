# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappé and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from subprocess import check_output, Popen, PIPE
import os, re, json
# from  bench_manager.bench_manager.doctype.bench_setting.bench_setting import sync_backups

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
			if self.developer_flag == 0:
				self.create_site()
			self.developer_flag = 0
			self.sync_site_config()
			self.update_app_list()
		else:
			if self.developer_flag == 0:
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
		if self.developer_flag == 0:
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
		terminal = check_output("bench --site "+self.site_name+" list-apps",
			shell=True, cwd='..')
		return terminal.strip('\n').split('\n')

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
						self.set_attr(site_config_field,
							common_site_config_data[site_config_field])
					except:
						pass
			with open(site_config_path, 'r') as f:
				site_config_data = json.load(f)
				for site_config_field in self.site_config_fields:
					try:
						self.set_attr(site_config_field,
							site_config_data[site_config_field])
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
	removable_apps = frappe.get_doc(doctype, docname).app_list.split('\n')
	removable_apps.remove('frappe')
	return removable_apps

@frappe.whitelist()
def console_command(doctype, docname, key, bench_command, app_name=''):
	shell_commands = {
		"install_app": "bench --site "+ docname + " install-app "+app_name,
		"remove_app": "bench --site "+ docname + " uninstall-app "+app_name+" --yes",
		"backup_site": "bench --site "+ docname + " backup --with-files",
		"migrate": "bench --site "+ docname + " migrate",
		"reinstall": "bench --site "+ docname + " reinstall --yes"
	}
	str_to_exec = [shell_commands[bench_command]]
	frappe.enqueue('bench_manager.bench_manager.doctype.bench_manager_command.bench_manager_command.run_command',
		exec_str_list=str_to_exec, cwd='..', doctype=doctype, key=key, docname=docname)