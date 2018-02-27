import sys
import numpy as np
sys.path.append("/usr/local/lib/python2.7/site-packages")
import test_helper

def list_continious(lst):
    return ', '.join(map(str, lst))

def lab1_test_ex_1(dummy_plus_5):
    f_10 = dummy_plus_5.take(10)
    Test.assertEqualsHashed(f_10, '931f5cd168f083db2a230d92a73a83710fb4437f',
                            'Incorrect RDD: [{}, ...]'.format(list_continious(f_10)),
                            'Correct RDD: [{}, ...]'.format(list_continious(f_10)))
    
def lab1_test_ex_2(dummy_divisible_by_3):
    res = dummy_divisible_by_3.take(10) + dummy_divisible_by_3.top(10)
    f_10 = dummy_divisible_by_3.take(10)
    Test.assertEqualsHashed(res, 'f560a8e93e904ba6eafad0c41ff0ad52e8db37ee',
                            'Incorrect RDD: [{}, ...]'.format(list_continious(f_10)),
                            'Correct RDD: [{}, ...]'.format(list_continious(f_10)))
    
def lab1_test_ex_3(dummy_less_than_50, dummy_top_5, dummy_product):
    res = dummy_less_than_50.collect()
    Test.assertEqualsHashed(res, '3e4e1750c95be2c366128d69d78aea2afde114a8',
                            'Incorrect RDD: {}'.format(res),
                            'Correct RDD: {}'.format(res))
    
    Test.assertEqualsHashed(dummy_top_5, '8ff5b2b55bc143e048bf78182ec3194f1e49e0c7',
                            'Incorrect RDD: {}'.format(dummy_top_5),
                            'Correct RDD: {}'.format(dummy_top_5))
    
    Test.assertEqualsHashed(dummy_product, 'cb78c76bd7a7cfe8feb17ad7a4e1166dcfbbb7d3',
                            'Incorrect product: {}'.format(dummy_product),
                            'Correct product: {}'.format(dummy_product))
    
def lab1_test_ex_4(letters, occurrence):
    res = letters.collect()
    Test.assertEqualsHashed(res, '19275f3ffa39938f61d208d6b310835fb18b759f',
                            'Incorrect RDD: {}'.format(res),
                            'Correct RDD: {}'.format(res))
    
    Test.assertEqualsHashed(occurrence, '22d71673a52391bd1724694ce8a2ec0238356522',
                            'Incorrect dict: {}'.format(occurrence),
                            'Correct dict: {}'.format(occurrence))
    
def lab1_test_ex_5(pairs, flat_pairs, flattened_pairs):
    res1 = pairs.take(5) + pairs.top(5)
    Test.assertEqualsHashed(res1, 'fb52be8957a9bdf4eaf329b26cdb707cdec41135',
                            'Incorrect RDD: [{}, ...]'.format(list_continious(res1)),
                            'Correct RDD: [{}, ...]'.format(list_continious(res1)))
    
    res2 = flat_pairs.take(10) + flat_pairs.top(10)
    Test.assertEqualsHashed(res2, 'a0e5a552e17d1c96511d392768c197e7318ec479',
                            'Incorrect RDD: [{}, ...]'.format(list_continious(res2)),
                            'Correct RDD: [{}, ...]'.format(list_continious(res2)))
    
    res3 = flattened_pairs.take(10) + flattened_pairs.top(10)
    Test.assertEqualsHashed(res3, 'a0e5a552e17d1c96511d392768c197e7318ec479',
                            'Incorrect RDD: [{}, ...]'.format(list_continious(res3)),
                            'Correct RDD: [{}, ...]'.format(list_continious(res3)))
    
    
def lab1_test_ex_6(number_pairs, number_duplicates):
    res1 = number_pairs.collect()
    Test.assertEqualsHashed(res1, '19e2885cbed30b9b2cfc220cf979b1d137e11f52',
                            'Incorrect RDD: {}'.format(res1),
                            'Correct RDD: {}'.format(res1))
    
    res2 = number_duplicates.collect()
    Test.assertEqualsHashed(res2, '84df916b883f187ed27a3109cf14bb4bd80e78e9',
                            'Incorrect RDD: {}'.format(res2),
                            'Correct RDD: {}'.format(res2))
    
