How to prepare the QCD CR systematic inputs
===========================================

### Overview

The code in this directory performs a 2nd-order polynomial fit of the QCD CR
systematic histogram for each year, MVA-bin combination.  The polynomial
fit parameters are transformed using a matrix composed of the eigenvectors
of the covariance matrix to a space where the three parameters are uncorrelated.
This allows the fit to be represented by three uncorrelated, Gaussian-constrained
nuisance parameters.

### Procedure

You will need to have the ttbar\_systematics.root files for each year.  They
are the inputs for run\_all\_p2fits.c.  The first argument of that function
(add\_full\_dev) will add the full deviation from 1 to the statistical error
for each point if set to true.  When you are ready, run run\_all\_p2fits.c.
It will create a directory called output-files with the output, which is a
pdf file for each fit and a root file containing the fitted histograms and a
TTree to be used for passing the fit result to Combine.

If you want, you can also run toy\_validation.c to check the output TTree.

