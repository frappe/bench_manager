# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappé and contributors
# For license information, please see license.txt


import json
import os
import re
import shlex
import time
from subprocess import PIPE, Popen, check_output

import frappe
import pymysql
from bench_manager.bench_manager.utils import (
	safe_decode,
	verify_whitelisted_call,
)
from frappe.model.document import Document


class Site(Document):
	site_config_fields = [
		"maintenance_mode",
		"pause_scheduler",
		"db_name",
		"db_password",
		"developer_mode",
		"disable_website_cache" "limits",
	]
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
			site_config_path = self.site_name + "/site_config.json"
			while not os.path.isfile(site_config_path):
				time.sleep(2)
			self.sync_site_config()
			self.app_list = "frappe"
			if self.developer_flag == 1:
				self.update_app_list()
			self.developer_flag = 0
		else:
			if self.developer_flag == 0:
				self.update_site_config()
				self.sync_site_config()

	def after_command(self, commands=None):
		frappe.publish_realtime("Bench-Manager:reload-page")

	@frappe.whitelist()
	def update_app_alias(self):
		self.update_app_list()
		self.update_site_alias()

	def update_app_list(self):
		# self.set_attr("app_list", '\n'.join(self.get_installed_apps()))
		self.db_set("app_list", "\n".join(self.get_installed_apps()))

	def update_site_alias(self):
		alias_list = ""
		for link in os.listdir("."):
			if os.path.islink(link) and self.name in os.path.realpath(link):
				alias_list += link + "\n"
		self.db_set("site_alias", alias_list)

	def get_installed_apps(self):
		all_sites = safe_decode(check_output("ls")).strip("\n").split("\n")

		retry = 0
		while self.site_name not in all_sites and retry < 3:
			time.sleep(2)
			print("waiting for site creation...")
			retry += 1
			all_sites = safe_decode(check_output("ls")).strip("\n").split("\n")

		if retry == 3 and self.site_name not in all_sites:
			list_apps = "frappe"
		else:
			list_apps = check_output(
				shlex.split("bench --site {site_name} list-apps".format(site_name=self.site_name)),
				cwd="..",
			)

		if "frappe" not in safe_decode(list_apps):
			list_apps = "frappe"
		return safe_decode(list_apps).strip("\n").split("\n")

	def update_site_config(self):
		site_config_path = os.path.join(self.site_name, "site_config.json")
		common_site_config_path = os.path.join("common_site_config.json")

		with open(site_config_path, "r") as f:
			site_config_data = json.load(f)
		with open(common_site_config_path, "r") as f:
			common_site_config_data = json.load(f)

		editable_site_config_fields = [
			"maintenance_mode",
			"pause_scheduler",
			"developer_mode",
			"disable_website_cache",
		]

		for site_config_field in editable_site_config_fields:
			if (
				self.get_attr(site_config_field) == None or self.get_attr(site_config_field) == ""
			):
				if site_config_data.get(site_config_field) != None:
					site_config_data.pop(site_config_field)
				self.set_attr(site_config_field, common_site_config_data.get(site_config_field))

			elif (
				not common_site_config_data.get(site_config_field)
				or self.get_attr(site_config_field) != common_site_config_data[site_config_field]
			):
				site_config_data[site_config_field] = self.get_attr(site_config_field)

			elif self.get_attr(site_config_field) == common_site_config_data[site_config_field]:
				if site_config_data.get(site_config_field) != None:
					site_config_data.pop(site_config_field)

			os.remove(site_config_path)
			with open(site_config_path, "w") as f:
				json.dump(site_config_data, f, indent=4)

	def sync_site_config(self):
		if os.path.isfile(self.site_name + "/site_config.json"):
			site_config_path = self.site_name + "/site_config.json"
			with open(site_config_path, "r") as f:
				site_config_data = json.load(f)
				for site_config_field in self.site_config_fields:
					if site_config_data.get(site_config_field):
						self.set_attr(site_config_field, site_config_data[site_config_field])

				if site_config_data.get("limits"):
					for limits_field in self.limits_fields:
						if site_config_data.get("limits").get(limits_field):
							self.set_attr(limits_field, site_config_data["limits"][limits_field])

					if site_config_data.get("limits").get("space_usage"):
						for space_usage_field in self.space_usage_fields:
							if site_config_data.get("limits").get("space_usage").get(space_usage_field):
								self.set_attr(
									space_usage_field, site_config_data["limits"]["space_usage"][space_usage_field]
								)
		else:
			frappe.throw("The site you're trying to access doesn't actually exist.")

	@frappe.whitelist()
	def create_alias(self, key, alias):
		files = check_output("ls")
		if alias in files:
			frappe.throw("Sitename already exists")
		else:
			self.console_command(key=key, caller="create-alias", alias=alias)

	@frappe.whitelist()
	def console_command(
		self, key, caller, alias=None, app_name=None, admin_password=None, mysql_password=None
	):
		site_abspath = None
		if alias:
			site_abspath = os.path.abspath(os.path.join(self.name))
		commands = {
			"migrate": ["bench --site {site_name} migrate".format(site_name=self.name)],
			"create-alias": [
				"ln -s {site_abspath} sites/{alias}".format(site_abspath=site_abspath, alias=alias)
			],
			"delete-alias": ["rm sites/{alias}".format(alias=alias)],
			"backup": [
				"bench --site {site_name} backup --with-files".format(site_name=self.name)
			],
			"reinstall": [
				"bench --site {site_name} reinstall --yes --admin-password {admin_password}".format(
					site_name=self.name, admin_password=admin_password
				)
			],
			"install_app": [
				"bench --site {site_name} install-app {app_name}".format(
					site_name=self.name, app_name=app_name
				)
			],
			"uninstall_app": [
				"bench --site {site_name} uninstall-app {app_name} --yes".format(
					site_name=self.name, app_name=app_name
				)
			],
			"drop_site": [
				"bench drop-site {site_name} --root-password {mysql_password}".format(
					site_name=self.name, mysql_password=mysql_password
				)
			],
		}
		frappe.enqueue(
			"bench_manager.bench_manager.utils.run_command",
			commands=commands[caller],
			doctype=self.doctype,
			key=key,
			docname=self.name,
		)
		return "executed"


