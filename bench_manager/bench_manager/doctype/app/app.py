# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappé and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from subprocess import check_output, Popen, PIPE
import os, re, time
from  bench_manager.bench_manager.utils import console_command

class App(Document):
	app_info_fields = ["app_title", "app_description", "app_publisher", "app_email",
		"app_icon", "app_color", "app_license"]

	def validate(self):
		if self.get("__islocal"):
			frappe.msgprint(str(self.developer_flag))
			if self.developer_flag == 0:
				self.create_app(self.key)
			self.developer_flag = 0
			app_data_path = '../apps/'+self.app_name+'/'+self.app_name+'.egg-info/PKG-INFO'
			while not os.path.isfile(app_data_path):
				time.sleep(2)
			self.update_app_details()
		else:
			if self.developer_flag == 0:
				self.update_app_details()

	def get_attr(self, varname):
		return getattr(self, varname)

	def set_attr(self, varname, varval):
		return setattr(self, varname, varval)

	def create_app(self, key):
		app_list = check_output("cd ../apps && ls",
			shell=True).split("\n")
		if self.app_name in app_list:
			frappe.throw("App: "+ self.app_name + " already exists, but most\
				likely there isn't a log of this app. Please click sync to\
				refresh your app list!")
		else:
			if ' ' in self.app_name:
				frappe.throw("The app name should be developer friendly, and \
					should not contain spaces !")
			else:
				terminal = Popen("cd .. && bench new-app " + self.app_name,
					stdin=PIPE, shell=True)
				str_to_exec = ''
				for app_info_field in self.app_info_fields:
					if self.get_attr(app_info_field) == None:
						self.set_attr(app_info_field, '\n')
					else:
						self.set_attr(app_info_field, self.get_attr(app_info_field)+'\n')
					str_to_exec += self.get_attr(app_info_field)

				frappe.msgprint('Creating app, please be patient...')
				terminal.communicate(str_to_exec)
				frappe.msgprint('Done')

	def on_trash(self):
		if self.developer_flag == 0:
			frappe.throw('Not allowed!')
		else:
			# todo: check if the app is linked to any site
			apps_file = 'apps.txt'
			with open(apps_file, 'r') as f:
				apps = f.readlines()
			try:
				apps.remove(self.app_name)
			except:
				try:
					apps.remove(self.app_name+'\n')
				except:
					pass
			os.remove(apps_file)
			with open(apps_file, 'w') as f:
			    f.writelines(apps)
			check_output("rm -rf " + self.app_name, shell=True)

	def update_app_details(self):
		try:
			app_data_path = '../apps/'+self.app_name+'/'+self.app_name+'.egg-info/PKG-INFO'
			with open(app_data_path, 'r') as f:
				app_data = f.readlines()
			for data in app_data:
				if 'Version:' in data:
					self.version = ''.join(re.findall('Version: (.*?)\\n', data))
				elif 'Summary:' in data:
					self.app_description = ''.join(re.findall('Summary: (.*?)\\n', data))
				elif 'Author:' in data:
					self.app_publisher = ''.join(re.findall('Author: (.*?)\\n', data))
				elif 'Author-email:' in data:
					self.app_email = ''.join(re.findall('Author-email: (.*?)\\n', data))
			self.app_title = self.app_name
			self.app_title = self.app_title.replace('-', ' ')
			self.app_title = self.app_title.replace('_', ' ')
		except:
			frappe.throw("Hey developer, the app you're trying to create an \
				instance of doesn't actually exist. You could consider setting \
				developer flag to 0 to actually create the app")