#include <iostream>
#include <cassandra.h>

int main() {
    CassCluster* cluster = cass_cluster_new();
    CassSession* session = cass_session_new();

    /* Add contact points */
    cass_cluster_set_contact_points(cluster, "127.0.0.1");

    /* Provide the cluster object as configuration to connect the session */
    CassFuture* connect_future = cass_session_connect(session, cluster);

    /* This operation will block until the result is ready */
    CassError rc = cass_future_error_code(connect_future);

    printf("Connect result: %s\n", cass_error_desc(rc));

    cass_future_free(connect_future);
    cass_session_free(session);
    cass_cluster_free(cluster);

    return 0;
}
