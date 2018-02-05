"""Evalute folk parameterized pipelines and models."""


def eval_model(model, df, verbose=None):
    pass
    # try:
    #     _print("  - Testing {}...".format(model.__class__.__name__))
    # except AttributeError:
    #     pass
    # model_id = 'metadata_{}'.format(model_cls.__name__)
    # X, y = x_y_by_col_lbl(df, 'category')
    # scores = cross_val_score(
    #     col_ignore_clf, X=X, y=y, cv=N_FOLDS, scoring='accuracy',
    #     n_jobs=-1,
    # )
    # acc_mean = scores.mean()
    # acc_std = scores.std()
    # _print("    Accuracy: {:.2f} (+/- {:.2f})".format(
    #     scores.mean(), scores.std() * 2))
    # _print("    Writing results to db...")
    # write_metrics_to_db(
    #     model_identifier=model_id,
    #     run_at=run_at,
    #     **{
    #         MetricKey.ACC_MEAN: acc_mean,
    #         MetricKey.ACC_STD: acc_std,
    #         MetricKey.N_FOLDS: N_FOLDS,
    #         MetricKey.DATASET_SIZE: len(df),
    #         MetricKey.N_CATEG: n_categories,
    #         **params
    #     }
    # )


def eval_pipeline_n_pmodel(pipeline, pmodel, raw_df, verbose=None):
    _print = lambda x: x
    if verbose:
        _print = lambda x: print(x)
    df = pipeline(raw_df)
    _print("Resulting dataset size: {}".format(len(df)))
    _print("Number of columns: {}".format(len(df.columns)))
    i = 1
    for model in pmodel:
        _print("Evaluating pipeline {}...".format(i))
        i += 1
        eval_model(model, df, verbose)


def eval_ppipeline_n_pmodel(ppipeline, pmodel, raw_df, verbose=None):
    """Evaluates all combinations of a parameterized pipeline and model.

    Parameters
    ----------
    ppipeline : ParameterizedPipeline
        The parameterized pipeline to evaluate.
    pmodel : ParameterizedModel
        The parameterized model to evaluate.
    raw_df : pandas.DataFrame
        The raw dataframe to be processed by the pipeline and fed to the model.
    verbose : bool, optional
        If set to True, informative messages are printed. If not set, defaults
        to not displaying message. Verbosity is also to pipeline application.
    """
    _print = lambda x: x
    if verbose:
        _print = lambda x: print(x)
    _print("=============================")
    # _print("Testing models on pipeline with params {}".format(params))
    i = 1
    for pipeline in ppipeline:
        _print("Evaluating pipeline {}...".format(i))
        eval_pipeline_n_pmodel(pipeline, pmodel, raw_df, verbose)
        i += 1
    _print("=============================\n")
