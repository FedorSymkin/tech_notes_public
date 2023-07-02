# Simple wallets API

Test payment system API for django learning purpose

## Overview
* REST API
* Every user has exacly 1 wallet with some currency
* There are 4 currencies in system: USD (base), EUR, CAD, CNY. Every currency has rate to base.
* Users can create operation of two types: put money to wallet and transfer money to another wallet (in any currency of system)
* Every operation has status which may be one of 4 values: draft, processing, accepted, failed
* Status of operation is controlled by external payment gateway using special API endpoint
* All operations and all changes of operation status are stored in history
* Operation contains info about wallet currency rate for the moment of creation for both source and destination wallets
* There is API endpoint for generating report of all operations and operation status changes related to specified wallet or specified username in specified pediod (period is optional, all time by default)
* There is API endpoint for generating report of all wallets
* Reports can be rendered in json or csv format

## Wallets balance and operations logic details
* When operation (transfer or put) is created, it is in status "draft" and wallets balance is not affected
* When transfer operation comes to status "processing", source wallet's balance is decreased. If source wallet of transfer operation doesn't have enouh money at that moment, operation is set to failed state, and cannot be continued later.
* When transfer operation comes to status "accepted", money of operation is credited to destination wallet.
* When transfer operation comes to status "failed", money of operation is rolled back to source wallet
* Operations may be done in any currency of system redgarless of source and destination wallet currency. Calculation of balance is implemented using rates to base currency (USD)
* Operation stores currency rates for both source and dest wallets and operation currency at the moment of creation. These rates (not actual) is used for calculations related to this operation.
* All collaborative changes of operation states and wallet balances are performed under transaction

### Protection from rate conditions during changes of operation status and wallets balance
* Operations status may be changed from external controller only by following rules:
	* draft -> processing
	* processing -> accepted
	* procedding -> failed
* Operation status cannot be set twice, e.q. "accepted -> accepted" is not allowed
* When operation status and wallet balance is changed, they are protected by row lock in DB

## API format
* Input data in request body: JSON 
* Output data in response: JSON or CSV for some endpoints

## API endpoints examples

### Create new user
`POST /users/new/`

Request data example:
```
{
    "username": "user4",
    "password": "pass4",
    "country": "Russia",
    "city": "Moscow",
    "currency": "EUR"
}
```

Response data example:
```
HTTP CODE: 201 CREATED
{
    "id": 4,
    "username": "user4",
    "country": "Russia",
    "city": "Moscow",
    "wallet": {
        "id": 4,
        "user": 4,
        "balance": "0.0000000",
        "currency": "EUR"
    }
}
```

### Get user data
`GET /users/<user_id>/` 

Response data example:
```
HTTP CODE: 200 OK
{
    "id": 4,
    "username": "user4",
    "country": "Russia",
    "city": "Moscow",
    "wallet": {
        "id": 4,
        "user": 4,
        "balance": "0.0000000",
        "currency": "EUR"
    }
}
```

### Get wallet data (balance, currency)
`GET /wallets/<wallet_id>/`

Response data example:
```
HTTP CODE: 200 OK
{
	"id": 4,
	"user": 4,
	"balance": "10.0000000",
	"currency": "EUR"
}
```

### Create put money operation
`POST /wallets/<wallet_id>/put_money/`

Request data example:
```
{
    "amount": 10.25,
    "currency": "USD"
}
```

Response data example with new operation details:
```
HTTP CODE: 201 CREATED
{
    "id": 8,
    "wallet_from": null,
    "wallet_to": 4,
    "amount": "10.2500000",
    "currency": "USD",
    "currency_rate_wallet_from": null,
    "currency_rate_operation": 1,
    "currency_rate_wallet_to": 1.5,
    "status": "draft"
}
```

### Create transfer money operation
`POST /wallets/<wallet_from>/put_money/`

Request data example:
```
{
    "wallet_to": 3,
    "amount": 10.25,
    "currency": "USD"
}
```

Response data example with new operation details:
```
HTTP CODE: 201 CREATED
{
    "id": 8,
    "wallet_from": 4,
    "wallet_to": 4,
    "amount": "10.2500000",
    "currency": "USD",
    "currency_rate_wallet_from": 0.75,
    "currency_rate_operation": 1,
    "currency_rate_wallet_to": 1.5,
    "status": "draft"
}
```

### Get operation details
`GET /operations/<operation_id>/`

