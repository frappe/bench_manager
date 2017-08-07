# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappé and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from subprocess import check_output, Popen, PIPE
import sys

class App(Document):
	def validate(self):
		if self.get("__islocal"):
			self.create_app()
		else:
			self.update_app_details()

	def create_app(self):
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
				self.app_title = self.app_title + '\n'
				self.app_description = self.app_description + '\n'
				self.app_publisher = self.app_publisher + '\n' 
				self.app_email = self.app_email + '\n'
				self.app_icon = self.app_icon + '\n' if self.app_icon!=None else '\n'
				self.app_color = self.app_color + '\n' if self.app_color!=None else '\n'
				self.app_license = self.app_license + '\n' if self.app_license!=None else '\n'
				terminal.communicate(self.app_title + self.app_description + 
					self.app_publisher + self.app_email + self.app_icon + 
					self.app_color + self.app_license)
				if self.app_title == None:
					self.app_title = self.app_title.replace('-', ' ')
					self.app_title = self.app_title.replace('_', ' ')

	def on_trash(self):
		frappe.throw('Not allowed!')

	def update_app_details(self):
		pass