def lab1_test_ex_7(inventory_diff, inventory_diff_sorted):
    res1 = inventory_diff.collect()
    Test.assertEqualsHashed(res1, '3af93b5e352a178963b6f6d72986edfc5a20aa6c',
                            'Incorrect RDD: {}'.format(res1),
                            'Correct RDD: {}'.format(res1))
    
    res2 = inventory_diff_sorted.collect()
    Test.assertEqualsHashed(res2, '89066489ead47cae2fa3737e8c4a82bc3e9afbd6',
                            'Incorrect RDD: {}'.format(res2),
                            'Correct RDD: {}'.format(res2))
    
    
    
def lab2_test_ex_1(logs):
    c = logs.count()
    t = logs.top(2)
    Test.assertEqualsHashed(c, 'd779e44c393784ee42c0baf60e5f787f2ab64d81',
                            'Incorrect logs count: {}'.format(c),
                            'Correct logs count: {}'.format(c))
    
    Test.assertEqualsHashed(t, '80b7732e143c2f3f867e9fdd0118c2ad6e47c141',
                            'Incorrect logs: [{}, ...]'.format(list_continious(logs.take(2))),
                            'Correct logs: [{}, ...]'.format(list_continious(logs.take(2))))
    
def lab2_test_ex_2(csa, csmin, csmax):
    Test.assertEqualsHashed(csa, '3b37b833000b5646f0ea8606a5e980b5728c77c4',
                            'Incorrect avg size: {}'.format(csa),
                            'Correct avg size: {}'.format(csa))
    
    Test.assertEqualsHashed(csmin, 'b6589fc6ab0dc82cf12099d1c2d40ab994e8410c',
                            'Incorrect min size: {}'.format(csmin),
                            'Correct min size: {}'.format(csmin))
    
    Test.assertEqualsHashed(csmax, '23ecf47a03f192561239cc7da9ea3e8755c8c0ee',
                            'Incorrect max size: {}'.format(csmax),
                            'Correct max size: {}'.format(csmax))
    
def lab2_test_ex_3(response_code_counts):
    Test.assertEqualsHashed(response_code_counts, 'e167b0ae562c9083c5ab35d9e5430583d9a2bc60',
                            'Incorrect RDD: {}'.format(response_code_counts),
                            'Correct RDD: {}'.format(response_code_counts))
    
def lab2_test_ex_4(response_code_counts):
    Test.assertEqualsHashed(response_code_counts, 'a23154aaf42c5addb8365a2dcd8d682210a3957b',
                            'Incorrect RDD: {}'.format(response_code_counts),
                            'Correct RDD: {}'.format(response_code_counts))
    
def lab2_test_ex_5(top_10_hosts):
    Test.assertEqualsHashed(top_10_hosts, 'fe387f732f0c9dc663adca8937d39d7a23278e6d',
                            'Incorrect RDD: {}'.format(top_10_hosts),
                            'Correct RDD: {}'.format(top_10_hosts))
    
def lab2_test_ex_6(top_10_hosts):
    Test.assertEqualsHashed(top_10_hosts, 'fe387f732f0c9dc663adca8937d39d7a23278e6d',
                            'Incorrect RDD: {}'.format(top_10_hosts),
                            'Correct RDD: {}'.format(top_10_hosts))
    
def lab2_test_ex_7(top_20_endpoints_404):
    Test.assertEqualsHashed(top_20_endpoints_404, '768e38a3aa83ea0d5ced989c6af4e7df0968412e',
                            'Incorrect RDD: {}'.format(top_20_endpoints_404),
                            'Correct RDD: {}'.format(top_20_endpoints_404))
    
def lab2_test_ex_8(top_20_endpoints_404):
    Test.assertEqualsHashed(top_20_endpoints_404, '8699ae1164d67e0a8260e74baf973070d559c9ec',
                            'Incorrect RDD: {}'.format(top_20_endpoints_404),
                            'Correct RDD: {}'.format(top_20_endpoints_404))
                            
def lab2_test_ex_9(top_11_hosts_404):
    Test.assertEqualsHashed(top_11_hosts_404, 'b68f0611777ca20cd48360d6296e544ad39599cb',
                            'Incorrect RDD: {}'.format(top_11_hosts_404),
                            'Correct RDD: {}'.format(top_11_hosts_404))
    
