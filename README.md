# Alliance Analytics Downloader
Download google analytics data for Alliance of Genome Resources sites

This script is intended to be first step towards normalizing page view
popularity scores across the Alliance of Genome Resources member sites

The ultimate goal of this work is to accurately capture the relative
community interest in human genes as inferred by page views at Alliance
and RGD combined with page views for othologous genes at member MODs

To add an additional site, add an entry in sites.yaml incuding the
Google Analytics view ID and regular expression filters that limit 
which URLs to include counts for when fetching data.

To allow this script to access a new site, read & analyze permissions
need to be given to ga-export@alliance-analytics-export.iam.gserviceaccount.com

