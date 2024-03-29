#! /usr/bin/env python3

from sklearn.linear_model import LassoCV
from sklearn.externals import joblib
import numpy as np
import math
import random


def stc(input_list):
    """Simple string conversion function"""
    return [str(x) for x in input_list]


class LCV:
    """Wrapper for SciKitLearn linear_model.ElasticNetCV to help with model optimization"""

    def __init__(self, x='numpy_array', y='predictor', sample_labels=None,
                 test_split=.2, sk_lassocv_kwargs=None, regression_site_labels=None, test_samples=None,
                 output_name=None, output_directory=None):
        assert isinstance(sk_lassocv_kwargs, dict)
        assert isinstance(sample_labels, list)
        assert isinstance(regression_site_labels, list)
        self.x = x
        self.y = y
        self.test_split = test_split
        self.la_kwargs = sk_lassocv_kwargs
        # test_container/ train_container [array, outcomes, labels]
        self.test_container = [[], [], []]
        self.train_container = [[], [], []]
        self.la_model = None
        self.sample_labels = sample_labels
        self.regression_site_labels = regression_site_labels
        self.model_stats = None
        self.input_test_samples = test_samples
        self.output_name = output_name
        self.output_directory = output_directory
        self.run()

    def run(self):
        self.set_test_samples()
        if self.input_test_samples:
            self.test_split = 0.1
        if self.test_split == 0:
            self.test_container = self.train_container
        self.fit_model()
        self.get_model_stats()
        self.model_output()

    def set_test_samples(self):
        if self.input_test_samples:
            test_samples = self.input_test_samples
        else:
            test_size = int(round(len(self.y) * self.test_split, 0))
            test_samples = random.sample(self.sample_labels, test_size)

        # test_container/ validation_container [test_array, test_outcomes, labels]

        for count, info in enumerate(zip(self.x, self.y, self.sample_labels)):
            if info[2] in test_samples:
                self.test_container[0].append(info[0])
                self.test_container[1].append(info[1])
                self.test_container[2].append(info[2])
            else:
                self.train_container[0].append(info[0])
                self.train_container[1].append(info[1])
                self.train_container[2].append(info[2])
        self.test_container[0] = np.asarray(self.test_container[0])
        self.test_container[1] = np.asarray(self.test_container[1])
        self.train_container[0] = np.asarray(self.train_container[0])
        self.train_container[1] = np.asarray(self.train_container[1])

    def fit_model(self):
        self.la_model = LassoCV(**self.la_kwargs).fit(self.train_container[0], self.train_container[1])

    def get_model_stats(self):
        regression_sites = []
        for site in zip(self.regression_site_labels, list(self.la_model.coef_)):
            if not math.isclose(site[1], 0):
                regression_sites.append(site[0])
        model_score = self.la_model.score(self.test_container[0], self.test_container[1])
        predicted_values = self.la_model.predict(self.test_container[0])
        self.model_stats = (regression_sites, model_score, predicted_values)

    def model_output(self):
        """
        """
        kwarg_pair = ['Test Split:%s\n' % str(self.test_split)]
        for key, value in self.la_model.get_params().items():
            kwarg_pair.append('%s:%s' % (key, str(value)))

        output_path = '%s%s' % (self.output_directory, self.output_name)

        joblib.dump(self.la_model, output_path + '.model')

        out = open(output_path + '.model_info.txt', 'w')
        out.write('%s\n' % self.output_name)
        out.write('Model Score (R^2) = %s\n' % str(self.model_stats[1]))
        out.write('%s\n' % '\t'.join(kwarg_pair))
        out.write('Test Samples \t%s\n' % '\t'.join(stc(self.test_container[2])))
        out.write('Test Samples Predicted Values \t%s\n' % '\t'.join(stc(self.model_stats[2])))
        out.write('Test Samples Actual Values \t%s\n' % '\t'.join(stc(self.test_container[1])))
        out.write('Training Samples \t%s\n' % '\t'.join(stc(self.train_container[2])))
        out.write('Training Samples Actual Values \t%s\n' % '\t'.join(stc(self.train_container[1])))
        out.write('Regression Sites \t%s\n' % '\t'.join(stc(self.model_stats[0])))
        out.close()
