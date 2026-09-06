"""Offline query-level evaluation. No model inference or SLAM execution."""
import argparse
import hashlib
import json
import math
from pathlib import Path


def evaluate(data, ks=(1, 5, 10), threshold=0.5):
    """Recall@k over positive queries; fixed-threshold top-1 detection over all queries.

    Scores must be higher-is-better. A wrong accepted match on a positive
    query is both a false positive and a missed true loop (false negative).
    All candidate/GT IDs must already satisfy a frozen eligibility protocol.
    """
    if not math.isfinite(threshold):
        raise ValueError('threshold must be finite')
    if not ks or any(type(k) is not int or k < 1 for k in ks):
        raise ValueError('ks must be positive integers')
    if data.get('schema_version') != 1 or not data.get('protocol_id'):
        raise ValueError('schema_version=1 and protocol_id are required')
    if type(data.get('synthetic')) is not bool:
        raise ValueError('synthetic must be explicitly true or false')
    queries = data.get('queries')
    if not isinstance(queries, list) or not queries:
        raise ValueError('queries must be a non-empty list')
    seen = set()
    hits = {k: 0 for k in ks}
    positives = tp = fp = fn = tn = 0
    for row in queries:
        qid = row['query_id']
        if not isinstance(qid, str) or not qid or qid in seen:
            raise ValueError('query_id must be a unique non-empty string')
        seen.add(qid)
        eligible, gt, candidates = row['eligible_ids'], row['positive_ids'], row['candidates']
        for name, ids in [('eligible_ids', eligible), ('positive_ids', gt)]:
            if not isinstance(ids, list) or any(not isinstance(i, str) or not i for i in ids):
                raise ValueError(name + ' must be a list of non-empty strings')
            if len(ids) != len(set(ids)) or qid in ids:
                raise ValueError(name + ' must not contain duplicates or query itself')
        eligible, gt = set(eligible), set(gt)
        if not gt <= eligible:
            raise ValueError('positive_ids must be eligible')
        if not isinstance(candidates, list):
            raise ValueError('candidates must be a list')
        ids = []
        previous = math.inf
        for candidate in candidates:
            cid, score = candidate['id'], candidate['score']
            if not isinstance(cid, str) or cid not in eligible or cid in ids:
                raise ValueError('candidates must be unique and eligible')
            if type(score) not in (int, float) or not math.isfinite(score) or score > previous:
                raise ValueError('scores must be finite, numeric and descending')
            previous = score
            ids.append(cid)
        if gt:
            positives += 1
            for k in ks:
                hits[k] += int(bool(gt.intersection(ids[:k])))
        accepted = bool(candidates) and candidates[0]['score'] >= threshold
        correct = accepted and ids[0] in gt
        tp += int(correct)
        fp += int(accepted and not correct)
        fn += int(bool(gt) and not correct)
        tn += int(not gt and not accepted)
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / positives if positives else None
    f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None
    return {
        'schema_version': 1, 'protocol_id': data['protocol_id'],
        'synthetic': data['synthetic'], 'query_count': len(queries),
        'positive_query_count': positives, 'negative_query_count': len(queries) - positives,
        'recall_at_k': {str(k): hits[k] / positives if positives else None for k in ks},
        'threshold': threshold, 'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn,
        'precision': precision, 'recall': recall, 'f1': f1,
        'detection_rule': 'fixed-threshold top-1; wrong positive-query acceptance counts as FP and FN',
        'tie_rule': 'input order is preserved; producer must declare deterministic tie-breaking',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--threshold', type=float, required=True)
    args = parser.parse_args()
    raw = args.input.read_bytes()
    result = evaluate(json.loads(raw), threshold=args.threshold)
    result['input_sha256'] = hashlib.sha256(raw).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write('\n')
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))


if __name__ == '__main__':
    main()
