CampusEats Order Service - Assignment 5 Notes

Team Information


Roll No.

Name: Sanika Jain 20252651046
      Anshu Mala (Leader)20252651010
      Annu Mishra 20252651009
      Mritunjay Maurya 20252651035

A1. HTTP Method Map

Method

URL

Meaning

Success

POST

/orders

Creates a new order

201 Created

GET

/orders

Reads the order collection; supports filter, sort and pagination

200 OK

GET

/orders/{orderId}

Reads one order

200 OK

PATCH

/orders/{orderId}

Partially modifies an order

200 OK

DELETE

/orders/{orderId}

Removes an order

204 No Content

POST

/orders/{orderId}/cancellation

Performs the non-CRUD cancellation action as a sub-resource

200 OK

The URLs use nouns/resources rather than action verbs such as /cancelOrder.

A2. Non-CRUD Actions

The cancellation action is represented as:

POST /orders/{orderId}/cancellation

This keeps the URL resource-oriented while representing a state-changing operation.

A3. Safe and Idempotent Operations

GET /orders is safe and idempotent.

GET /orders/{orderId} is safe and idempotent.

POST /orders is not safe or naturally idempotent, so the service uses Idempotency-Key to make a retry return the original result without creating duplicate work.

PATCH and DELETE are state-changing operations. PATCH uses If-Match to prevent lost updates; DELETE is intended to be idempotent for the same resource state.

GET endpoints do not change server state.

A4. Filtering, Sorting and Pagination

GET /orders remains a pure read. Query parameters are used instead of putting filtering or sorting instructions in the URL path.

Examples:

GET /orders?status=placed

GET /orders?sort=-createdAt

GET /orders?page=1&limit=10

Supported sort values are createdAt, -createdAt, totalAmount, -totalAmount, orderId, and -orderId.

A5. OPTIONS and Method Override

OPTIONS /orders returns 204 No Content with:

Allow: GET, POST, OPTIONS

OPTIONS /orders/{orderId} returns:

Allow: GET, PATCH, DELETE, OPTIONS

The service also accepts the documented X-HTTP-Method-Override fallback for PUT, PATCH and DELETE when a constrained client cannot send those methods directly. The normal API should use the real HTTP method.

A6. Complete HTTP Request and Response Example

HTTP version: HTTP/1.1

Request

POST /orders HTTP/1.1
Host: localhost:5000
Content-Type: application/json
Accept: application/json
Authorization: Bearer demo-token
Idempotency-Key: order-1001

{"userId":1,"restaurantId":10,"paymentMethod":"card","items":[{"menuItemId":5,"quantity":2,"price":100}]}

Response

HTTP/1.1 201 Created
Content-Type: application/json
Location: /orders/1
X-Content-Type-Options: nosniff
Strict-Transport-Security: max-age=31536000; includeSubDomains

{"orderId":1,"userId":1,"restaurantId":10,"items":[{"menuItemId":5,"quantity":2,"price":100}],"totalAmount":200,"status":"pending_payment","createdAt":"..."}

B1. Content Negotiation

JSON request bodies use Content-Type: application/json. The service supports JSON responses and checks the Accept header. If the client requests an unsupported response type, the service returns 406 Not Acceptable.

B2. Status Codes

Situation

Status

Create resource

201 Created + Location

Read resource

200 OK

Delete resource

204 No Content

Malformed request

400 Bad Request

Missing resource

404 Not Found

State conflict

409 Conflict

Domain refusal

422 Unprocessable Entity

Unsupported Accept type

406 Not Acceptable

Missing Bearer token

401 Unauthorized

Rate limit exceeded

429 Too Many Requests

Payment dependency unavailable

503 Service Unavailable

If-Match mismatch

412 Precondition Failed

B3. Authorization

Protected state-changing endpoints require:

Authorization: Bearer <token>

A missing or empty Bearer token returns 401 Unauthorized. No real authentication system is required for this assignment.

B4. Caching and ETag

GET /orders/{orderId} returns an ETag and Cache-Control: private, max-age=60.

The ETag is calculated from the current JSON representation. When the resource representation changes, the ETag changes.

B5. Rate Limiting

The service maintains a per-client in-memory request budget. Responses include X-RateLimit-Limit and X-RateLimit-Remaining. When the budget is exhausted, the service returns 429 Too Many Requests and Retry-After.

B6. CORS

Responses include Access-Control-Allow-Origin. OPTIONS responses also expose allowed methods and headers for browser preflight requests.

B7. Security Headers

Responses include:

X-Content-Type-Options: nosniff

Strict-Transport-Security: max-age=31536000; includeSubDomains

C1. Conditional GET

A client can send:

If-None-Match: <current-etag>

