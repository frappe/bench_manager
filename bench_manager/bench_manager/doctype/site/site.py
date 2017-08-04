# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappé and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import subprocess
import json
import re

class Site(Document):
	def validate(self):
		if self.get("__islocal"):
			self.create_site()		
		else:
			self.update_site_config()
			self.sync_site_config()

	def create_site(self):
		site_list = subprocess.check_output("ls", shell=True).split("\n")
		if self.site_name in site_list:
			frappe.throw("Site: "+ self.site_name+ " already exists, but most\
				likely there isn't a log of this site. Please click sync to\
				refresh your site list!")
		else:
			subprocess.check_output("cd .. && bench new-site "+self.site_name,
				shell=True)

	def on_trash(self):
		site_list = subprocess.check_output("ls", shell=True).split("\n")
		if self.site_name in site_list:
			subprocess.check_output("cd .. && bench drop-site "+self.site_name,
				shell=True)
		else:
			frappe.throw("Site: "+ self.site_name+ " doesn't exists! Please\
				click sync to refresh your site list!")

	def update_site_config(self):
		self.app_list = '\n'.join(frappe.get_installed_apps()) #TODO: this is wrong, enter the console and retrive the code for the site in question
		site_config_path = self.site_name+'/site_config.json'
		common_site_config_path = 'common_site_config.json'
		with open(site_config_path, 'r') as f:
			site_config_data = json.load(f)
		with open(common_site_config_path, 'r') as f:
			common_site_config_data = json.load(f)

	def sync_site_config(self):
		pass