def lab2_test_ex_10(top_11_hosts_404):
    Test.assertEqualsHashed(top_11_hosts_404, 'a2a32f8d91d217a2a82a59276448f4162d72b2cc',
                            'Incorrect RDD: {}'.format(top_11_hosts_404),
                            'Correct RDD: {}'.format(top_11_hosts_404))
    
    
def lab3_test_ex_1(first_point_label, first_point_features):
    Test.assertEqualsHashed(len(first_point_features),
                            '17ba0791499db908433b80f37c5fbc89b870084b',
                            'Incorrect number of features: {}'.format(len(first_point_features)),
                            'Correct number of features: {}'.format(len(first_point_features)))
    
    Test.assertEqualsHashed(first_point_label,
                            '2ce6ddc84d93a3a1dcd84238cd67260bd7272e08',
                            'Incorrect label: {}'.format(first_point_label),
                            'Correct label: {}'.format(first_point_label))
    
    expected_x0 = [7.0,0.27,0.36,20.7,0.045,45.0,170.0,1.001,3.0,0.45,8.8]
    Test.assertEqualsHashed((first_point_features - expected_x0),
                            '0bf31a85e53f1ce22604702e55bbf7f41ebde965',
                            'Incorrect features: {}'.format(first_point_features),
                            'Correct features: {}'.format(first_point_features))
    
def lab3_test_ex_2_1(min_rating, max_rating, rating_range):
    Test.assertEqualsHashed(min_rating,
                            'bdc1408a91f161dab5a9893d23db3c7095200e1d',
                            'Incorrect min rating: {}'.format(min_rating),
                            'Correct min rating: {}'.format(min_rating))
    
    Test.assertEqualsHashed(max_rating,
                            'b85ab32eaa572c8016edf68011078dceed8149e5',
                            'Incorrect max rating: {}'.format(max_rating),
                            'Correct max rating: {}'.format(max_rating))
    
    Test.assertEqualsHashed(rating_range,
                            '2ce6ddc84d93a3a1dcd84238cd67260bd7272e08',
                            'Incorrect rating range: {}'.format(rating_range),
                            'Correct rating range: {}'.format(rating_range))
    
def lab3_test_ex_2_2(parsed_points, shifted_parsed_points):
    old_features = parsed_points.first().features
    new_features = shifted_parsed_points.first().features
    diff_features = old_features - new_features

    new_min_rating = shifted_parsed_points.map(lambda lp: lp.label).min()
    new_max_rating = shifted_parsed_points.map(lambda lp: lp.label).max()
    new_rating_range = new_max_rating - new_min_rating
    
    Test.assertEqualsHashed(diff_features,
                            '0bf31a85e53f1ce22604702e55bbf7f41ebde965',
                            'New features are not calculated correctly',
                            'New features calculated correctly')
    
    Test.assertEqualsHashed(new_rating_range,
                            '2ce6ddc84d93a3a1dcd84238cd67260bd7272e08',
                            'New year range is not calculated correctly',
                            'New year range calculated correctly')
    
def lab3_test_ex_3(n_partitions, train_data, val_data, test_data):
    sf2 = train_data.map(lambda lp: lp.features[2]).sum()
    sf3 = val_data.map(lambda lp: lp.features[3]).sum()
    sf4 = test_data.map(lambda lp: lp.features[4]).sum()
    sums = [sf2, sf3, sf4]
    n_total = train_data.count() + val_data.count() + test_data.count()

    Test.assertEqualsHashed(n_total,
                            '6f62570437644d4721b266a162d20cc35889917f',
                            'Unexpected Train, Val, Test dataset sizes',
                            'Train, Val, Test sizes are ok')
    
    Test.assertEqualsHashed(sums,
                            '8b4a1f9f2301bd4396fe196fb3cb62dda4b70b0d',
                            'Train, Val, Test have unexpected values',
                            'Train, Val, Test are ok')
    
    Test.assertEqualsHashed(n_partitions,
                            '9f28346a7d38b31687c9d21909b6318da391f569',
                            'Wrong number of partitions: {}'.format(n_partitions),
                            'Correct number of partitions: {}'.format(n_partitions))
    
