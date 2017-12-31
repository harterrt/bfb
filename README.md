# Introduction

This repo is a collection of tools for working with transaction data from
Black Forest Brewery's POS system.

# TODO

* Reporting
  * Merge this branch into master once `ratelimiting` is submitted
    * Waiting on successful backfill to submit `ratelimiting`
  * Automatically run report for "last month"
    * This makes it easier to generate the report we need
    * Partial reports aren't really useful
* Testing
  * Mock out API calls with fake data. Test expected functionality
* Clean up
  * Make headers more uniform, csvs should have meaningful order
  * Add parameter for output file path
  * Clean up class vs global functions in clover.py
