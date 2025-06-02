import json
import os
import numpy as np
from pathlib import Path

json_list = [f for f in os.listdir(os.curdir) if f.endswith(".json")]

'''
Stats for content:
'''

json_file = json_list[0]

ro_perplexity = []
md_perplexity = []

with open(json_file, "r") as f:
    data_content = json.load(f)
    '''
    RO
    '''
    romanian_data = data_content['ro']

    for example in romanian_data:
        ro_perplexity.append(float(example['perplexity']))

    '''
    MD
    '''
    md_data = data_content['md']

    for example in md_data:
        md_perplexity.append(float(example['perplexity']))

ro_mean = np.mean(ro_perplexity)
ro_median = np.median(ro_perplexity)
ro_std = np.std(ro_perplexity)

md_mean = np.mean(md_perplexity)
md_median = np.median(md_perplexity)
md_std = np.std(md_perplexity)

print(ro_mean, ro_median, ro_std)
print(md_mean, md_median, md_std)

stats_ro = {
    "content": {
        "mean" : ro_mean,
        "median": ro_median,
        "std": ro_std
    }
}

stats_md = {
    "content": {
        "mean" : ro_mean,
        "median": ro_median,
        "std": ro_std
    }
}

with open("ro_stats.json", "w") as f:
    json.dump(stats_ro, f, indent=4)

with open("md_stats.json", "w") as f:
    json.dump(stats_md, f, indent=4)

'''
Stats for title:
'''
json_file = json_list[1]

ro_perplexity = []
md_perplexity = []

with open(json_file, "r") as f:
    data_content = json.load(f)
    '''
    RO
    '''
    romanian_data = data_content['ro']

    for example in romanian_data:
        ro_perplexity.append(float(example['perplexity']))

    '''
    MD
    '''
    md_data = data_content['md']

    for example in md_data:
        md_perplexity.append(float(example['perplexity']))

ro_mean = np.mean(ro_perplexity)
ro_median = np.median(ro_perplexity)
ro_std = np.std(ro_perplexity)

md_mean = np.mean(md_perplexity)
md_median = np.median(md_perplexity)
md_std = np.std(md_perplexity)

print(ro_mean, ro_median, ro_std)
print(md_mean, md_median, md_std)

stats_ro = {
    "title": {
        "mean" : ro_mean,
        "median": ro_median,
        "std": ro_std
    }
}

stats_md = {
    "title": {
        "mean" : ro_mean,
        "median": ro_median,
        "std": ro_std
    }
}

ro_stats_path = "ro_stats.json"
with open(ro_stats_path, "r") as f:
    json_file = json.load(f)

json_file["title"] = {
    "mean": ro_mean,
    "median": ro_median,
    "std": ro_std
}

with open(ro_stats_path, "w") as f:
    json.dump(json_file, f, indent=4)

md_stats_path = "md_stats.json"
with open(md_stats_path, "r") as f:
    json_file = json.load(f)

json_file["title"] = {
    "mean": md_mean,
    "median": md_median,
    "std": md_std
}

with open(md_stats_path, "w") as f:
    json.dump(json_file, f, indent=4)

