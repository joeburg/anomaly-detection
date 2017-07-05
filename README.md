# Table of Contents
1. [Summary](README.md#summary)
2. [Required Libraries](README.md#required-libraries)
3. [Capacity](README.md#capacity)
9. [Testing](README.md#testing)


# Summary

This program detects anomalous purchases within a social network, where an anomalous purchase is more than 3 standard deviations from the mean of the last T purchases in the user's Dth degree social network. 

# Required Libraries

This program was written in python and requires the following standard python libraries:
* json
* numpy
* sys
* time
* unittest

# Capacity

This program can process ~100 events/second locally on a mac. So it should be able to handle rather large traffic volumes. 

# Testing 

To run the python unit test, use the following command in the top directory:

$ python -m src.tests.tests

The unit tests are placed within the src/ directory to follow good python practices, where tests are placed within the same module.
