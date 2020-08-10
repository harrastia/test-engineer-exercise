# Test automation exercise

This repository provides a "quick and dirty" application for different exercises
related to test automation.

Disclaimer: These apps do not follow best practices or the quality standards at
Holvi, they have been put in place quickly for the exercise.

## Requirements

You will need to have installed in your system `Docker` and `docker-compose`.
All this has been developed mostly using MacOS. Please let us know if there is
any problem running this in other operating systems.

## Quickstart

The use case implemented is two applications:
 * Inventory for a shop and placing orders for provider.
 * Provider warehouse inventory, order reception and delivery to customers

The only thing necessary to get the applications running is execute
`docker-compose up` at the root folder of the directory. It will run 3
applications which can be reached in the following ports:

* `http://localhost:5001`: Inventory app for customer 1
* `http://localhost:5002`: Inventory app for customer 2
* `http://localhost:5500`: Provider warehouse app


## Service implementation and integration

The services use Python `Flask` with storage of data with Python `tinydb` in json.
Databases with initial data have been provided so that they are easy to reset
via `git reset --hard` (docker-compose down and up will be required)

Frontends are implemented with Mithriljs.

The two services communicate via API endpoints and update their databases
when communication is successful.

## Exercise

The precise exercise will be delivered to you together with the referene to this
repository. If any code modifications are done as part of it, zip the results
and send back via email. In order to preserve anonimity between candidates, please
do not create Pull requests.