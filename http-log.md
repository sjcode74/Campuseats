## Request 1: Get a single post

**Command:**
```
curl -i https://jsonplaceholder.typicode.com/posts/1
```

**Response:**
```
HTTP/1.1 200 OK
Date: Mon, 24 Aug 2026 05:05:24 GMT
Content-Type: application/json; charset=utf-8
Content-Length: 292
Connection: keep-alive
...
{
  "userId": 1,
  "id": 1,
  "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
  "body": "quia et suscipit\nsuscipit recusandae consequuntur expedita et cum\nreprehenderit molestiae ut ut quas totam\nnostrum rerum est autem sunt rem eveniet architecto"
}
```

**Note:** 200 OK means the request succeeded and the server found the resource. Content-Type application/json; charset=utf-8 means the response body is JSON text.


## Request 2: Get all posts

**Command:**
```
curl -i https://jsonplaceholder.typicode.com/posts
```

**Response:**
```
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Transfer-Encoding: chunked
...

[
  {
    "userId": 1,
    "id": 1,
    "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
    "body": "quia et suscipit..."
  },
  {
    "userId": 1,
    "id": 2,
    "title": "qui est esse",
    "body": "est rerum tempore vitae..."
  }
  ... (100 posts total, truncated for brevity)
]
```

**Note:** 200 OK means the request succeeded and returned the full collection. Content-Type application/json means it's a JSON array of post objects. Notice this response uses `Transfer-Encoding: chunked` instead of `Content-Length`, since the server didn't know the total size upfront.


## Request 3: Get a single user

**Command:**
```
curl -i https://jsonplaceholder.typicode.com/users/3
```

**Response:**
```
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Content-Length: 520
Connection: keep-alive
Cache-Control: max-age=43200
cf-cache-status: MISS
...

{
  "id": 3,
  "name": "Clementine Bauch",
  "username": "Samantha",
  "email": "Nathan@yesenia.net",
  "address": {
    "street": "Douglas Extension",
    "suite": "Suite 847",
    "city": "McKenziehaven",
    "zipcode": "59590-4157",
    "geo": {
      "lat": "-68.6102",
      "lng": "-47.0653"
    }
  },
  "phone": "1-463-123-4447",
  "website": "ramiro.info",
  "company": {
    "name": "Romaguera-Jacobson",
    "catchPhrase": "Face to face bifurcated interface",
    "bs": "e-enable strategic applications"
  }
}
```

**Note:** 200 OK means the request succeeded and the user with id=3 was found. Content-Type application/json means the body is a single JSON object (not an array, since we requested one specific user).

## Request 4: Get comments filtered by postId

**Command:**
```
curl -i "https://jsonplaceholder.typicode.com/comments?postId=1"
```

**Response:**
```
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Transfer-Encoding: chunked
Connection: keep-alive
cf-cache-status: REVALIDATED
...

[
  {
    "postId": 1,
    "id": 1,
    "name": "id labore ex et quam laborum",
    "email": "Eliseo@gardner.biz",
    "body": "laudantium enim quasi est quidem magnam voluptate ipsam eos..."
  },
  {
    "postId": 1,
    "id": 2,
    "name": "quo vero reiciendis velit similique earum",
    "email": "Jayne_Kuhic@sydney.com",
    "body": "est natus enim nihil est dolore omnis voluptatem numquam..."
  }
  ... (5 comments total, all with postId=1)
]
```

**Note:** 200 OK means the request succeeded. The `?postId=1` query parameter filtered results server-side, returning only the 5 comments belonging to post 1, instead of all 500 comments. Content-Type application/json means the body is a JSON array.


## Request 5: Get a non-existent post (deliberate failure)

**Command:**
```
curl -i https://jsonplaceholder.typicode.com/posts/99999
```

**Response:**
```
HTTP/1.1 404 Not Found
Content-Type: application/json; charset=utf-8
Content-Length: 2
Connection: keep-alive
cf-cache-status: EXPIRED
...

{}
```

**Note:** 404 Not Found means the server understood the request but could not find a resource with id=99999, since only posts 1-100 exist. Content-Type application/json is still returned even for the error, but the body is an empty object `{}` since there's no data to return.