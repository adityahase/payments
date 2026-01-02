# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt
import frappe


def back_fill():
	from payments.stripe.doctype.stripe_charge.stripe_charge import StripeCharge

	StripeCharge.back_fill()


def front_fill():
	from payments.stripe.doctype.stripe_charge.stripe_charge import StripeCharge

	StripeCharge.front_fill()


def fill():
	front_fill()
	back_fill()


def cleanup():
	frappe.db.delete("Stripe Charge")
	frappe.db.delete("Stripe Card")
