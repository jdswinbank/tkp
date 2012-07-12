# This is a set of unit tests in the presence of correlated noise.
# That noise was generated by convolving uncorrelated noise with the
# dirty beam of a certain VLA observation. 3969 identical extended
# sources on a regular 63*63 grid were convolved with the clean beam.
# The accuracy of the deconvolution algorithm, i.e., the deconvolution
# of the fitted parameters from the clean beam. is tested.
# It also tests the accuracy of the peak flux measurements.
# Bias up to 5 sigma is allowed.
# Remember that oversampling of the synthesized beam will likely reduce bias.
# Accuracy tests for integrated fluxes and positions will be added
# later, as well as tests for the kappa*sigma clipper and the
# deblending algorithm.

import unittest
try:
    unittest.TestCase.assertIsInstance
except AttributeError:
    import unittest2 as unittest

import os
import numpy as np

from tkp.utility.accessors import FitsFile
from tkp.sourcefinder import image

import tkp.config
from ..decorators import requires_data


DATAPATH = tkp.config.config['test']['datapath']
MAX_BIAS = 5.0
NUMBER_INSERTED = 3969
TRUE_PEAK_FLUX = 1063.67945065
TRUE_DECONV_SMAJ = 2.*5.5956/2.
TRUE_DECONV_SMIN = 0.5*4.6794/2.
TRUE_DECONV_BPA = -0.5*(-49.8)


class SourceParameters(unittest.TestCase):

    def setUp(self):
        bgfile = FitsFile(os.path.join(DATAPATH, 'CORRELATED_NOISE.FITS'))
        bgdata = image.ImageData(bgfile.data,
                                 bgfile.beam, bgfile.wcs).data
        fitsfile = FitsFile(os.path.join(DATAPATH, 'TEST_DECONV.FITS'))
        img = image.ImageData(fitsfile.data, fitsfile.beam,
                              fitsfile.wcs)

        # This is quite subtle. We bypass any possible flaws in the
        # kappa, sigma clipping algorithm by supplying a background
        # level and noise map.  In this way we make sure that any
        # possible biases in the measured source parameters cannot
        # come from biases in the background level.  The peak fluxes,
        # in particular, can be biased low if the background levels
        # are biased high.  The background and noise levels supplied
        # here are the true values.

        extraction_results = img.extract(
            anl=6., noisemap=np.std(bgdata)*np.ones((2048, 2048)),
            bgmap=np.mean(bgdata)*np.ones((2048, 2048)))
        self.number_sources = len(extraction_results)

        peak_fluxes = []
        deconv_smajaxes = []
        deconv_sminaxes = []
        deconv_bpas = []

        for sources in extraction_results:
            peak_fluxes.append([sources.peak.value, sources.peak.error])
            deconv_smajaxes.append([sources.smaj_dc.value,
                                    sources.smaj_dc.error])
            deconv_sminaxes.append([sources.smin_dc.value,
                                    sources.smin_dc.error])
            deconv_bpas.append([sources.theta_dc.value,
                                sources.theta_dc.error])

        self.peak_fluxes = np.array(peak_fluxes)
        self.deconv_smajaxes = np.array(deconv_smajaxes)
        self.deconv_sminaxes = np.array(deconv_sminaxes)
        self.deconv_bpas = np.array(deconv_bpas)

    @requires_data(os.path.join(DATAPATH, 'CORRELATED_NOISE.FITS'))
    @requires_data(os.path.join(DATAPATH, 'TEST_DECONV.FITS'))
    def testAllDeconvolved(self):
        self.assertEqual(
            np.where(np.isnan(self.deconv_smajaxes), 1, 0).sum(), 0)
        self.assertEqual(
            np.where(np.isnan(self.deconv_sminaxes), 1, 0).sum(), 0)
        self.assertEqual(
            np.where(np.isnan(self.deconv_bpas), 1, 0).sum(), 0)

    @requires_data(os.path.join(DATAPATH, 'CORRELATED_NOISE.FITS'))
    @requires_data(os.path.join(DATAPATH, 'TEST_DECONV.FITS'))
    def testNumSources(self):
        self.assertEqual(self.number_sources, NUMBER_INSERTED)

    @requires_data(os.path.join(DATAPATH, 'CORRELATED_NOISE.FITS'))
    @requires_data(os.path.join(DATAPATH, 'TEST_DECONV.FITS'))
    def testPeakFluxes(self):
        peak_weights = 1./self.peak_fluxes[:,1]**2
        sum_peak_weights = np.sum(peak_weights)
        av_peak = np.sum(self.peak_fluxes[:,0] * peak_weights /
                         sum_peak_weights)
        av_peak_err = np.mean(self.peak_fluxes[:,1])
        signif_dev_peak = ((TRUE_PEAK_FLUX-av_peak) *
                           np.sqrt(self.number_sources) / av_peak_err)
        self.assertTrue(np.abs(signif_dev_peak) < MAX_BIAS)

    @requires_data(os.path.join(DATAPATH, 'CORRELATED_NOISE.FITS'))
    @requires_data(os.path.join(DATAPATH, 'TEST_DECONV.FITS'))
    def testMajorAxes(self):
        smaj_weights = 1./self.deconv_smajaxes[:,1]**2
        sum_smaj_weights = np.sum(smaj_weights)
        av_smaj = np.sum(self.deconv_smajaxes[:,0]*smaj_weights /
                         sum_smaj_weights)
        av_smaj_err = np.mean(self.deconv_smajaxes[:,1])
        signif_dev_smaj = ((TRUE_DECONV_SMAJ-av_smaj) *
                           np.sqrt(self.number_sources) / av_smaj_err)
        self.assertTrue(np.abs(signif_dev_smaj) < MAX_BIAS)

    @requires_data(os.path.join(DATAPATH, 'CORRELATED_NOISE.FITS'))
    @requires_data(os.path.join(DATAPATH, 'TEST_DECONV.FITS'))
    def testMinorAxes(self):
        smin_weights = 1./self.deconv_sminaxes[:,1]**2
        sum_smin_weights = np.sum(smin_weights)
        av_smin = np.sum(self.deconv_sminaxes[:,0] * smin_weights /
                         sum_smin_weights)
        av_smin_err = np.mean(self.deconv_sminaxes[:,1])
        signif_dev_smin = ((TRUE_DECONV_SMIN-av_smin) *
                           np.sqrt(self.number_sources) / av_smin_err)
        self.assertTrue(np.abs(signif_dev_smin) < MAX_BIAS)

    @requires_data(os.path.join(DATAPATH, 'CORRELATED_NOISE.FITS'))
    @requires_data(os.path.join(DATAPATH, 'TEST_DECONV.FITS'))
    def testPositionAngles(self):
        bpa_weights = 1./self.deconv_bpas[:,1]**2
        sum_bpa_weights = np.sum(bpa_weights)
        av_bpa = np.sum(self.deconv_bpas[:,0]*bpa_weights/sum_bpa_weights)
        av_bpa_err = np.mean(self.deconv_bpas[:,1])
        signif_dev_bpa = ((TRUE_DECONV_BPA-av_bpa) *
                          np.sqrt(self.number_sources) / av_bpa_err)
        self.assertTrue(np.abs(signif_dev_bpa) < MAX_BIAS)


if __name__ == '__main__':
    unittest.main()