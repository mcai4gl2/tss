DynamoDB tests
==============

Tests here expects dynamodb is running locally. See circle.yml for an example of how to run a dynamodb local instance.

Tests here expects the dynamodb is empty on start. There is currently no code to handle the situation when table exists.

When running the tests locally, would need to restart dynamodb local manually every time before tests are ran.