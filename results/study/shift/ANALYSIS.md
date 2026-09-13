# Cross-dataset feature shift

Descriptive comparison of 20000 sampled seed-42 held-out rows per dataset in the shared signed-log encoding. KS distance measures marginal distribution difference (0 identical empirical CDFs, 1 maximal separation). No significance test or causal attribution is claimed; mixtures of attacks and benign traffic differ, and correlated or duplicate rows are not independent observations. This analysis does not tune training or thresholds.

| Feature | KS distance | Wasserstein (encoded units) | UNSW median | IDS2018 median |
| --- | --- | --- | --- | --- |
| retransmitted_out_bytes | 0.6690 | 5.7028 | 6.9745 | 0.0000 |
| retransmitted_out_pkts | 0.6636 | 1.8602 | 2.3026 | 0.0000 |
| retransmitted_in_bytes | 0.6337 | 4.2844 | 6.2916 | 0.0000 |
| icmp_ipv4_type | 0.6232 | 2.5183 | 3.5835 | 0.0000 |
| icmp_type | 0.6232 | 5.9589 | 9.1006 | 0.0000 |
| retransmitted_in_pkts | 0.6222 | 1.3409 | 1.9459 | 0.0000 |
| min_ttl | 0.5981 | 2.0104 | 3.4657 | 4.6151 |
| out_pkts | 0.5841 | 1.6340 | 3.6636 | 1.3863 |
| max_ttl | 0.5834 | 2.0012 | 3.4965 | 4.6151 |
| num_pkts_up_to_128_bytes | 0.5606 | 1.6787 | 4.2047 | 1.9459 |
| in_pkts | 0.5590 | 1.5336 | 3.6376 | 1.7918 |
| src_to_dst_second_bytes | 0.5360 | 1.8039 | 7.9197 | 5.4510 |
| src_to_dst_avg_throughput | 0.5310 | 2.0452 | 16.3618 | 13.7747 |
| in_bytes | 0.5197 | 1.8086 | 7.7765 | 5.4510 |
| tcp_win_max_in | 0.5054 | 2.1912 | 9.9170 | 9.0110 |
| dst_to_src_second_bytes | 0.4978 | 2.0192 | 8.1533 | 5.8377 |
| out_bytes | 0.4847 | 2.0625 | 8.0818 | 5.8319 |
| min_ip_pkt_len | 0.4688 | 0.2673 | 3.9703 | 3.7136 |
| dst_to_src_avg_throughput | 0.4673 | 2.2843 | 16.6089 | 14.1967 |
| shortest_flow_pkt | 0.4634 | 0.2186 | 3.9703 | 3.7136 |
| tcp_flags | 0.4362 | 1.2835 | 3.3322 | 3.1781 |
| client_tcp_flags | 0.3876 | 1.2865 | 3.3322 | 3.1355 |
| dns_query_id | 0.3744 | 3.7821 | 0.0000 | 0.0000 |
| dns_query_type | 0.3743 | 0.5718 | 0.0000 | 0.0000 |
| num_pkts_1024_to_1514_bytes | 0.3715 | 1.0961 | 0.0000 | 0.0000 |
| dns_ttl_answer | 0.3659 | 1.3460 | 0.0000 | 0.0000 |
| tcp_win_max_out | 0.3240 | 2.2513 | 9.5806 | 9.0110 |
| longest_flow_pkt | 0.3187 | 0.2815 | 6.6983 | 5.2627 |
| max_ip_pkt_len | 0.3187 | 0.2815 | 6.6983 | 5.2627 |
| l7_proto | 0.3087 | 0.5637 | 0.0000 | 0.0000 |
| server_tcp_flags | 0.1979 | 0.7592 | 3.3322 | 3.1355 |
| protocol | 0.1875 | 0.1813 | 1.9459 | 1.9459 |
| num_pkts_256_to_512_bytes | 0.1790 | 0.2185 | 0.0000 | 0.0000 |
| num_pkts_512_to_1024_bytes | 0.1764 | 0.3106 | 0.0000 | 0.0000 |
| ftp_command_ret_code | 0.1581 | 0.8407 | 0.0000 | 0.0000 |
| num_pkts_128_to_256_bytes | 0.1545 | 0.2513 | 0.0000 | 0.6931 |
| flow_duration_milliseconds | 0.0868 | 1.3257 | 0.0000 | 0.0000 |
| duration_in | 0.0834 | 0.3319 | 0.0000 | 0.0000 |
| duration_out | 0.0726 | 0.2870 | 0.0000 | 0.0000 |
