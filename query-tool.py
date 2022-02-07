

cluster = Cluster.connect(
    "couchbase://localhost",
    ClusterOptions(PasswordAuthenticator("Administrator", "password")))
bucket = cluster.bucket("travel-sample")
collection = bucket.default_collection()

try:
    result = cluster.query(
        "SELECT * FROM `travel-sample`.inventory.airport LIMIT 10", QueryOptions(metrics=True))

    for row in result.rows():
        print("Found row: {}".format(row))

    print("Report execution time: {}".format(
        result.metadata().metrics().execution_time()))

except CouchbaseException as ex:
    import traceback
    traceback.print_exc()