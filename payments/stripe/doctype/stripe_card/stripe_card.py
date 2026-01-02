# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from payments.utils import StripeHelper, get_country, unscrub


class StripeCard(Document, StripeHelper):
	stripe_object = StripeHelper.stripe().PaymentMethod
	doctype = "Stripe Card"

	@classmethod
	def create(cls, method):
		if card := method.get("card", {}):
			doc = frappe.get_doc(
				{
					"doctype": "Stripe Card",
					"name": method.id,
					"customer": method.customer,
					"brand": BRAND_MAP.get(card.display_brand, "New"),
					"country": get_country(card.country),
					"expiry_month": card.exp_month,
					"expiry_year": card.exp_year,
					"funding": unscrub(card.funding),
					"address_line_1_check": unscrub(card.checks.address_line1_check),
					"cvc_check": unscrub(card.checks.cvc_check),
					"address_postal_code_check": unscrub(card.checks.address_postal_code_check),
					"address_city": method.billing_details.address.city,
					"address_country": get_country(method.billing_details.address.country),
					"address_postal_code": method.billing_details.address.postal_code,
					"address_state": method.billing_details.address.state,
					"payload": cls.serialize(method),
				}
			).insert()
			doc.update_creation(method.created)


BRAND_MAP = {
	"american_express": "American Express",
	"cartes_bancaires": "Cartes Bancaires",
	"diners_club": "Diners Club",
	"discover": "Discover",
	"eftpos_australia": "EFTPOS Australia",
	"interac": "Interac",
	"jcb": "JCB",
	"mastercard": "Mastercard",
	"union_pay": "Union Pay",
	"visa": "Visa",
	"other": "Other",
}
