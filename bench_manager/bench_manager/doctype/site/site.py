# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappé and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from subprocess import check_output, Popen, PIPE
import os, re, json, time, _mysql
from  bench_manager.bench_manager.utils import console_command

class Site(Document):
	site_config_fields = ["maintenance_mode", "pause_scheduler", "db_name", "db_password",
		"developer_mode", "disable_website_cache" "limits"]
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
			self.sync_site_config()
			self.app_list = 'frappe'
			if self.developer_flag == 1:
				self.update_app_list()
			self.developer_flag = 0
		else:
			if self.developer_flag == 0:
				self.update_app_list()
				self.update_site_config()
				self.sync_site_config()

	def after_command(self, commands=None):
		frappe.publish_realtime("Bench-Manager:reload-page")

	# def create_site(self, key):
	# 	site_list = check_output("ls".split()).split("\n")
	# 	if self.site_name in site_list:
	# 		frappe.throw("Site: "+ self.site_name+ " already exists, but most\
	# 			likely there isn't a log of this site. Please click sync to\
	# 			refresh your site list!")
	# 	else:
	# 		if not self.install_erpnext:
	# 			console_command(doctype=self.doctype,
	# 				docname=self.site_name,
	# 				key=key,
	# 				commands="bench new-site {}".format(self.site_name))
	# 		else:
	# 			with open('apps.txt', 'r') as f:
	# 			    app_list = f.read()
	# 			if 'erpnext' in app_list:
	# 				console_command(doctype=self.doctype,
	# 					docname = self.site_name,
	# 					key = key,
	# 					commands = "bench new-site {}\rbench --site {} install-app erpnext".format(docname, docname))
	# 			else:
	# 				console_command(doctype=self.doctype,
	# 					docname=self.site_name,
	# 					key=key,
	# 					commands = "bench new-site {}\rbench get-app erpnext https://github.com/frappe/erpnext.git\rbench --site {} install-app erpnext".format(docname, docname))

	def on_trash(self):
		if self.developer_flag == 0:
			# frappe.throw("Please go inside the site and try deleting again")
			frappe.publish_realtime("Bench-Manager:drop-site", {"site_name": self.site_name}, user=frappe.session.user)
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

		editable_site_config_fields = ["maintenance_mode", "pause_scheduler",
			"developer_mode", "disable_website_cache"]

		for site_config_field in editable_site_config_fields:
			if self.get_attr(site_config_field) == None or self.get_attr(site_config_field) == '':
				if site_config_data.get(site_config_field) != None:
					site_config_data.pop(site_config_field)
				self.set_attr(site_config_field,
					common_site_config_data.get(site_config_field))

			elif (not common_site_config_data.get(site_config_field) or self.get_attr(site_config_field) != common_site_config_data[site_config_field]):
				site_config_data[site_config_field] = self.get_attr(site_config_field)

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
					if site_config_data.get(site_config_field):
						self.set_attr(site_config_field,
							site_config_data[site_config_field])

				if site_config_data.get('limits'):
					for limits_field in self.limits_fields:
						if site_config_data.get('limits').get(limits_field):
							self.set_attr(limits_field,
								site_config_data['limits'][limits_field])

					if site_config_data.get('limits').get('space_usage'):
						for space_usage_field in self.space_usage_fields:
							if site_config_data.get('limits').get('space_usage').get(space_usage_field):
								self.set_attr(space_usage_field,
									site_config_data['limits']['space_usage'][space_usage_field])
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

@frappe.whitelist()
def pass_exists(doctype, docname=''):
	#return string convention 'TT',<root_password>,<admin_password>
	ret = {'condition':'', 'root_password':'', 'admin_password':''}
	common_site_config_path = 'common_site_config.json'
	with open(common_site_config_path, 'r') as f:
		common_site_config_data = json.load(f)

	ret['condition'] += 'T' if common_site_config_data.get('root_password') else 'F'
	ret['root_password'] = common_site_config_data.get('root_password')

	ret['condition'] += 'T' if common_site_config_data.get('admin_password') else 'F'
	ret['admin_password'] = common_site_config_data.get('admin_password')

	if docname == '': #Prompt reached here on new-site
		return ret

	site_config_path = docname+'/site_config.json'
	with open(site_config_path, 'r') as f:
		site_config_data = json.load(f)
	#FF FT TF
	ret['condition'][1] = 'T' if site_config_data.get('admin_password') else 'F'
	ret['admin_password'] = site_config_data.get('admin_password')
	return ret


@frappe.whitelist()
def verify_new_site(site_name, mysql_password, admin_password, install_erpnext, key):
	all_sites = frappe.get_all('Site')
	all_sites = [site["name"] for site in all_sites]
	process = check_output("ls".split())
	process = process.strip('\n').split('\n')
	all_sites = list(set(all_sites) | set(process))
	if site_name in all_sites:
		frappe.throw("Site already exists!")
	try:
		db = _mysql.connect(host=frappe.conf.db_host or u'localhost', user=u'root' ,passwd=mysql_password)
		db.close()
	except Exception as e:
		print e
	create_site(site_name=site_name, install_erpnext=install_erpnext, mysql_password=mysql_password, admin_password=admin_password, key=key)
	return "console"

def create_site(site_name, install_erpnext, mysql_password, admin_password, key):
	commands = "bench new-site --mariadb-root-password {mysql_password} \
		--admin-password {admin_password} {site_name}".format(site_name=site_name, 
		admin_password=admin_password, mysql_password=mysql_password)
	if install_erpnext == "true":
		with open('apps.txt', 'r') as f:
		    app_list = f.read()
		if 'erpnext' not in app_list:
			commands += "\rbench get-app erpnext https://github.com/frappe/erpnext.git"
		else:
			commands += "\rbench --site {site_name} install-app erpnext".format(site_name=site_name)
	console_command(doctype="Bench Settings", key=key, commands = commands)
	all_sites = check_output("ls").strip('\n').split('\n')
	while site_name not in all_sites:
		time.sleep(2)
		all_sites = check_output("ls").strip('\n').split('\n')
		print "waiting... "
	doc = frappe.get_doc({'doctype': 'Site', 'site_name': site_name, 'developer_flag':1})
	doc.insert()