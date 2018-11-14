# -*- coding:utf-8 -*-

broker_url = "redis://localhost:6379/0"
result_backend = "redis://localhost:6379/0"

task_default_exchange = "vampiretasks"
task_default_exchange_type = "direct"
task_default_routing_key = "vampire"
task_default_queue = "vampiretasks"
task_time_limit = 7200

accept_content = ["json"]
task_serializer = "json"
result_serializer = "json"

worker_prefetch_multiplier = 1
