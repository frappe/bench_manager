from . import __version__ as app_version

app_name = "bench_manager"
app_title = "Bench Manager"
app_publisher = "Frappe"
app_description = "GUI for using bench commands "
app_icon = "fa fa-gamepad"
app_color = "grey"
app_email = "info@frappe.io"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/bench_manager/css/bench_manager.css"
app_include_js = "/assets/bench_manager/js/bench_manager.js"

# include js, css files in header of web template
# web_include_css = "/assets/bench_manager/css/bench_manager.css"
# web_include_js = "/assets/bench_manager/js/bench_manager.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "bench_manager.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "bench_manager.install.before_install"
# after_install = "bench_manager.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "bench_manager.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"bench_manager.tasks.all"
# 	],
# 	"daily": [
# 		"bench_manager.tasks.daily"
# 	],
# 	"hourly": [
# 		"bench_manager.tasks.hourly"
# 	],
# 	"weekly": [
# 		"bench_manager.tasks.weekly"
# 	]
# 	"monthly": [
# 		"bench_manager.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "bench_manager.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "bench_manager.event.get_events"
# }
