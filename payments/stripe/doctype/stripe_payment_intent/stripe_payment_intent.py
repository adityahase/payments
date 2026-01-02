# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from payments.utils import StripeHelper, unscrub


class StripePaymentIntent(Document, StripeHelper):
	stripe_object = StripeHelper.stripe().PaymentIntent
	doctype = "Stripe Payment Intent"

	@classmethod
	def create(cls, intent):
		doc = frappe.get_doc(
			{
				"doctype": "Stripe Payment Intent",
				"name": intent.id,
				"status": unscrub(intent.status),
				"customer": intent.customer,
				"amount": intent.amount / 100,
				"description": intent.description,
				"currency": intent.currency.upper(),
				"payload": cls.serialize(intent),
			}
		).insert()
		doc.update_creation(intent.created)
