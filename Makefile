create-topic:
	docker exec broker-1 kafka-topics --bootstrap-server broker-1:9092 --create --if-not-exists --topic user-tracking --partitions 2 --replication-factor 2