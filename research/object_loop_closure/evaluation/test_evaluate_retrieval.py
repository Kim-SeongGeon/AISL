import copy
import json
import unittest
from pathlib import Path
from evaluate_retrieval import evaluate


class EvaluationTest(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((Path(__file__).parent / 'examples' / 'synthetic.json').read_text())

    def test_known_rankings_and_wrong_loop(self):
        result = evaluate(self.data, threshold=0.5)
        self.assertEqual(result['recall_at_k'], {'1': 0.5, '5': 1.0, '10': 1.0})
        self.assertEqual((result['tp'], result['fp'], result['fn'], result['tn']), (1, 2, 1, 1))
        self.assertAlmostEqual(result['precision'], 1/3)
        self.assertAlmostEqual(result['f1'], 0.4)

    def test_missing_predictions_still_count(self):
        self.data['queries'][0]['candidates'] = []
        result = evaluate(self.data)
        self.assertEqual(result['positive_query_count'], 2)
        self.assertEqual(result['fn'], 2)

    def test_invalid_rankings_rejected(self):
        for kind in ('duplicate', 'ineligible', 'nan', 'ascending', 'self'):
            with self.subTest(kind=kind):
                data = copy.deepcopy(self.data)
                row = data['queries'][0]
                if kind == 'duplicate':
                    row['candidates'].append(dict(row['candidates'][0]))
                elif kind == 'ineligible':
                    row['candidates'][0]['id'] = 'future_frame'
                elif kind == 'nan':
                    row['candidates'][0]['score'] = float('nan')
                elif kind == 'ascending':
                    row['candidates'][1]['score'] = 1.1
                else:
                    row['eligible_ids'].append(row['query_id'])
                with self.assertRaises(ValueError):
                    evaluate(data)

    def test_no_positives_is_undefined_not_zero(self):
        self.data['queries'] = self.data['queries'][2:]
        result = evaluate(self.data)
        self.assertIsNone(result['recall_at_k']['1'])
        self.assertIsNone(result['recall'])

    def test_tied_scores_keep_declared_order(self):
        row = self.data['queries'][0]
        row['candidates'][1]['score'] = row['candidates'][0]['score']
        self.assertEqual(evaluate(self.data)['tp'], 1)


if __name__ == '__main__':
    unittest.main()