def lab3_test_ex_4_1(weights, intercept):
    expected_intercept = 1.00003687092
    expected_weights = [0.000250792702944,9.87942310023e-06,1.22220831068e-05,0.000221312646545,1.58457070761e-06,0.00128775449573,
                    0.00488322878768,3.66514390106e-05,0.000117928277594,1.81713979186e-05,0.000399983541013]
    
    Test.assertEqualsHashed(abs(intercept - expected_intercept) < 1,
                            '88b33e4e12f75ac8bf792aebde41f1a090f3a612',
                            'Incorrect intercept: {}'.format(intercept),
                            'Correct intercept: {}'.format(intercept))
    
    Test.assertEqualsHashed(abs(weights[0] - expected_weights[0]) < 1,
                            '88b33e4e12f75ac8bf792aebde41f1a090f3a612',
                            'Incorrect weights: {}'.format(weights),
                            'Correct weights: {}'.format(weights))
    
def lab3_test_ex_4_2(sample_prediction):
    Test.assertEqualsHashed(abs(sample_prediction - 1.89839708175) < 1,
                            '88b33e4e12f75ac8bf792aebde41f1a090f3a612',
                            'Incorrect prediction: {}'.format(sample_prediction),
                            'Prediction: {}'.format(sample_prediction))
    
def lab3_test_ex_5_1(squared_error, example_RMSE):
    Test.assertEqualsHashed(squared_error(3, 1),
                            '1b6453892473a467d07372d45eb05abc2031647a',
                            'Incorrect squared_error function',
                            'Correct squared_error function')
    
    Test.assertEqualsHashed(example_RMSE,
                            '4b322e37f07576b9230316f90b84285b5d096941',
                            'Incorrect example_error: {}'.format(example_RMSE),
                            'Correct example_error: {}'.format(example_RMSE))
    
def lab3_test_ex_5_3(val_RMSE, best_RMSE):
    Test.assertEqualsHashed(abs(val_RMSE - 1.52408180718) < 1,
                            '88b33e4e12f75ac8bf792aebde41f1a090f3a612',
                            'Incorrect val_RMSE: {}'.format(val_RMSE),
                            'Correct val_RMSE: {}'.format(val_RMSE))
    
    Test.assertEqualsHashed(abs(best_RMSE - 1.524081788) < 1,
                            '88b33e4e12f75ac8bf792aebde41f1a090f3a612',
                            'Incorrect best_RMSE: {}'.format(best_RMSE),
                            'Correct best_RMSE: {}'.format(best_RMSE))
    
def lab3_test_ex_6_1(parsed_intervals):
    Test.assertEqualsHashed(parsed_intervals.map(lambda lp: lp.label).sum(),
                            '0b1de9cebbe9b7a3e42cf4e76d56df9e2002dc9b',
                            'Incorrect parsed_intervals: {}, ...'.format(parsed_intervals.first()),
                            'Correct parsed_intervals: {}, ...'.format(parsed_intervals.first()))
    
def lab3_test_ex_6_2(train_data, test_data, parsed_intervals):
    Test.assertEqualsHashed(train_data.map(lambda lp: lp.label).sum(),
                            '95790ce05be9850d7bb5d2c4e8f8d2cb9c3476d6',
                            'Incorect splitting',
                            'Correct splitting')
    
    Test.assertEqualsHashed(test_data.map(lambda lp: lp.label).sum(),
                            'dd10ec4543eef62a4eff4ce4f324ca036df08b4c',
                            'Incorect splitting',
                            'Correct splitting')
    
    Test.assertEqualsHashed(np.allclose(
            parsed_intervals.map(lambda lp: lp.label).sum(),
            train_data.map(lambda lp: lp.label).sum() +
                test_data.map(lambda lp: lp.label).sum()),
                            '88b33e4e12f75ac8bf792aebde41f1a090f3a612',
                            'Incorect splitting',
                            'Correct splitting')
    
def lab3_test_ex_6_3(test_accuracy):
    Test.assertEqualsHashed(test_accuracy >= 0.5,
                            '88b33e4e12f75ac8bf792aebde41f1a090f3a612',
                            'Incorrect DecisionTree model prediction',
                            'Correct DecisionTree model prediction')
    
def lab3_test_ex_6_4(test_accuracy):
    Test.assertEqualsHashed(test_accuracy >= 0.6,
                            '88b33e4e12f75ac8bf792aebde41f1a090f3a612',
                            'Incorrect RandomForest model prediction',
                            'Correct RandomForest model prediction')
    
