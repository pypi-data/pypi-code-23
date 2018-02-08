
class TestDatasetMeta(unittest.TestCase):



    # def test_meta_variable(self):
    #     D = ge.dataset.DataSet();
    #
    #     # Simple parameter
    #     D.set_meta_parameter("regexes.simple_namelike", "^[A-Z][a-z]+$")
    #     self.assertEqual(D.get_meta_parameter("regexes.double_vowels.0"), "aa")
    #
    #     # List parameter
    #     D.set_meta_parameter("regexes.double_vowels", ["aa", "ee", "ii", "oo", "uu"])
    #     self.assertEqual(D.get_meta_parameter("regexes.simple_namelike"), "^[A-Z][a-z]+$")







    # # Immediately before running, replace any $meta_value substitutions provided to the expectation
    # for arg in kwargs:
    #     if isinstance(kwargs[arg], list):
    #         replacement_list = []
    #         needs_replacement = False
    #         for list_arg in kwargs[arg]:
    #             if isinstance(list_arg, (dict, DotDict)) and "$meta_value" in list_arg:
    #                 replacement_list.append(self.get_meta_parameter(kwargs[arg]["$meta_value"]))
    #                 needs_replacement = True
    #             else:
    #                 replacement_list.append(list_arg)
    #         if needs_replacement:
    #             all_args[arg] = replacement_list
    #     elif isinstance(kwargs[arg], (dict, DotDict)) and "$meta_value" in arg:
    #         all_args[arg] = self.get_meta_parameter(kwargs[arg]["$meta_value"])


    # def set_meta_parameter(self, parameter, value):
    #     self._expectations_config['meta'][parameter] = value
    #
    # def get_meta_parameter(self, parameter, default_value=None):
    #     if parameter in self._expectations_config['meta']:
    #         return self._expectations_config['meta'][parameter]
    #     else:
    #         return default_value




    all_args = ensure_json_serializable(all_args)
+
+                # Make multiple copies: one that will be passed the expectation, after substitutions are made, and
+                # another that will be stored in the expectations config.
    expectation_args = copy.deepcopy(all_args)
+                saved_expectation_args = copy.deepcopy(all_args)

    #Construct the expectation_config object
    expectation_config = DotDict({
        "expectation_type": method_name,
-                    "kwargs": expectation_args
+                    "kwargs": saved_expectation_args
    })

    if meta is not None:
