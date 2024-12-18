# Overview
This repository is for a scoping review of breath-by-breath gas exchange data processing. It contains most data and code for study 1 from the dissertation found at https://conservancy.umn.edu/items/f62f4994-5f30-480a-a0cd-4e3a819d6c7b.

# Repository Navigation
It is worth noting that this repository was part of Anton's first major version control project. As such, it is admittedly less tidy and organized than would be ideal. Nevertheless, the most useful parts of this repository for those interested in the details will likely be the **code** and **data** folders. Folders and subfolders with minor importance are omitted from this section. Please contact Anton (ahesse2567@gmail.com) if you require additional information. 

## Code
### cpet_articles
This folder contains the majority of the code in this repository.
#### gathering
Here we store mostly Python scripts to download article metadata and then the articles themselves, either through text and data mining services or web scraping. Subfolders are organized by publisher when necessary.
#### tidying
Most scripts here clean or organize full-text files.
#### analysis
Scripts here emphasize identifying eligible and ineligible articles and using regular expressions to extract text snippets that may indicate the presence of methods describing data processing steps. The **reporting** subfolder contains scripts that usually perform the final calculations that appear in the dissertation or any published articles.

## Data
### cpet_articles
As in the code folder, this folder contains the most and most important data in the repository.
#### database_search
Initial electronic search output.
#### unpaywall
The major article metadata file is unpaywall_info.csv. Other files mostly record files downloaded or errors encountered during text and data mining process.
#### text_analysis
Data from which we performed most of our final analyses. The **eligibility** subfolder has records of if and how different articles were eligible or ineligible.