@frappe.whitelist()
def get_installable_apps(doctype, docname):
	verify_whitelisted_call()
	app_list_file = "apps.txt"
	with open(app_list_file, "r") as f:
		apps = f.read().split("\n")
	installed_apps = frappe.get_doc(doctype, docname).app_list.split("\n")
	installable_apps = set(apps) - set(installed_apps)
	return [x for x in installable_apps]


@frappe.whitelist()
def get_removable_apps(doctype, docname):
	verify_whitelisted_call()
	removable_apps = frappe.get_doc(doctype, docname).app_list.split("\n")
	removable_apps.remove("frappe")
	return removable_apps


@frappe.whitelist()
def pass_exists(doctype, docname=""):
	verify_whitelisted_call()
	# return string convention 'TT',<root_password>,<admin_password>
	ret = {"condition": "", "root_password": "", "admin_password": ""}
	common_site_config_path = "common_site_config.json"
	with open(common_site_config_path, "r") as f:
		common_site_config_data = json.load(f)

	ret["condition"] += "T" if common_site_config_data.get("root_password") else "F"
	ret["root_password"] = common_site_config_data.get("root_password")

	ret["condition"] += "T" if common_site_config_data.get("admin_password") else "F"
	ret["admin_password"] = common_site_config_data.get("admin_password")

	if docname == "":  # Prompt reached here on new-site
		return ret

	site_config_path = docname + "/site_config.json"
	with open(site_config_path, "r") as f:
		site_config_data = json.load(f)
	# FF FT TF
	if ret["condition"][1] == "F":
		ret["condition"] = (
			ret["condition"][0] + "T" if site_config_data.get("admin_password") else "F"
		)
		ret["admin_password"] = site_config_data.get("admin_password")
	else:
		if site_config_data.get("admin_password"):
			ret["condition"] = ret["condition"][0] + "T"
			ret["admin_password"] = site_config_data.get("admin_password")
	return ret


@frappe.whitelist()
def verify_password(site_name, mysql_password):
	verify_whitelisted_call()
	try:
		db = pymysql.connect(
			host=frappe.conf.db_host or "localhost", user="root", passwd=mysql_password
		)
		db.close()
	except Exception as e:
		print(e)
		frappe.throw("MySQL password is incorrect")
	return "console"


@frappe.whitelist()
def create_site(site_name, install_erpnext, mysql_password, admin_password, key):
	verify_whitelisted_call()
	commands = [
		"bench new-site --mariadb-root-password {mysql_password} --admin-password {admin_password} --no-mariadb-socket {site_name}".format(
			site_name=site_name, admin_password=admin_password, mysql_password=mysql_password
		)
	]
	if install_erpnext == "true":
		with open("apps.txt", "r") as f:
			app_list = f.read()
		if "erpnext" not in app_list:
			commands.append("bench get-app erpnext")
		commands.append(
			"bench --site {site_name} install-app erpnext".format(site_name=site_name)
		)
	frappe.enqueue(
		"bench_manager.bench_manager.utils.run_command",
		commands=commands,
		doctype="Bench Settings",
		key=key,
	)
	all_sites = safe_decode(check_output("ls")).strip("\n").split("\n")
	while site_name not in all_sites:
		time.sleep(2)
		print("waiting for site creation...")
		all_sites = safe_decode(check_output("ls")).strip("\n").split("\n")
	doc = frappe.get_doc(
		{"doctype": "Site", "site_name": site_name, "app_list": "frappe", "developer_flag": 1}
	)
	doc.insert()
	frappe.db.commit()
