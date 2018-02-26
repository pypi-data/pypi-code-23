"""Evalute folk parameterized pipelines and models."""

from datetime import datetime

from pdutil.transform import x_y_by_col_lbl
from sklearn.model_selection import (
    cross_val_score,
)

from .metricsdb import (
    MetricKey,
    write_experiment_res,
)


def eval_model_by_params(
        run_id, model, model_id, df, lbl_col, metric_db=None, n_folds=None,
        **kwargs):
    if n_folds is None:
        n_folds = 5
    print("  - Testing {}...".format(model_id))
    X, y = x_y_by_col_lbl(df, lbl_col)
    print('    Performing {}-fold cross validation...'.format(n_folds))
    scores = cross_val_score(
        model, X=X, y=y, cv=n_folds, scoring='accuracy',
        n_jobs=-1,
    )
    acc_mean = scores.mean()
    acc_std = scores.std()
    print("    Accuracy: {:.2f} (+/- {:.2f})".format(
        scores.mean(), scores.std() * 2))
    n_classes = len(df[lbl_col].unique())
    if metric_db:
        print("    Writing results to db...")
        write_experiment_res(
            res_doc={
                MetricKey.MODEL_ID: model_id,
                MetricKey.LBL_COL: lbl_col,
                MetricKey.ACC_MEAN: acc_mean,
                MetricKey.ACC_STD: acc_std,
                MetricKey.N_FOLDS: n_folds,
                MetricKey.DATASET_SIZE: len(df),
                MetricKey.N_CLASS: n_classes,
                **kwargs,
            },
            db_name=metric_db,
            run_id=run_id,
        )


def eval_pmodel_by_params(
        run_id, pipeline, pmodel, raw_df, metric_db=None, n_folds=None,
        **kwargs):
    print("=============================")
    print("Testing parameterized model on pipeline with "
          "params {}".format(kwargs))
    df = pipeline.fit_transform(raw_df)
    print("Dataset size: {}".format(len(df)))
    print("Number of columns: {}".format(len(df.columns)))
    print("Resulting dataset size: {}".format(len(df)))
    partial_pmodel = pmodel.partial(kwargs)
    j = 1
    for model, params in partial_pmodel.model_n_params_iter():
        model_id = pmodel.model_id_by_params(params)
        print("-------- Model {} --------".format(j))
        print("Testing model with params: {}".format(params))
        full_params = {**params, **kwargs}
        eval_model_by_params(
            run_id=run_id,
            model=model,
            model_id=model_id,
            metric_db=metric_db,
            df=df,
            n_folds=n_folds,
            **full_params
        )
        j += 1
    print("=============================\n")


def eval_param_pipeline_n_model(param_pipeline, param_model, dataset,
                                metric_db=None, n_folds=None):
    """Evaluates the given parameterized pipeline and model.

    Parameters
    ----------
    param_pipeline : folk.ParameterizedPipeline
        The parameterized pipeline to evaluate.
    param_model : folk.ParameterizedModel
        The parameterized model to evaluate.
    dataset : pandas.DataFrame
        The dataset to evaluate the parameterized pipeline and model on.
    metric_db : str, optional
        The name of the folk metrics db to write results to. Must be included
        in folk's configuration. If not given, results are not written to db.
    n_folds
    """
    run_at = datetime.utcnow()
    run_id = str(run_at.timestamp()).replace('.', '')
    i = 1
    for pipeline, params in param_pipeline.pipe_n_params_iter():
        print("Pipeline #{}".format(i))
        eval_pmodel_by_params(
            run_id=run_id,
            pipeline=pipeline,
            pmodel=param_model,
            raw_df=dataset,
            metric_db=metric_db,
            n_folds=n_folds,
            **params,
        )
        i += 1
