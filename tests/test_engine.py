import unittest
from engine import timestamps, normalize, rank_frames, load_index

class EngineTests(unittest.TestCase):
    def test_sampling_stays_within_video(self):
        self.assertEqual(timestamps(5.1),[0,2,4])
        self.assertEqual(timestamps(4),[0,2])
        self.assertEqual(timestamps(.5),[0])
    def test_invalid_sampling(self):
        for duration,interval in [(0,2),(5,0),(float('inf'),2)]:
            with self.assertRaises(ValueError): timestamps(duration,interval)
    def test_zero_and_nonfinite_vectors(self):
        for vector in ([0,0],[float('nan'),1]):
            with self.assertRaises(ValueError): normalize(vector)
    def test_nearby_results_are_deduplicated(self):
        frames=[{'timestamp':t,'thumbnail':'frame','embedding':v} for t,v in [(0,[1,0]),(2,[.99,.01]),(4,[.8,.2]),(8,[0,1])]]
        self.assertEqual([r['timestamp'] for r in rank_frames(frames,[1,0])],[0,4,8])
    def test_mismatched_spaces_rejected(self):
        with self.assertRaises(ValueError): rank_frames([{'timestamp':0,'thumbnail':'x','embedding':[1,0]}],[1,0,0])
    def test_video_id_cannot_be_a_path(self):
        with self.assertRaises(ValueError): load_index('../../outside')

if __name__=='__main__': unittest.main()