def lab3_test_ex_7_1(parsed_groups, train_data, test_data):
    Test.assertEqualsHashed(parsed_groups.map(lambda lp: lp.label).sum(),
                            '0ce7925bf636cbafa9005ce2d9673bc31b8122a6',
                            'Incorect splitting',
                            'Correct splitting')
    
    Test.assertEqualsHashed(train_data.map(lambda lp: lp.label).sum() +
                                test_data.map(lambda lp: lp.label).sum(),
                            '0ce7925bf636cbafa9005ce2d9673bc31b8122a6',
                            'Incorect splitting',
                            'Correct splitting')
    
def lab3_test_ex_7_2(test_accuracy_lr):
    Test.assertEqualsHashed(test_accuracy_lr >= 0.75,
                            '88b33e4e12f75ac8bf792aebde41f1a090f3a612',
                            'Incorrect LogisticRegression model prediction',
                            'Correct LogisticRegression model prediction')
    
def lab3_test_ex_7_4(test_accuracy_lr):
    Test.assertEqualsHashed(test_accuracy_lr >= 0.75,
                            '88b33e4e12f75ac8bf792aebde41f1a090f3a612',
                            'Incorrect LogisticRegression model prediction',
                            'Correct LogisticRegression model prediction')
    
def lab3_test_ex_7_5(test_error_lr, test_error_svm):
    Test.assertEqualsHashed(test_error_lr <= 0.23,
                            '88b33e4e12f75ac8bf792aebde41f1a090f3a612',
                            'Incorrect LogisticRegression err calculation',
                            'Correct LogisticRegression err calculation')
    
    Test.assertEqualsHashed(test_error_svm <= 0.23,
                            '88b33e4e12f75ac8bf792aebde41f1a090f3a612',
                            'Incorrect SVMWithSGD err calculation',
                            'Correct SVMWithSGD err calculation')   
    
    
def lab3_test_ex_7_6(test_accuracy_gb):
    Test.assertEqualsHashed(test_accuracy_gb >= 0.85,
                            '88b33e4e12f75ac8bf792aebde41f1a090f3a612',
                            'Incorrect GradientBoosting model prediction',
                            'Correct GradientBoosting model prediction')
  

def lab4_test_ex_1(get_counts_and_averages):    
    data = [
        (1, (1, 2, 3, 4)),
        (100, (10.0, 20.0, 30.0)),
        (110, xrange(20))
    ]
    
    expectations = [
        '7650c6f17f08af462b87700b3d78f4007675a7db',
        '878cc669276bfb82d2953b2e50896b7e1e1e1c4f',
        '8d7a82af2322875247f75cac0f18ff522101b9c6'
    ]
    
    for (args, expectation) in zip(data, expectations):
        result = get_counts_and_averages(args)
        Test.assertEqualsHashed(result, expectation,
                                'Test failed for: {}'.format(args),
                                '{} -> {}'.format(args, result))


def lab4_test_ex_2(grouped_purchases, average_purchases):
    gpc = grouped_purchases.count()
    Test.assertEqualsHashed(gpc,
                            '2e0ab5b38ac3a139b7527efc5eec2118105b82b0',
                            'Incorrect length of "grouped_purchases": {}'.format(gpc),
                            'Length of `grouped_purchases` is {}'.format(gpc))
    
    apc = average_purchases.count()
    Test.assertEqualsHashed(apc,
                            '2e0ab5b38ac3a139b7527efc5eec2118105b82b0',
                            'Incorrect length of "average_purchases": {}'.format(apc),
                            'Length of `average_purchases` is {}'.format(apc))
    
    ap = average_purchases.takeOrdered(3)
    Test.assertEqualsHashed(ap,
                            'b66b7ed8a7d8127b31625f4d0ce631bb4cc8e232',
                            #'b0eb8bf0055def9cb27b14faea14e9873afe3d52',
                            'Incorrect `average_purchases`: {}'.format(ap),
                            'Correct `average_purchases`: {}'.format(ap))
    
def lab4_test_ex_3(recommended_products):
    l = len(recommended_products)
    Test.assertEqualsHashed(l,
                            '91032ad7bbcb6cf72875e8e8207dcfba80173f7c',
                            'Incorrect number of products: {}'.format(l),
                            'Correct number of products: {}'.format(l))
    
    Test.assertEqualsHashed(recommended_products,
                            '389979fae5f36cafbd562ea5c80f5660d42eaefb',
                            #'d5ee60603688f50e1d4bbf18e174866db11c1b99',
                            'Incorrect products: [{}, ...]'.format(list_continious(recommended_products)),
                            'Correct products: [{}, ...]'.format(list_continious(recommended_products[0:3])))
    
