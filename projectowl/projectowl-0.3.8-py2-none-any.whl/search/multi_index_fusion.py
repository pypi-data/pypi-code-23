"""Mechanism to fuse search results from multiple feature index.
"""


class MultiIndexFusion(object):
  """Class to manage combination of multiple result sets.
  """

  def group_and_rerank(self, res_list):
    """Group hits and rerank using distance.

    Args:
      res_list: a list of NNs from each index.
      Each member is: {"data": [(item_id, dist)], "weight": weight_val}
    Returns:
      combined ranking list of items.
    """
    # a predefined value for maximum feature distance.
    max_dist_val = 1000
    num_feats = len(res_list)
    # get feature weights.
    feat_weights = []
    # form item distance dict.
    all_item_dists = {}
    all_item_hits = {}
    for idx, feat_res in enumerate(res_list):
      feat_weights.append(feat_res["weight"])
      for item in feat_res["data"]:
        item_id, item_dist = item
        if item_id not in all_item_hits:
          all_item_hits[item_id] = 0
          all_item_dists[item_id] = [max_dist_val] * num_feats
        # add hits.
        all_item_hits[item_id] += 1
        all_item_dists[item_id][idx] = item_dist
    # normalize weights.
    weight_sum = sum(feat_weights)
    feat_weights = [x / weight_sum for x in feat_weights]
    # group items based on hits and compute weighted dist.
    hit_items = [None] * (num_feats + 1)
    for item_id, hit_num in all_item_hits.iteritems():
      if hit_items[hit_num] is None:
        hit_items[hit_num] = []
      # compute weighted sum distance.
      cur_item_dists = all_item_dists[item_id]
      final_dist = sum(
          [dist * w for dist, w in zip(cur_item_dists, feat_weights)])
      hit_items[hit_num].append((item_id, hit_num, final_dist))
    # rerank each group and form final results.
    final_res = []
    for idx, items in enumerate(hit_items):
      if items is None:
        continue
      hit_items[idx] = sorted(items, key=lambda item: item[2])
      items.reverse()
      # add to final res.
      final_res.extend(items)
    # correct rank from small distance to large.
    final_res.reverse()
    return final_res