Response data example with new operation details:
```
HTTP CODE: 200 OK
{
    "id": 8,
    "wallet_from": 4,
    "wallet_to": 4,
    "amount": "10.2500000",
    "currency": "USD",
    "currency_rate_wallet_from": 0.75,
    "currency_rate_operation": 1,
    "currency_rate_wallet_to": 1.5,
    "status": "processing"
}
```

### Set operation status (used by external payment gateway)
`PATCH /operations/<operation_id>/set_status/`

Request data example:
```
{
    "status": "accepted",
}
```

Response data example with new operation details:
```
HTTP CODE: 200 OK
{
    "operation": 8,
    "status": "accepted"
}
```

### Get report of wallet operations
`GET /wallets/<wallet_id>/operations/?date_from=YYYY-mm-dd&date_to=YYYY-mm-dd&format=<format>`

* date_from and date_to is optional
* format = json|csv is optional (default json)

Example of csv report:
```
datetime,new_status,operation.amount,operation.currency,operation.currency_rate_operation,operation.currency_rate_wallet_from,operation.currency_rate_wallet_to,operation.id,operation.status,operation.wallet_from,operation.wallet_to
2019-05-07T03:31:20.977000Z,failed,2000.0000000,USD,1.0000000,1.0000000,1.5000000,5,failed,1,2
2019-05-07T03:31:08.431000Z,draft,2000.0000000,USD,1.0000000,1.0000000,1.5000000,5,failed,1,2
2019-05-07T03:30:52.732000Z,failed,0.2500000,USD,1.0000000,1.0000000,1.5000000,4,failed,1,2
2019-05-07T03:30:39.606000Z,processing,0.2500000,USD,1.0000000,1.0000000,1.5000000,4,failed,1,2
2019-05-07T03:30:32.502000Z,draft,0.2500000,USD,1.0000000,1.0000000,1.5000000,4,failed,1,2
2019-05-07T03:29:23.894000Z,accepted,1.0000000,CAD,0.7500000,1.0000000,1.5000000,3,accepted,1,2
2019-05-07T03:29:07.613000Z,processing,1.0000000,CAD,0.7500000,1.0000000,1.5000000,3,accepted,1,2
2019-05-07T03:28:55.508000Z,draft,1.0000000,CAD,0.7500000,1.0000000,1.5000000,3,accepted,1,2
2019-05-07T03:28:29.935000Z,accepted,5.0000000,USD,1.0000000,1.5000000,1.0000000,2,accepted,2,1
2019-05-07T03:28:19.864000Z,processing,5.0000000,USD,1.0000000,1.5000000,1.0000000,2,accepted,2,1
2019-05-07T03:28:11.727000Z,draft,5.0000000,USD,1.0000000,1.5000000,1.0000000,2,accepted,2,1
2019-05-07T03:27:45.996000Z,accepted,5.0000000,USD,1.0000000,1.0000000,1.5000000,1,accepted,1,2
2019-05-07T03:27:35.618000Z,processing,5.0000000,USD,1.0000000,1.0000000,1.5000000,1,accepted,1,2
2019-05-07T03:27:17.431000Z,draft,5.0000000,USD,1.0000000,1.0000000,1.5000000,1,accepted,1,2
```	

fields description:

* `datetime` - datetime of operation status change (or creation)
* `new_status` - new_status
* `operation.amount` - amount on money in operation currency
* `operation.currency` - operation currency
* `operation.currency_rate_operation` - rate of operation currency to USD at the moment of operation creation
* `operation.currency_rate_wallet_from` - rate of source wallet currency (if present) to USD at the moment of operation creation
* `operation.currency_rate_wallet_to` - rate of destination wallet currency to USD at the moment of operation creation
* `operation.id` - unique operation id
* `operation.status` - currently status of operation
* `operation.wallet_from` - source wallet id 
* `operation.wallet_to` - destination wallet id 

TODO: make fields ordered in csv

### Get report of wallet operations by username
`GET /users/by_name/<username>/operations/?date_from=YYYY-mm-dd&date_to=YYYY-mm-dd&format=<format>`
Output is same

### Get all users wallets (balance and currency)
`GET /wallets/all/?format=<format>`

format = json|csv is optional (default json)

Example of csv report:
```
balance,currency,id,user
9.2500000,USD,1,1
10.5000000,EUR,2,2
21.3333333,CAD,3,3
0.0000000,EUR,4,4
```

# Starting server and setup database
* Setup database configuration in settings.py, sections DATABASES
* `python3 manage.py migrate`
* `python3 manage.py loaddata currencies`
* optional for testing: `python3 manage.py loaddata users_wallets operations`
* `python3 manage.py runserver`