def lab4_test_ex_4_1(indexed_buyers, indexed_products):
    l1 = len(indexed_buyers)
    Test.assertEqualsHashed(l1,
                            '0029723da11a640ffd2eec846a9a2cca6285831b',
                            'Incorrect length of indexed_buyers: {}'.format(l1),
                            'Correct length of indexed_buyers: {}'.format(l1))
    
    l2 = len(indexed_products)
    Test.assertEqualsHashed(l2,
                            '2e0ab5b38ac3a139b7527efc5eec2118105b82b0',
                            'Incorrect length of indexed_buyers: {}'.format(l2),
                            'Correct length of indexed_buyers: {}'.format(l2))
    
def lab4_test_ex_4_3(purchases):
    Test.assertEqualsHashed([purchases.take(5), purchases.count()],
                            '27475424fbfde8a2a48b480a5db01eb3f9884182',
                            #'c1fdc61ea8e59eec85a99cc2c017831baa4f4051',
                            'Incorrect purchases RDD: [{}, ...]'.format(list_continious(purchases.take(5))),
                            'Correct purchases RDD: [{}, ...]'.format(list_continious(purchases.take(5))))
    
def lab4_test_ex_5(error_list):
    
    RMSE1 = error_list[0]
    RMSE2 = error_list[1]
    RMSE3 = error_list[2]
    
    Test.assertTrue(abs(RMSE1 - 1.26491106407) < 0.00000001,
                    'incorrect RMSE1 value (expected 1.26491106407)',
                    'test 5.1 - success')
    Test.assertTrue(abs(RMSE2 - 2.70801280155) < 0.00000001,
                    'incorrect RMSE1 value (expected 2.70801280155)',
                    'test 5.2 - success')
    Test.assertTrue(abs(RMSE3 - 0.0) < 0.00000001,
                    'incorrect RMSE1 value (expected 0.0)',
                    'test 5.3 - success')
    
    
def lab4_test_ex_6(errors_list):
    Test.assertTrue(abs(errors_list[0] - 6.3120935921) < 0.5,
                    'incorrect RMSE[0] value (expected about 6.312)',
                    'Test 6.1 - success')
    Test.assertTrue(abs(errors_list[4] - 3.97614773441) < 0.5,
                    'incorrect RMSE[4] value (expected about 3.976)',
                    'Test 6.2 - success')
    Test.assertTrue(abs(errors_list[7] - 4.07374957224) < 0.5,
                    'incorrect RMSE[7] value (expected about 4.074)',
                    'Test 6.3 - success')
    Test.assertTrue(abs(errors_list[9] - 4.27126330603) < 0.5,
                    'incorrect RMSE[9] value (expected about 4.272)',
                    'Test 6.4 - success')
    Test.assertTrue(abs(errors_list[14] - 4.02682737231) < 0.5,
                    'incorrect RMSE[14] value (expected about 4.027)',
                    'Test 6.4 - success')


def lab4_test_ex_7(RMSE, predictions):
    Test.assertTrue(abs(RMSE - 4.72051562103) < 0.5,
                    'incorrect RMSE value (expected about 4.721)',
                    'Test 7.1 - success')
    Test.assertEqualsHashed( predictions.take(3)[1], 
                            '11ec7603d09fbc0af0517cacd4d162f4a9e18196', 
                            'incorrect first 3 elements of the predictions', 
                            'Test 7.2 - success') 
    Test.assertEqualsHashed( abs(predictions.take(5)[4][2] - 5.048388885082981) < 0.2, 
                            '88b33e4e12f75ac8bf792aebde41f1a090f3a612', 
                            'incorrect prediction for the element in predictions', 
                            'Test 7.3 - success') 
    
    
def lab4_test_ex_8(average, RMSE):
    Test.assertEqualsHashed(average, 
                            '48da600e257d511cd9a7db7ce4fa34ae6b92748e', 
                            'incorrect average purchase (expected 3.8254751809)', 
                            'Test 8.1 is successful')
    Test.assertEqualsHashed(RMSE, 
                            '215eafc55a1caa2db0dd959fcba648e27d270cc9', 
                            'incorrect RMSE (expected 4.99122318964)', 
                            'Test 8.2 is successful')
    
