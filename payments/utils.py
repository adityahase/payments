# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

import frappe

MAX_PAGES = 10
PAGINATION_LIMIT = 100
MAX_LIMIT = MAX_PAGES * PAGINATION_LIMIT


class StripeHelper:
	stripe_name_field = "name"  # Default field to map with Stripe ID
	document_name_field = "id"  # Stripe field to map with Document name

	@classmethod
	def stripe(cls):
		return frappe.get_doc("Stripe Settings").get_stripe()

	@classmethod
	def front_fill(cls):
		if frappe.get_all(cls.doctype):
			# We only need to fill till the latest entry
			ending_before = frappe.get_all(
				cls.doctype, order_by="creation DESC", limit=1, pluck=cls.stripe_name_field
			)[0]
			print("Ending Before", frappe.get_all(cls.doctype, {"name": ending_before}, ["name", "creation"]))
			list = cls.stripe_object.list(limit=PAGINATION_LIMIT, ending_before=ending_before)
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
		list = cls.stripe_object.list(limit=PAGINATION_LIMIT, starting_after=starting_after)
		cls._fill(list.auto_paging_iter())

	@classmethod
	def _fill(cls, iterator):
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

			if index >= MAX_LIMIT - 1:
				print(f"Reached max limit of {MAX_LIMIT}. Stopping.")
				break
