import os
import json

final_arr = []
for dataset_name in [
    "glove-100-angular",
    "gist-960-euclidean",
    "deep-image-96-angular",
    "dbpedia-openai-1M-1536-angular",
]:
    map_dir_engine = {
        # "RediSearch 2.8.0 (July 2023) SW (6 threads m6i.2xlarge)": f"{dataset_name}-redis-6-threads-july-10",
        "Redis 7.2": f"vertical-1-shard-6-threads-results/{dataset_name}",
        # "RediSearch 2.8.11 (February 2024) SW (6 shards 0 threads m6i.2xlarge)": f"horizontal-6-shards-0-threads-results/{dataset_name}",
        # "Amazon Aurora Memory-Optimized Class PostgreSQL v16.1 and pgvector 0.5.1 (db.r7g.2xlarge)": f"results-aurora-postgres16-1-r7g.2xlarge/{dataset_name}",
        # "Amazon Aurora Read-Optimized Class PostgreSQL v16.1 and pgvector 0.5.1 (db.r6gd.2xlarge)": f"results-aurora-postgres16-1-r6gd.2xlarge/{dataset_name}",
 # "Qdrant Cloud v1.3.2 (July 2023)": f"{dataset_name}-qdrant",
       "Qdrant 1.7.4": f"qdrant-cloud-1_7_4-8vcpus-32gbram-results/{dataset_name}",
        # "Qdrant SW v1.3.2": f"{dataset_name}-qdrant-SW",
       "Milvus 2.2.11": f"{dataset_name}-milvus-july-16",
       "Weaviate 1.20.1": f"{dataset_name}-weaviate",
    }

    # iterate over files in that directory
    for engine_name, directory in map_dir_engine.items():
        engine_arr = []
        engine_upload_map = {}
        if os.path.exists(directory):
            print(f"working on engine: {engine_name} and dir: {directory}")
            print("reading first the upload data")
            for filename in os.listdir(directory):
                f = os.path.join(directory, filename)
                setup_name = filename.split(dataset_name)[0]
                setup_name = setup_name[0 : len(setup_name) - 1]
                if "upload" in f:
                    with open(f, "r") as fd:
                        json_res = json.load(fd)
                        parallel = 1
                        if "parallel" in json_res["params"]:
                            parallel = json_res["params"]["parallel"]

                        # ingest
                        if "upload_time" in json_res["results"]:
                            total_time = json_res["results"]["total_time"]
                            upload_time = json_res["results"]["upload_time"]

                            engine_upload_map[setup_name] = {
                                "upload_time": upload_time,
                                "total_upload_time": total_time,
                            }

            for filename in os.listdir(directory):
                f = os.path.join(directory, filename)
                setup_name = filename.split(dataset_name)[0]
                setup_name = setup_name[0 : len(setup_name) - 1]
                with open(f, "r") as fd:
                    json_res = json.load(fd)
                    parallel = 1
                    if "parallel" in json_res["params"]:
                        parallel = json_res["params"]["parallel"]

                    # query
                    if "rps" in json_res["results"]:
                        upload_time = engine_upload_map[setup_name]["upload_time"]
                        total_upload_time = engine_upload_map[setup_name][
                            "total_upload_time"
                        ]
                        setup_name = setup_name.replace("-ef-", "-ef_construction-")
                        rps = json_res["results"]["rps"]
                        mean_precisions = json_res["results"]["mean_precisions"]
                        mean_time = json_res["results"]["mean_time"]
                        p50_time = json_res["results"]["p50_time"]
                        p95_time = json_res["results"]["p95_time"]
                        p99_time = json_res["results"]["p99_time"]
                        engine_params = {}
                        if "search_params" in json_res["params"]:
                            engine_params["search_params"] = json_res["params"][
                                "search_params"
                            ]
                        if "params" in json_res["params"]:
                            engine_params["params"] = json_res["params"][
                                "params"
                            ]
                        single_run = {
                            "engine_name": engine_name,
                            "setup_name": setup_name,
                            "dataset_name": dataset_name,
                            "rps": rps,
                            "parallel": parallel,
                            "mean_precisions": mean_precisions,
                            "p50_time": p50_time,
                            "p95_time": p95_time,
                            "p99_time": p99_time,
                            "mean_time": mean_time,
                            "upload_time": upload_time,
                            "total_upload_time": total_upload_time,
                            "engine_params": engine_params,
                        }
                        engine_arr.append(single_run)
                        final_arr.append(single_run)

with open("result-2023-07-05.json", "w") as json_fd:
    json.dump(final_arr, json_fd)
