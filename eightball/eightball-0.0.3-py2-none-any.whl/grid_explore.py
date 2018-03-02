# param_bounds = {
#     'n_estimators': (20, 5, 1, 1, 50),
#     'min_samples_split': (14, 12, 1, 1, 32),
#     'max_features': (0.2, 0.15, 0.05, 0.05, 1)
# }
import copy


class GridExplore(object):
    def __init__(self, model, scoring):
        self.model = copy.copy(model)
        self.scoring = scoring
        self.all_scores = {}
        self.best_score = -1000
        self.best_params = 0
        self.new_scores_count = 1
        self.best_score_path = []
        self.best_param_path = []

    def explore(self, param_bounds, verbose=False):
        step_size = []
        param_vals = []
        min_step_size = []
        lower_lims = []
        upper_lims = []
        param_names = param_bounds.keys()
        param_names.sort()
        for p in param_names:
            param_vals.append(param_bounds[p][0])
            step_size.append(param_bounds[p][1])
            min_step_size.append(param_bounds[p][2])
            lower_lims.append(param_bounds[p][3])
            upper_lims.append(param_bounds[p][4])
        self.iter = 0
        if verbose:
            print('param_vals: %s' % dict(zip(param_names, param_vals)))
            print('\tstep_size: %s' % step_size)
        while self.iter < 30:
            param_grid = {}
            for i in range(len(param_names)):
                p = param_names[i]
                if param_vals[i] - step_size[i] < lower_lims[i]:
                    param_grid[p] = [lower_lims[i], param_vals[i], param_vals[i] + step_size[i]]
                if param_vals[i] + step_size[i] > upper_lims[i]:
                    param_grid[p] = [param_vals[i] - step_size[i], param_vals[i], upper_lims[i]]
                else:
                    param_grid[p] = [
                        param_vals[i] - step_size[i], param_vals[i], param_vals[i] + step_size[i]
                    ]
            self.new_scores_count = 0
            res = self.process(param_grid, param_names=param_names)
            if verbose:
                print('param_vals: %s' % dict(zip(param_names, param_vals)))
                print('\tstep_size: %s' % step_size)
                print('\tnew_scores_count: %s' % self.new_scores_count)
                print('\tbest_score: %s' % self.best_score)
            self.best_score_path.append(self.best_score)
            self.best_param_path.append(self.best_params)
            if self.new_scores_count == 0:
                # cut step_size in half
                step_size_old = step_size
                step_size = []
                for i in range(len(param_names)):
                    if type(step_size_old[i]) == str:
                        continue
                    if type(step_size_old[i]) == int:
                        new_step = step_size_old[i] / 2
                    if type(step_size_old[i]) == float:
                        new_step = step_size_old[i] / 2
                    if new_step < min_step_size[i]:
                        new_step = step_size_old[i]
                    step_size.append(new_step)
                if step_size == step_size_old:
                    break
            param_vals = self.best_params
            self.iter += 1
        res['param_names'] = param_names
        return res

    def get_score(self, params, param_names):
        if params in self.all_scores:
            return self.all_scores[params]
        else:
            self.new_scores_count += 1
            params_dict = dict(zip(param_names, params))
            self.model.clf.set_params(**params_dict)
            # select the correct proba
            proba = True
            if type(self.scoring) == str and self.scoring in ('accuracy'):
                proba = False
            if type(self.scoring) == dict:
                if self.scoring.values()[0].__name__ in ('accuracy_score'):
                    proba = False
            eval_results = self.model.evaluate(scoring=self.scoring, proba=proba)
            score_type = eval_results._scores.keys()[0]
            if score_type in ['brier']:
                score = -eval_results._scores[score_type]['mean']
            else:
                score = eval_results._scores[score_type]['mean']
            self.all_scores[params] = score
            return score

    def process(self, param_grid, param_values=(), param_names=None):
        param_grid = param_grid.copy()
        keys = param_grid.keys()
        keys.sort()
        k = keys[0]
        param_v = param_grid.pop(k)
        if len(param_grid) > 0:
            # process next batch
            params = []
            values = []
            for px in param_v:
                px2 = param_values + (px,)
                results = self.process(param_grid, param_values=px2, param_names=param_names)
                params.append(results['params'])
                values.append(results['values'])
            return {'params': params, 'values': values}
        else:
            params = []
            values = []
            for px in param_v:
                p_cell = param_values + (px,)
                params.append(p_cell)
                score = self.get_score(p_cell, param_names)
                if score > self.best_score:
                    self.best_score = score
                    self.best_params = p_cell
                values.append(score)
            return {'params': params, 'values': values}