If the supplied ETag matches, the service returns 304 Not Modified with no response body.

C2. Conditional Write

PATCH /orders/{orderId} requires If-Match. If the supplied ETag does not match the current resource ETag, the service returns 412 Precondition Failed and does not apply the update.

C3. Idempotency-Key

POST /orders accepts Idempotency-Key. The same key returns the previously created order instead of performing the create/payment work again.

Without idempotency protection, a client retry after a timeout could cause duplicate orders or duplicate payment attempts.

C4. Safe-Retry Plan

Endpoint

Safe?

Naturally Idempotent?

Protection / Retry Rule

GET /orders

Yes

Yes

Safe to retry; use normal GET retry handling

GET /orders/{orderId}

Yes

Yes

Safe to retry; If-None-Match can reduce payload

POST /orders

No

No

Use Idempotency-Key so a retry returns the original result

PATCH /orders/{orderId}

No

Not guaranteed

Use If-Match to avoid overwriting a changed resource

DELETE /orders/{orderId}

No

Yes by intended resource semantics

Retry only when the client can handle 404 after the first successful deletion

POST /orders/{orderId}/cancellation

No

Not naturally

Repeating a successful cancellation reaches the already-cancelled state and returns the documented conflict response

D1. Curl Transcript Plan

The final curl-transcript.txt records curl -v output for:

Create order → 201 Created + Location.

Repeat same create with the same Idempotency-Key → original order/result.

Conditional GET with If-None-Match → 304 Not Modified.

Conditional PATCH with a wrong If-Match → 412 Precondition Failed.

Invalid request → 400 Bad Request.

Unknown order → 404 Not Found.

Protected endpoint without Authorization → 401 Unauthorized.

D2. Header Table

Endpoint

Request headers

Response headers

POST /orders

Content-Type, Accept, Authorization, Idempotency-Key

Location, rate-limit headers, security/CORS headers

GET /orders

Accept

rate-limit headers, security/CORS headers

GET /orders/{id}

Accept, If-None-Match

ETag, Cache-Control, rate-limit/security/CORS headers

PATCH /orders/{id}

Content-Type, Accept, Authorization, If-Match

ETag, Cache-Control, rate-limit/security/CORS headers

POST /orders/{id}/cancellation

Content-Type, Accept, Authorization

ETag, Cache-Control, rate-limit/security/CORS headers

DELETE /orders/{id}

Authorization

Cache-Control, rate-limit/security/CORS headers

OPTIONS

Origin, Access-Control-Request-Method, Access-Control-Request-Headers

Allow and CORS headers

D3. Dependency Failure Fallback

The Order Service depends on the Payment Service when creating an order.

If the Payment Service is unreachable after timeout/retry attempts, the Order Service returns 503 Service Unavailable and does not create the order. The client can retry later using the same Idempotency-Key.

Assignment Questions

1. WSDL Lines vs OpenAPI Lines

The WSDL contains more lines than the OpenAPI specification because WSDL describes SOAP operations, messages, bindings, XML types and service details in a more XML-heavy format.

OpenAPI represents REST resources, HTTP methods, parameters, request bodies and responses more directly.

Therefore, the OpenAPI specification can be shorter and easier to read for this REST service.

2. SOAP Fault vs REST Problem Response

A SOAP service can return an error using soap:Fault.

In this REST service, the same type of failure is represented using an HTTP status code and a common problem response:

{
  "type": "about:blank",
  "title": "Not Found",
  "status": 404,
  "detail": "Order not found"
}

3. Safe and Idempotent Difference

Safe means the request is read-only and does not intentionally change server state. Idempotent means repeating the same request has the same intended effect as making it once.

GET is both safe and idempotent. A state-changing request such as POST is not naturally safe or idempotent, so Idempotency-Key is used for order creation.

4. Why Idempotency-Key Matters

If the client times out after the server has already created an order, the client may retry. Without an idempotency key, the retry could create another order or trigger another payment attempt. The key lets the server recognize the retry and return the original result.

5. ETag and If-None-Match

The ETag identifies the current representation of an order. A client sends it back in If-None-Match. If it still matches, the server returns 304 Not Modified without sending the representation again.

6. If-Match and 412

If-Match is used for conditional updates. The server compares the supplied ETag with the current ETag. A mismatch means another change has occurred, so the server returns 412 Precondition Failed rather than overwriting the newer representation.

7. 429 and Retry-After

429 Too Many Requests indicates that the client has exceeded the request budget. Retry-After tells the client how long to wait before trying again.

8. Dependency Failure

The Payment Service is a required dependency for order creation. If it remains unavailable after the configured retry/timeout behavior, the Order Service returns 503 Service Unavailable and does not create the order.