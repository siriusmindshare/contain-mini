# Integration Tests

These scripts test each ML feature by issuing calls to the `ds_infra` container. They can be run in  environments:

1. locally on your laptop with the dockerized db in a healthy state



# For local testing with the dockerized db

Note, to run these integration tests, you must have the database container up in a healthy state, and initialized as per the `ds_infra` project README.

Also, `https-call.sh` script contains a `-k` option in the curl command. We are using responsys certificate that only works in responsys domain. Since we are using this in localhost, it server will reject any connection that is from localhost. So, -k will allow to ignore such exceptions


## rfm

`./rfm.sh`

