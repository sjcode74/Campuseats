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


## HTTP binding

The SOAP request is carried as an HTTP POST to the endpoint defined in the
WSDL's service/port section. Below is the raw HTTP request block:

```
POST /soap/payment HTTP/1.1
Host: api.payflex.example.com
Content-Type: text/xml; charset=utf-8
Content-Length: 512
SOAPAction: "http://payflex.example.com/payment/charge"

<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:pay="http://payflex.example.com/payment/wsdl">
  <soap:Header>
    <pay:Credentials>
      <pay:apiKey>CAMPUSEATS_9F3A21B7</pay:apiKey>
      <pay:merchantId>CAMPUSEATS_UNIV01</pay:merchantId>
    </pay:Credentials>
  </soap:Header>
  <soap:Body>
    <pay:ChargeRequest>
      <pay:orderId>ORD-58213</pay:orderId>
      <pay:amount>249.00</pay:amount>
      <pay:currency>INR</pay:currency>
      <pay:cardToken>tok_4f8e2a9c7b1d</pay:cardToken>
    </pay:ChargeRequest>
  </soap:Body>
</soap:Envelope>
```