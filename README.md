[![Build Status](https://travis-ci.org/OpenHumans/oh-23andme-source.svg?branch=master)](https://travis-ci.org/OpenHumans/oh-23andme-source)
[![Test Coverage](https://api.codeclimate.com/v1/badges/a21c2545bf9356bf1277/test_coverage)](https://codeclimate.com/github/OpenHumans/oh-23andme-source/test_coverage)
[![Maintainability](https://api.codeclimate.com/v1/badges/a21c2545bf9356bf1277/maintainability)](https://codeclimate.com/github/OpenHumans/oh-23andme-source/maintainability)


# The *23andMe* upload project for *Open Humans*

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

The deployed version can be found at [https://oh23andmesource.herokuapp.com/](https://oh23andmesource.herokuapp.com/)

This is a Django project that is based on the [Open Humans Data Uploader](https://www.github.com/gedankenstuecke/oh_data_uploader) and [FamilyTreeDNA Uploader](https://www.github.com/gedankenstuecke/ftdna-upload). It uses the same general logic for setting up the project. But in addition to this it adds a simple *Celery* task that is enqueued as soon as a new file is uploaded.

This task grabs the newly uploaded file from *Open Humans* and performs the file format verifications to test that it's a proper *23andMe* file. Invalid rows from the file are being deleted to ensure the privacy of participants. If the uploaded file is completely broken the file will be deleted and the user is getting a message notifying them about the problem.

Furthermore, the uploaded file will be converted to a `VCF` too.
