# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

import json
from datetime import datetime, timezone

import frappe
from frappe.utils import convert_utc_to_system_timezone


class StripeHelper:
	stripe_name_field = "name"  # Default field to map with Stripe ID
	document_name_field = "id"  # Stripe field to map with Document name

	@classmethod
	def settings(cls):
		return frappe.get_doc("Stripe Settings")

	@classmethod
	def stripe(cls):
		if frappe.flags.in_install:
			return frappe._dict()
		return cls.settings().get_stripe()

	@classmethod
	def front_fill(cls):
		if frappe.get_all(cls.doctype):
			# We only need to fill till the latest entry
			ending_before = frappe.get_all(
				cls.doctype, order_by="creation DESC", limit=1, pluck=cls.stripe_name_field
			)[0]
			print("Ending Before", frappe.get_all(cls.doctype, {"name": ending_before}, ["name", "creation"]))
			list = cls.stripe_object.list(limit=cls.settings().limit, ending_before=ending_before)
			cls._fill(list.auto_paging_iter())
		else:
			print("No existing entries found. Skipping front fill.")
			return

	@classmethod
	def back_fill(cls):
		if frappe.get_all(cls.doctype):
			# Start filling the entries older than the oldest entry
			starting_after = frappe.get_all(
				cls.doctype, order_by="creation ASC", limit=1, pluck=cls.stripe_name_field
			)[0]
		else:
			starting_after = None
		print("Starting After", frappe.get_all(cls.doctype, {"name": starting_after}, ["name", "creation"]))
		list = cls.stripe_object.list(limit=cls.settings().limit, starting_after=starting_after)
		cls._fill(list.auto_paging_iter())

	@classmethod
	def _fill(cls, iterator):
		settings = cls.settings()
		max_limit = settings.limit * settings.max_pages
		for index, entry in enumerate(iterator):
			try:
				if frappe.db.exists(cls.doctype, entry.get(cls.document_name_field)):
					print(f"Skipping {cls.doctype} - {index} - {entry.get(cls.document_name_field)}")
					continue

				print(f"Inserting {cls.doctype} - {index} - {entry.get(cls.document_name_field)}")
				cls.create(entry)
				frappe.db.commit()
			except Exception as e:
				frappe.log_error(f"{cls.doctype} Insertion Error")
				frappe.db.rollback()
				print(f"Error inserting {cls.doctype} - {index} - {entry.get(cls.document_name_field)}", e)
				raise

			if index >= max_limit - 1:
				print(f"Reached max limit of {max_limit}. Stopping.")
				break

	@classmethod
	def fill_everything(cls, **kwargs):
		list = cls.stripe_object.list(limit=cls.settings().limit, **kwargs)
		cls._fill(list.auto_paging_iter())

	def _get_system_time_from_timestamp(self, timestamp):
		utc = datetime.fromtimestamp(timestamp, tz=timezone.utc)
		return convert_utc_to_system_timezone(utc)

	def update_creation(self, timestamp):
		creation_system = self._get_system_time_from_timestamp(timestamp)
		frappe.db.set_value(
			self.doctype,
			self.name,
			{"creation": creation_system, "modified": creation_system},
			update_modified=False,
		)

	@classmethod
	def serialize(cls, object):
		return json.dumps(object, default=str, indent=4)


def unscrub(str):
	return frappe.unscrub(str or "")


def get_country(code):
	return frappe.db.get_value("Country", {"code": (code or "").lower()})
