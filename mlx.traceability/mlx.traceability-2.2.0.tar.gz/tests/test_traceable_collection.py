from unittest import TestCase

import mlx.traceable_item as dut


class TestTraceableCollection(TestCase):
    docname = 'folder/doc.rst'
    identification_src = 'some-random$name\'with<\"weird@symbols'
    fwd_relation = 'some-random-forward-relation'
    rev_relation = 'some-random-reverse-relation'
    unidir_relation = 'some-random-unidirectional-relation'
    identification_tgt = 'another-item-to-target'

    def test_init(self):
        coll = dut.TraceableCollection()
        # Self test should fail as no relations configured
        with self.assertRaises(dut.TraceabilityException):
            coll.self_test()

    def test_add_relation_pair_bidir(self):
        coll = dut.TraceableCollection()
        # Initially no relations, so no reverse
        self.assertIsNone(coll.get_reverse_relation(self.fwd_relation))
        relations_iterator = coll.iter_relations()
        self.assertNotIn(self.fwd_relation, relations_iterator)
        self.assertNotIn(self.rev_relation, relations_iterator)
        # Add a bi-directional relation pair
        coll.add_relation_pair(self.fwd_relation, self.rev_relation)
        # Reverse for fwd should be rev, and vice-versa
        self.assertEqual(self.rev_relation, coll.get_reverse_relation(self.fwd_relation))
        self.assertEqual(self.fwd_relation, coll.get_reverse_relation(self.rev_relation))
        # Verify relations iterator
        relations_iterator = coll.iter_relations()
        self.assertIn(self.fwd_relation, relations_iterator)
        self.assertIn(self.rev_relation, relations_iterator)
        # Self test should pass
        coll.self_test()

    def test_add_relation_pair_unidir(self):
        coll = dut.TraceableCollection()
        # Initially no relations, so no reverse
        self.assertIsNone(coll.get_reverse_relation(self.unidir_relation))
        # Add a uni-directional relation pair
        coll.add_relation_pair(self.unidir_relation)
        # Reverse for fwd should be nothing
        self.assertEqual(coll.NO_RELATION_STR, coll.get_reverse_relation(self.unidir_relation))
        # Self test should pass
        coll.self_test()

    def test_add_item(self):
        coll = dut.TraceableCollection()
        # Initially no items
        self.assertFalse(coll.has_item(self.identification_src))
        self.assertIsNone(coll.get_item(self.identification_src))
        item_iterator = coll.iter_items()
        self.assertNotIn(self.identification_src, item_iterator)
        self.assertNotIn(self.identification_tgt, item_iterator)
        # Add an item
        item1 = dut.TraceableItem(self.identification_src)
        item1.set_document(self.docname)
        coll.add_item(item1)
        self.assertTrue(coll.has_item(self.identification_src))
        self.assertEqual(item1, coll.get_item(self.identification_src))
        # Add same item: should give warning
        with self.assertRaises(dut.TraceabilityException):
            coll.add_item(item1)
        self.assertTrue(coll.has_item(self.identification_src))
        self.assertEqual(1, len(coll.items))
        self.assertEqual(item1, coll.get_item(self.identification_src))
        # Add a second item, make sure first one is still there
        self.assertFalse(coll.has_item(self.identification_tgt))
        item2 = dut.TraceableItem(self.identification_tgt)
        item2.set_document(self.docname)
        coll.add_item(item2)
        self.assertTrue(coll.has_item(self.identification_tgt))
        self.assertEqual(item2, coll.get_item(self.identification_tgt))
        self.assertEqual(item1, coll.get_item(self.identification_src))
        # Verify iterator
        item_iterator = coll.iter_items()
        self.assertIn(self.identification_src, item_iterator)
        self.assertIn(self.identification_tgt, item_iterator)
        # Self test should pass
        coll.add_relation_pair(self.fwd_relation, self.rev_relation)
        coll.self_test()

    def test_add_item_overwrite(self):
        coll = dut.TraceableCollection()
        item1 = dut.TraceableItem(self.identification_src)
        item1.set_document(self.docname)
        coll.add_item(item1)
        coll.add_relation_pair(self.fwd_relation, self.rev_relation)
        coll.add_relation(self.identification_src,
                          self.fwd_relation,
                          self.identification_tgt)
        # Add target item: should update existing one (keeping relations)
        item2 = dut.TraceableItem(self.identification_tgt)
        item2.set_document(self.docname)
        coll.add_item(item2)
        # Assert old relations are still there
        item1_out = coll.get_item(self.identification_src)
        item2_out = coll.get_item(self.identification_tgt)
        relations = item1_out.iter_targets(self.fwd_relation)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_tgt)
        relations = item2_out.iter_targets(self.rev_relation)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_src)
        # Assert item are not placeholders
        self.assertFalse(item1_out.is_placeholder())
        self.assertFalse(item2_out.is_placeholder())

    def test_add_relation_unknown_source(self):
        # with unknown source item, exception is expected
        coll = dut.TraceableCollection()
        item2 = dut.TraceableItem(self.identification_tgt)
        item2.set_document(self.docname)
        coll.add_item(item2)
        coll.add_relation_pair(self.fwd_relation, self.rev_relation)
        with self.assertRaises(ValueError):
            coll.add_relation(self.identification_src,
                              self.fwd_relation,
                              self.identification_tgt)
        # Self test should pass
        coll.self_test()

    def test_add_relation_unknown_relation(self):
        # with unknown relation, warning is expected
        coll = dut.TraceableCollection()
        item1 = dut.TraceableItem(self.identification_src)
        item1.set_document(self.docname)
        item2 = dut.TraceableItem(self.identification_tgt)
        item2.set_document(self.docname)
        coll.add_item(item1)
        coll.add_item(item2)
        with self.assertRaises(dut.TraceabilityException):
            coll.add_relation(self.identification_src,
                              self.fwd_relation,
                              self.identification_tgt)
        relations = item1.iter_targets(self.fwd_relation, explicit=True, implicit=True)
        self.assertEqual(0, len(relations))
        relations = item2.iter_targets(self.fwd_relation, explicit=True, implicit=True)
        self.assertEqual(0, len(relations))
        # Self test should pass
        coll.add_relation_pair(self.fwd_relation, self.rev_relation)
        coll.self_test()

    def test_add_relation_unknown_target(self):
        # With unknown target item, the generation of a placeholder is expected
        coll = dut.TraceableCollection()
        item1 = dut.TraceableItem(self.identification_src)
        item1.set_document(self.docname)
        coll.add_item(item1)
        coll.add_relation_pair(self.fwd_relation, self.rev_relation)
        coll.add_relation(self.identification_src,
                          self.fwd_relation,
                          self.identification_tgt)
        # Assert explicit forward relation is created
        relations = item1.iter_targets(self.fwd_relation, explicit=True, implicit=False)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_tgt)
        relations = item1.iter_targets(self.fwd_relation, explicit=False, implicit=True)
        self.assertEqual(0, len(relations))
        # Assert placeholder item is created
        item2 = coll.get_item(self.identification_tgt)
        self.assertIsNotNone(item2)
        self.assertEqual(self.identification_tgt, item2.get_id())
        self.assertTrue(item2.is_placeholder())
        # Assert implicit reverse relation is created
        relations = item2.iter_targets(self.rev_relation, explicit=False, implicit=True)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_src)
        relations = item2.iter_targets(self.fwd_relation, explicit=True, implicit=False)
        self.assertEqual(0, len(relations))
        # Self test should fail, as we have a placeholder item
        with self.assertRaises(dut.MultipleTraceabilityExceptions):
            coll.self_test()

    def test_add_relation_happy(self):
        # Normal addition of relation, everything is there
        coll = dut.TraceableCollection()
        item1 = dut.TraceableItem(self.identification_src)
        item1.set_document(self.docname)
        item2 = dut.TraceableItem(self.identification_tgt)
        item2.set_document(self.docname)
        coll.add_item(item1)
        coll.add_item(item2)
        coll.add_relation_pair(self.fwd_relation, self.rev_relation)
        coll.add_relation(self.identification_src,
                          self.fwd_relation,
                          self.identification_tgt)
        # Assert explicit forward relation is created
        relations = item1.iter_targets(self.fwd_relation, explicit=True, implicit=False)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_tgt)
        relations = item1.iter_targets(self.fwd_relation, explicit=False, implicit=True)
        self.assertEqual(0, len(relations))
        # Assert item2 is not a placeholder item
        item2_read = coll.get_item(self.identification_tgt)
        self.assertFalse(item2.is_placeholder())
        self.assertEqual(item2, item2_read)
        # Assert implicit reverse relation is created
        relations = item2.iter_targets(self.rev_relation, explicit=False, implicit=True)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_src)
        relations = item2.iter_targets(self.fwd_relation, explicit=True, implicit=False)
        self.assertEqual(0, len(relations))
        # Self test should pass
        coll.self_test()

    def test_add_relation_unidirectional(self):
        # Normal addition of uni-directional relation
        coll = dut.TraceableCollection()
        item1 = dut.TraceableItem(self.identification_src)
        item1.set_document(self.docname)
        coll.add_item(item1)
        coll.add_relation_pair(self.unidir_relation)
        coll.add_relation(self.identification_src,
                          self.unidir_relation,
                          self.identification_tgt)
        # Assert explicit forward relation is created
        relations = item1.iter_targets(self.unidir_relation, explicit=True, implicit=False)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_tgt)
        relations = item1.iter_targets(self.unidir_relation, explicit=False, implicit=True)
        self.assertEqual(0, len(relations))
        # Assert item2 is not existent
        self.assertIsNone(coll.get_item(self.identification_tgt))
        # Self test should pass
        coll.self_test()

    def test_stringify(self):
        coll = dut.TraceableCollection()
        # Assert relation pairs are printed
        coll.add_relation_pair(self.fwd_relation, self.rev_relation)
        collstr = str(coll)
        self.assertIn(self.fwd_relation, collstr)
        self.assertIn(self.rev_relation, collstr)
        # Add some items and relations, assert they are in the string
        item1 = dut.TraceableItem(self.identification_src)
        item1.set_document(self.docname)
        coll.add_item(item1)
        coll.add_relation(self.identification_src,
                          self.fwd_relation,
                          self.identification_tgt)
        collstr = str(coll)
        self.assertIn(self.identification_src, collstr)
        self.assertIn(self.identification_tgt, collstr)

    def test_selftest(self):
        coll = dut.TraceableCollection()
        coll.add_relation_pair(self.fwd_relation, self.rev_relation)
        # Self test should pass
        coll.self_test()
        # Create first item
        item1 = dut.TraceableItem(self.identification_src)
        item1.set_document(self.docname)
        # Improper use: add target on item level (no sanity check and no automatic reverse link)
        item1.add_target(self.fwd_relation, self.identification_tgt)
        # Improper use is not detected at level of item-level
        item1.self_test()
        # Add item to collection
        coll.add_item(item1)
        # Self test should fail as target item is not in collection
        with self.assertRaises(dut.MultipleTraceabilityExceptions):
            coll.self_test()
        # Self test one limited scope (no matching document), should pass
        coll.self_test('document-does-not-exist.rst')
        # Creating and adding second item, self test should still fail as no automatic reverse relation
        item2 = dut.TraceableItem(self.identification_tgt)
        item2.set_document(self.docname)
        coll.add_item(item2)
        with self.assertRaises(dut.MultipleTraceabilityExceptions):
            coll.self_test()
        # Mimicing the automatic reverse relation, self test should pass
        item2.add_target(self.rev_relation, self.identification_src)
        coll.self_test()
