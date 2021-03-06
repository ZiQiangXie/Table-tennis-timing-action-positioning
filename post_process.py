import os
import json
import glob
import numpy as np
import pandas 
import pandas as pd

json_path_0 = "submission_0.json"
json_path_1 = "submission_1.json"

def iou_with_anchors(anchors_min, anchors_max, box_min, box_max):
    """Compute jaccard score between a box and the anchors.
    """
    len_anchors = anchors_max - anchors_min
    int_xmin = np.maximum(anchors_min, box_min)
    int_xmax = np.minimum(anchors_max, box_max)
    inter_len = np.maximum(int_xmax - int_xmin, 0.)
    union_len = len_anchors - inter_len + box_max - box_min
    jaccard = np.divide(inter_len, union_len)
    return jaccard

def soft_nms(df, alpha, t1, t2):
    '''
    df: proposals generated by network;
    alpha: alpha value of Gaussian decaying function;
    t1, t2: threshold for soft nms.
    '''
    df = df.sort_values(by="score", ascending=False)
    tstart = list(df.xmin.values[:])
    tend = list(df.xmax.values[:])
    tscore = list(df.score.values[:])

    rstart = []
    rend = []
    rscore = []

    while len(tscore) > 1 and len(rscore) < 101:
        max_index = tscore.index(max(tscore))
        tmp_iou_list = iou_with_anchors(np.array(tstart), np.array(tend),
                                        tstart[max_index], tend[max_index])
        for idx in range(0, len(tscore)):
            if idx != max_index:
                tmp_iou = tmp_iou_list[idx]
                tmp_width = tend[max_index] - tstart[max_index]
                if tmp_iou > t1 + (t2 - t1) * tmp_width:
                    tscore[idx] = tscore[idx] * np.exp(
                        -np.square(tmp_iou) / alpha)

        rstart.append(tstart[max_index])
        rend.append(tend[max_index])
        rscore.append(tscore[max_index])
        tstart.pop(max_index)
        tend.pop(max_index)
        tscore.pop(max_index)

    newDf = pd.DataFrame()
    newDf['score'] = rscore
    newDf['xmin'] = rstart
    newDf['xmax'] = rend
    return newDf


submit_dic = {"version": None,
              "results": {},
              "external_data": {}
              }
results = submit_dic['results']

results_0 = json.load(open(json_path_0, 'r'))["results"]
results_1 = json.load(open(json_path_1, 'r'))["results"]
for video_name in results_1.keys():
    results_list = results_0[video_name] + results_1[video_name] 
    
    cols = ["xmin", "xmax", "score"]
    score_vector_list = []
    for seg in results_list:
        score_vector_list.append([seg["segment"][0], seg["segment"][1], seg["score"]])

    score_vector_list = np.stack(score_vector_list)
    df = pandas.DataFrame(score_vector_list, columns=cols)

    proposal_list = []
    df = soft_nms(df, alpha=0.4, t1=0.55, t2=0.8)
    for idx in range(min(100, len(df))):
        tmp_prop={"score":df.score.values[idx], \
                  "segment":[df.xmin.values[idx], df.xmax.values[idx]]}
        proposal_list.append(tmp_prop)
    results[video_name] = proposal_list

json.dump(submit_dic, open('submission.json', 'w', encoding='utf-8'))
