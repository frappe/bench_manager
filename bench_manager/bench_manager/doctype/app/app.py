# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappé and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from subprocess import check_output, Popen, PIPE

class App(Document):
	pass
	# def validate(self):
	# 	if self.get("__islocal"):
	# 		self.create_app()
	# 	else:
	# 		seld.update_app_details()

	# def create_app(self):
	# 	app_list = check_output("cd ../apps && ls",
	# 		shell=True).split("\n")
	# 	if self.app_name in app_list:
	# 		frappe.throw("App: "+ self.app_name + " already exists, but most\
	# 			likely there isn't a log of this app. Please click sync to\
	# 			refresh your app list!")
	# 	else:
	# 		terminal = Popen("cd .. && bench new-app " + self.app_name,
	# 			stdin=PIPE, shell=True)
	# 		self.app_title = self.app_title if self.app_title!='' else '\n'
	# 		self.app_description = self.app_description + '\n'
	# 		self.app_publisher = self.app_publisher + '\n' 
	# 		self.app_email = self.app_email + '\n'
	# 		self.app_icon = self.app_icon if self.app_icon!='' else '\n'
	# 		self.app_color = self.app_color if self.app_color!='' else '\n'
	# 		terminal.communicate(self.app_title + self.app_description + 
	# 			self.app_publisher + self.app_email + self.app_icon + 
	# 			self.app_color)

	# def on_trash(self):
	# 	app_list = check_output("cd ../apps && ls",
	# 		shell=True).split("\n")

	# 	if self.app_name in app_list:
	# 		check_output("cd .. && bench remove-from-installed-apps "
	# 			+self.app_name, shell=True)
	# 	else:
	# 		frappe.throw("App: "+ self.app_name+ " doesn't exist! Please click\
	# 			sync to  refresh your app list!")

	def update_app_details(self):
		pass