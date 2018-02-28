#!/usr/bin/python

import h2o

def get_model_property(model, summary=True, validation_metrics=False,
    mean_residual_deviance=False, columns=False, categorical_col_domains=False,
    parameters=False, all_output=False):
    """
    A convenience function to return a property from a model, since they
    are held in dicts that are not instrospectable.

    Only one property will be returned: the first one on this list that
    has a value of True.

    Args:
        model: An H2O model
        summary: if True, returns it
        validation_metrics: if True, returns it
        mean_residual_deviance: if True, returns it
        columns: if True, returns it
        categorical_col_domains: if True, returns it
        parameters: if True, returns it
        all_output: if True, returns all of the above

    Returns:
        dict/list from json or value, depending on Args
    """
    if summary:
        return model._model_json['output']['model_summary']
    elif validation_metrics:
        return model._model_json['output']['validation_metrics']
    elif mean_residual_deviance:
        return model._model_json['output']['validation_metrics'].mean_residual_deviance()
    elif columns:
        return model._model_json['output']['names']
    elif categorical_col_domains:
        return model._model_json['output']['domains']
        # ^ if this doesn't work maybe it's ['names']['domains']
    elif parameters:
        return model._model_json['parameters']
    elif all_output:
        return model._model_json['output']
    else:
        raise Exception('no valid arg is True')

def get_varimp(model):
    """
    Returns a pandas dataframe of variable importances

    Args:
        model: an H2O model

    Returns:
        A pandas dataframe with columns 'variable', 'relative_importance',
           'scaled_importance', 'pct'.

    returns a dataframe of variable importances"""
    import pandas as pd
    df_varimp = pd.DataFrame(model.varimp(), columns = ['variable',
                        'relative_importance', 'scaled_importance', 'pct'])
    df_varimp.sort_values('relative_importance', ascending=False,
                           inplace=True)
    return df_varimp

def get_train_test_split(h2o_frame, cutoff):
    """
    Splits h2oframe into train and test sets randomly.

    Args:
        h2o_frame: An h2o frame
        cutoff: A float between 0 and 1

    Returns:
        A tuple of two h2o frames, with the largest one first. In other words,
        cutoff=0.2 and cutoff=0.8 will return the exact same thing.
    """
    assert 0 < cutoff < 1, "cutoff must be in range (0,1)"
    r = h2o_frame.runif() # Random UNIForm numbers, one per row
    return h2o_frame[r < cutoff], h2o_frame[r >= cutoff]

def get_predictions(model, h2o_frame):
    """
    Returns predictions from an h2o model based on values in an h2o frame.

    Args:
        model: an h2o model
        predictions: an h2o frame

    Returns:
        list of predicted values with same length as predictions h2o frame
    """
    return list(model.predict(h2o_frame).as_data_frame()['predict'])

def print_H2OGradientBoostingEstimator_instantiation_args():
    """
    Prints a helpful list of arguments for H2OGradientBoostingEstimator when
    instantiated.

    Args:
        None

    Returns:
        None
    """
    print("""H2OGradientBoostingEstimator args
        model_id (str, optional) The unique id assigned to the resulting
            model. If none is given, an id will automatically be generated.
        distribution (str) The distribution function of the response. Must be
            "AUTO", "bernoulli", "multinomial", "poisson", "gamma", "tweedie",
            "laplace", "quantile" or "gaussian"
        quantile_alpha (float) Quantile (only for Quantile regression, must be
            between 0 and 1)
        tweedie_power (float) Tweedie power (only for Tweedie distribution,
            must be between 1 and 2)
        ntrees (int) A non-negative integer that determines the number of
            trees to grow.
        max_depth (int) Maximum depth to grow the tree.
        min_rows (int) Minimum number of rows to assign to terminal nodes.
        learn_rate (float) Learning rate (from 0.0 to 1.0)
        learn_rate_annealing (float) Multiply the learning rate by this factor
            after every tree
        sample_rate (float) Row sample rate per tree (from 0.0 to 1.0)
        sample_rate_per_class (list) Row sample rate per tree per class (one
            per class, from 0.0 to 1.0)
        col_sample_rate (float) Column sample rate per split (from 0.0 to 1.0)
        col_sample_rate_change_per_level (float) Relative change of the column
            sampling rate for every level (from 0.0 to 2.0)
        col_sample_rate_per_tree (float) Column sample rate per tree (from 0.0
            to 1.0)
        nbins (int) For numerical columns (real/int), build a histogram of (at
            least) this many bins, then split at the best point.
        nbins_top_level (int) For numerical columns (real/int), build a
            histogram of (at most) this many bins at the root level, then decrease
            by factor of two per level.
        nbins_cats (int) For categorical columns (factors), build a histogram
            of this many bins, then split at the best point. Higher values can
            lead to more overfitting.
        balance_classes (bool) logical, indicates whether or not to balance
            training data class counts via over/under-sampling (for imbalanced
            data)
        class_sampling_factors (list) Desired over/under-sampling ratios per
            class (in lexicographic order). If not specified, sampling factors
            will be automatically computed to obtain class balance during
            training. Requires balance_classes.
        max_after_balance_size (float) Maximum relative size of the training
            data after balancing class counts (can be less than 1.0). Ignored if
            balance_classes is False, which is the default behavior.
        seed (int) Seed for random numbers (affects sampling when
            balance_classes=T)
        build_tree_one_node (bool) Run on one node only; no network overhead
            but fewer cpus used. Suitable for small datasets.
        nfolds (int, optional) Number of folds for cross-validation. If nfolds
            >= 2, then validation must remain empty.
        fold_assignment (str) Cross-validation fold assignment scheme, if
            fold_column is not specified. Must be "AUTO", "Random" or "Modulo"
        keep_cross_validation_predictions (bool) Whether to keep the
            predictions of the cross-validation models
        keep_cross_validation_fold_assignment (bool) Whether to keep the
            cross-validation fold assignment.
        score_each_iteration (bool) Attempts to score each tree.
        score_tree_interval (int) Score the model after every so many trees.
            Disabled if set to 0.
        stopping_rounds (int) Early stopping based on convergence of
            stopping_metric. Stop if simple moving average of length k of the
            stopping_metric does not improve (by stopping_tolerance) for
            k=stopping_rounds scoring events. Can only trigger after at least 2k
            scoring events. Use 0 to disable.
        stopping_metric (str) Metric to use for convergence checking, only for
            _stopping_rounds > 0 Can be one of "AUTO", "deviance", "logloss",
            "MSE", "AUC", "r2", "misclassification".
        stopping_tolerance (float) Relative tolerance for metric-based
            stopping criterion (stop if relative improvement is not at least this
            much)
        min_split_improvement (float) Minimum relative improvement in squared
            error reduction for a split to happen
        random_split_points (boolean) Whether to use random split points for
            histograms (to pick the best split from).
        max_abs_leafnode_pred (float) Maximum absolute value of a leaf node
            prediction.""")

