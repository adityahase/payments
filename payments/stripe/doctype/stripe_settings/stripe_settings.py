# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

# import frappe
import stripe
from frappe.model.document import Document


class StripeSettings(Document):
	def get_stripe(self):
		key = self.get_password("api_key")
		stripe.api_key = key
		return stripe
