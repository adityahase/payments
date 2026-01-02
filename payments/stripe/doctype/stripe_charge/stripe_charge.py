# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from payments.utils import StripeHelper, unscrub


class StripeCharge(Document, StripeHelper):
	stripe_object = StripeHelper.stripe().Charge
	doctype = "Stripe Charge"

	@classmethod
	def create(cls, charge):
		doc = frappe.get_doc(
			{
				"doctype": "Stripe Charge",
				"name": charge.id,
				"status": unscrub(charge.status),
				"payment_intent": charge.payment_intent,
				"card": charge.payment_method,
				"refunded": charge.refunded,
				"dispute": charge.dispute,
				"failure_code": unscrub(charge.failure_code),
				"failure_message": charge.failure_message,
				"advice_code": unscrub(charge.outcome.advice_code),
				"network_status": unscrub(charge.outcome.network_status),
				"network_advice_code": charge.outcome.network_advice_code,
				"network_decline_code": charge.outcome.network_decline_code,
				"type": unscrub(charge.outcome.type),
				"risk_level": unscrub(charge.outcome.risk_level),
				"reason": unscrub(charge.outcome.reason),
				"seller_message": charge.outcome.seller_message,
				"payload": cls.serialize(charge),
			}
		).insert(ignore_links=True)  # We cannot fetch all linked PaymentIntent without breaking backfill
		doc.update_creation(charge.created)
