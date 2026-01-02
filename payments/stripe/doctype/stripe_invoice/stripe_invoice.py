# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from payments.utils import StripeHelper, unscrub


class StripeInvoice(Document, StripeHelper):
	stripe_object = StripeHelper.stripe().InvoicePayment
	doctype = "Stripe Invoice"
	stripe_name_field = "invoice_payment"
	document_name_field = "invoice"

	@classmethod
	def create(cls, invoice):
		doc = frappe.get_doc(
			{
				"doctype": "Stripe Invoice",
				"name": invoice.invoice,
				"status": unscrub(invoice.status),
				"type": unscrub(invoice.payment.type),
				"charge": invoice.payment.get("charge"),
				"payment_intent": invoice.payment.get("payment_intent"),
				"invoice_payment": invoice.id,
				"payload": cls.serialize(invoice),
			}
		).insert(ignore_links=True)
		doc.update_creation(invoice.created)
