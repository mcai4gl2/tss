tss Support for dynamodb
========================

## Motivation

When working for home projects, usually I don't want to maintain a server with Mongodb myself. However I still want to access my data everywhere. Dynamodb is Amazon's cloud offering for NonSql database which gives 25GB space for free. This is perfect for small projects in which I can just chunk data into it without the overheads of maintaining servers.

## Current Status

Current dynamodb implementation replicates the mongodb interface implemented. It is a bare minimum implementation.

There are the following enhancements which will be implemented:

* General improvements on exception handling
* Abstract the storage from slice and series so common logic between mongodb and dynamodb can be extracted and unified
* More testing against Amazon cloud directly instead of just local dynamodb

## Interface Differences

Main differences between mongodb storage and dynamodb storage are:

* `num_of_samples` in mongo is stored in `Series`. This is however stored at slice level in dynamodb. This is because dynamodb doesn't have a way to address and update field on sub document.

* slice has attribute named `slice_data` instead of `data`. This is because `data` is a reserved word in dynamodb.

* In mongo, `Series` has id as the primary key. In dynamodb, we use `scope` and `name` together to identify a `Series`. This is to avoid expensive scan in dynamodb and use query with only `scope` to list data. This is more related to the fact that in dynamodb, we expect to know the key. This can be changed with further study of dynamodb api.