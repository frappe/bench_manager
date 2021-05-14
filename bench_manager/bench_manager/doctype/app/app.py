# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappé and contributors
# For license information, please see license.txt


import os
import re
import shlex
import time
from subprocess import PIPE, STDOUT, Popen, check_output

import frappe
from bench_manager.bench_manager.utils import (
	safe_decode,
	verify_whitelisted_call,
)
from frappe.model.document import Document


class App(Document):
	app_info_fields = [
		"app_title",
		"app_description",
		"app_publisher",
		"app_email",
		"app_icon",
		"app_color",
		"app_license",
	]

	def validate(self):
		if self.get("__islocal"):
			if self.developer_flag == 0:
				frappe.throw("Creation of new apps is not supported at the moment!")
			self.developer_flag = 0
			app_data_path = os.path.join(
				"..",
				"apps",
				self.app_name,
				"{app_name}.egg-info".format(app_name=self.app_name),
				"PKG-INFO",
			)
			while not os.path.isfile(app_data_path):
				time.sleep(2)
			self.update_app_details()
		else:
			if self.developer_flag == 0:
				self.update_app_details()

	def onload(self):
		self.update_app_details()

	def get_attr(self, varname):
		return getattr(self, varname)

	def set_attr(self, varname, varval):
		return setattr(self, varname, varval)

	def after_command(self, commands=None):
		frappe.publish_realtime("Bench-Manager:reload-page")

	def on_trash(self):
		if self.developer_flag == 0:
			frappe.throw("Not allowed!")
		else:
			apps_file = "apps.txt"
			with open(apps_file, "r") as f:
				apps = f.readlines()
			try:
				apps.remove(self.app_name)
			except:
				try:
					apps.remove(self.app_name + "\n")
				except:
					pass
			os.remove(apps_file)
			with open(apps_file, "w") as f:
				f.writelines(apps)
			if self.app_name != "":
				check_output(shlex.split("rm -r ../apps/{app_name}".format(app_name=self.app_name)))

	def update_app_details(self):
		pkg_info_file = os.path.join(
			"..",
			"apps",
			self.app_name,
			"{app_name}.egg-info".format(app_name=self.app_name),
			"PKG-INFO",
		)
		if os.path.isfile(pkg_info_file):
			app_data_path = pkg_info_file
			with open(app_data_path, "r") as f:
				app_data = f.readlines()
			app_data = frappe.as_unicode("".join(app_data)).split("\n")
			if "" in app_data:
				app_data.remove("")
			app_data = [x + "\n" for x in app_data]
			for data in app_data:
				if "Version:" in data:
					self.version = "".join(re.findall("Version: (.*?)\\n", data))
				elif "Summary:" in data:
					self.app_description = "".join(re.findall("Summary: (.*?)\\n", data))
				elif "Author:" in data:
					self.app_publisher = "".join(re.findall("Author: (.*?)\\n", data))
				elif "Author-email:" in data:
					self.app_email = "".join(re.findall("Author-email: (.*?)\\n", data))
			self.app_title = self.app_name
			self.app_title = self.app_title.replace("-", " ")
			self.app_title = self.app_title.replace("_", " ")
			if os.path.isdir(os.path.join("..", "apps", self.app_name, ".git")):
				self.current_git_branch = safe_decode(
					check_output(
						"git rev-parse --abbrev-ref HEAD".split(),
						cwd=os.path.join("..", "apps", self.app_name),
					)
				).strip("\n")
				self.is_git_repo = True
			else:
				self.current_git_branch = None
				self.is_git_repo = False
		else:
			frappe.throw(
				"Hey developer, the app you're trying to create an \
				instance of doesn't actually exist. You could consider setting \
				developer flag to 0 to actually create the app"
			)

	@frappe.whitelist()
	def pull_rebase(self, key, remote):
		remote, branch_name = remote.split("/")
		self.console_command(
			key=key, caller="pull-rebase", branch_name=branch_name, remote=remote
		)

	@frappe.whitelist()
	def console_command(self, key, caller, branch_name=None, remote=None, commit_msg=None):
		commands = {
			"git_init": ["git init", "git add .", "git commit -m 'Initial Commit'"],
			"switch_branch": ["git checkout {branch_name}".format(branch_name=branch_name)],
			"new_branch": ["git branch {branch_name}".format(branch_name=branch_name)],
			"delete_branch": ["git branch -D {branch_name}".format(branch_name=branch_name)],
			"git_fetch": ["git fetch --all"],
			"track-remote": [
				"git checkout -b {branch_name} -t {remote}".format(
					branch_name=branch_name, remote=remote
				)
			],
			"pull-rebase": [
				"git pull --rebase {remote} {branch_name}".format(
					branch_name=branch_name, remote=remote
				)
			],
			"commit": [
				"git add .",
				'git commit -m "{commit_msg}"'.format(commit_msg=commit_msg),
			],
			"stash": ["git add .", "git stash"],
			"apply-stash": ["git stash apply"],
		}
		frappe.enqueue(
			"bench_manager.bench_manager.utils.run_command",
			commands=commands[caller],
			cwd=os.path.join("..", "apps", self.name),
			doctype=self.doctype,
			key=key,
			docname=self.name,
		)


@frappe.whitelist()
def get_branches(doctype, docname, current_branch):
	verify_whitelisted_call()
	app_path = os.path.join("..", "apps", docname)  #'../apps/'+docname
	branches = (check_output("git branch".split(), cwd=app_path)).split()
	branches.remove("*")
	branches.remove(current_branch)
	return branches


@frappe.whitelist()
def get_remotes(docname):
	command = "git branch -r"
	remotes = (
		safe_decode(
			check_output(shlex.split(command), cwd=os.path.join("..", "apps", docname))
		)
		.strip("\n")
		.split("\n  ")
	)
	remotes = [remote for remote in remotes if "HEAD" not in remote]
	return remotes