# def print_H2OGradientBoostingEstimator_train_method_args():
#         """
#     Prints a helpful list of arguments for H2OGradientBoostingEstimator when
#     .train() method is called.

#     Args:
#         None

#     Returns:
#         None
#     """
#     txt = ("""z
#     x: A vector containing the names of the predictors to use while
#         building the GBM model.
#     y: A character string or index that represents the response variable
#         in the model.
#     training frame: An H2OFrame object containing the variables in the
#         model.
#     validation frame: An H2OFrame object containing the validation dataset
#         used to construct confusion matrix. If blank, the training data is
#         used by default.
#     nfolds: Number of folds for cross-validation.
#     ignore const cols: A boolean indicating if constant columns should be
#         ignored. Default is True.
#     ntrees: A non-negative integer that defines the number of trees. The
#         default is 50.
#     max depth: The user-defined tree depth. The default is 5.
#     min rows: The minimum number of rows to assign to the terminal nodes.
#         The default is 10.
#     nbins: For numerical columns (real/int), build a histogram of at least
#         the specified number of bins, then split at the best point The default
#         is 20.
#     nbins cats: For categorical columns (enum), build a histogram of the
#         specified number of bins, then split at the best point. Higher values
#         can lead to more overfitting. The default is 1024.
#     seed: Seed containing random numbers that affects sampling.
#     learn rate: An integer that defines the learning rate. The default is
#         0.1 and the range is 0.0 to 1.0.
#     distribution: Enter AUTO, bernoulli, multinomial, gaussian, poisson,
#         gamma or tweedie to select the distribution function. The default is
#         AUTO.
#     score each iteration: A boolean indicating whether to score during
#         each iteration of model training. Default is false.
#     fold assignment: Cross-validation fold assignment scheme, if fold
#         column is not specified. The following options are supported: AUTO,
#         Random, or Modulo.
#     fold column: Column with cross-validation fold index assignment per
#         observation.
#     offset column: Specify the offset column. Note: Offsets are per-row
#         bias values that are used during model training. For Gaussian
#         distributions, they can be seen as simple corrections to the response
#         (y) column. Instead of learning to predict the response (y-row), the
#         model learns to predict the (row) offset of the response column. For
#         other distributions, the offset corrections are applied in the
#         linearized space before applying the inverse link function to get the
#         actual response values.
#     weights column: Specify the weights column. Note: Weights are per-row
#         observation weights. This is typically the number of times a row is
#         repeated, but non-integer values are supported as well. During
#         training, rows with higher weights matter more, due to the larger loss
#         function pre-factor.
#     balance classes: Balance training data class counts via over or
#         undersampling for imbalanced data. The default is FALSE.
#     max confusion matrix size: Maximum size (number of classes) for
#         confusion matrices to print in the H2O logs. Default it 20.
#     max hit ratio k: (for multi-class only) Maximum number (top K) of
#         predictions to use for hit ratio computation. Use 0 to disable.
#         Default is 10.
#     r2 stopping: Stop making trees when the R2 metric equals or exceeds
#         this value. Default is 0.999999.
#     build tree one node: Specify if GBM should be run on one node only; no
#         network overhead but fewer CPUs used. Suitable for small datasets.
#         Default is False.
#     tweedie power: A numeric specifying the power for the tweedie function
#         when distribution = "tweedie". Default is 1.5.
#     checkpoint: Enter a model key associated with a previously-trained
#         model. Use this option to build a new model as a continuation of a
#         previously-generated model.
#     keep cross validation predictions: Specify whether to keep the
#         predictions of the crossvalidation models. Default is False.
#     class sampling factors: Desired over/under-sampling ratios per class
#         (in lexicographic order). If not specified, sampling factors will be
#         automatically computed to obtain class balance during training.
#         Requires balance classes.
#     max after balance size: Maximum relative size of the training data
#         after balancing class counts; can be less than 1.0. The default is 5.
#     nbins top level: For numerical columns (real/int), build a histogram
#         of (at most) this many bins at the root level, then decrease by factor
#         of two per level.
#     model id: The unique ID assigned to the generated model. If not
#         specified, an ID is generated automatically.""")
#     print(txt)
