# CampusEats — SOAP Partner Integration

## Team
Team Id: 
Members name : Anshu Mala 20252651010 (Leader)
               Sanika Jain 20252651046
               Annu Mishra 20252651009
               Mritunjay Maurya 20252651037

## Context

CampusEats integrates with **PayFlex**, an external payment gateway, to process
student payments for orders. We integrate the `charge` operation via SOAP,
even though the rest of CampusEats is built on REST, for three reasons.

First, payment processing needs a **strong, formal contract** — the gateway
publishes a WSDL that precisely defines every field, type, and fault a client
must handle, which matters far more here than for a simple resource lookup.
Second, financial transactions require **message-level security**: SOAP's
WS-Security standard lets us sign and encrypt the payment payload itself
(not just the transport), so the message stays protected even if it passes
through intermediaries. Third, payment gateways commonly need to guarantee
**transactional reliability** — knowing definitively whether a charge
succeeded, failed, or is still pending — which SOAP's mature WS-* standards
(WS-ReliableMessaging, WS-AtomicTransaction) are built to support, unlike
plain REST/HTTP.

The operation we integrate: **charge(orderId, amount, cardToken) → paymentId, status**