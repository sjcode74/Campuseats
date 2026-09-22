# CampusEats Order Service - Assignment 4 Notes

## A4. Resource Table

| Method | URL | What it does | Success | Failure |
|---|---|---|---|---|
| POST | `/orders` | Creates a new order | 201 Created | 400, 503 |
| GET | `/orders` | Gets orders, optionally filtered by status | 200 OK | 400 |
| GET | `/orders/{orderId}` | Gets one order by ID | 200 OK | 404 |
| POST | `/orders/{orderId}/cancellation` | Cancels an order | 200 OK | 400, 404, 409, 422 |

## A5. Hard Mapping Choice

In the SOAP service, an operation such as `cancelOrder` was mapped to the REST endpoint:

`POST /orders/{orderId}/cancellation`

The action is represented as a sub-resource called `cancellation` instead of using a verb such as `/cancelOrder`.

This keeps the REST URL resource-oriented while still representing a state-changing operation.

---

## D3. Dependency Failure Fallback

The Order Service depends on the Payment Service when creating an order.

If the Payment Service is unreachable after timeout and retry attempts, the Order Service returns:

`503 Service Unavailable`

The order is not created in this situation.

This fallback was chosen because creating an order without confirming payment could leave the system in an inconsistent state. Returning 503 allows the client to retry the request later using the same `Idempotency-Key`.

---

# Assignment Questions

## 1. WSDL Lines vs OpenAPI Lines

The WSDL contains more lines than the OpenAPI specification because WSDL describes SOAP operations, messages, bindings, XML types and service details in a more XML-heavy format.

OpenAPI represents REST resources, HTTP methods, parameters, request bodies and responses more directly.

Therefore, the OpenAPI specification can be shorter and easier to read for this REST service.

---

## 2. SOAP Fault vs REST Problem Response

A SOAP service can return an error using `soap:Fault`.

For example:

`soap:Fault`

In this REST service, the same type of failure is represented using an HTTP status code and a common problem response:

```json
{
  "type": "about:blank",
  "title": "Not Found",
  "status": 404,
  "detail": "Order not found"
}
