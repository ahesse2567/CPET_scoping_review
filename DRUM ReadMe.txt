This readme.txt file was generated on <20241010> by <Anton Hesse>
Recommended citation for the data: 


-------------------
GENERAL INFORMATION
-------------------


1. Breath-by-breath outlier, interpolation, and averaging methodology documentation during exercise testing in original, peer-reviewed articles


2. Author Information


  Principal Investigator Contact Information
        Name: Anton Hesse
           Institution: University of Minnesota-Twin Cities
           Address: Cooke Hall 1900 University Ave SE, Minneapolis, MN 55455
           Email: hesse151@umn.edu; ahesse2567@gmail.com
	   ORCID: 0000-0001-8456-7343

  Associate or Co-investigator Contact Information
        Name: Christopher Lundstrom
           Institution: University of Minnesota-Twin Cities
           Address: Cooke Hall 1900 University Ave SE, Minneapolis, MN 55455
           Email: lund0982@umn.edu
	   ORCID: 0000-0002-1527-1685

  Associate or Co-investigator Contact Information
        Name: Manix White
           Institution: University of Minnesota-Twin Cities


3. Date published or finalized for release: 

4. Date of data collection (single date, range, approximate date) <suggested format YYYYMMDD>

5. Geographic location of data collection (where was data collected?): Minneapolis, MN

6. Information about funding sources that supported the collection of the data: This project was not funded

7. Overview of the data (abstract): This dataset comprises the outlier documentation of results for studies with an exercise test that collected breath-by-breath gas exchange data. The results describe if the article text described the outlier removal procedures, and if so, how.


--------------------------
SHARING/ACCESS INFORMATION
-------------------------- 


1. Licenses/restrictions placed on the data: 

2. Links to publications that cite or use the data: 

3. Was data derived from another source? No

4. Terms of Use: Data Repository for the U of Minnesota (DRUM) By using these files, users agree to the Terms of Use. https://conservancy.umn.edu/pages/policies/#drum-terms-of-use




---------------------
DATA & FILE OVERVIEW
---------------------


1. File List
   A. Filename:        outliers.csv
      Short description:        File identification, corresponding regular expression terms and text snippets, and categorization of outlier removal procedures

   B. Filename:        interpolation.csv
      Short description:        File identification, corresponding regular expression terms and text snippets, and categorization of outlier removal procedures
        
   C. Filename:        averaging.csv
      Short description:	File identification, corresponding regular expression terms and text snippets, and categorization of outlier removal procedures


2. Relationship between files:        



--------------------------
METHODOLOGICAL INFORMATION
--------------------------

1. Description of methods used for collection/generation of data: We conducted a semi-automated scoping review to document the prevalence and popularity of different breath-by-breath data processing procedures. Articles were downloaded from a combination of text and data mining APIs, custom web-scraping scripts, and manual downloads.

2. Methods for processing the data: Article PDFs and other binary files were converted to plain text files. We next normalized the plain text files by converting text to lowercase, removing end-of-line hyphenations, excessive whitespace, etc. We then used regular expressions to extract phrases that likely contained information on data processing details.

3. Instrument- or software-specific information needed to interpret the data: We performed our descriptive statistics using R and RStudio, but several programming languages or spreadsheet software could perform these analyses.


4. Standards and calibration information, if appropriate: N/A


5. Environmental/experimental conditions: N/A


6. Describe any quality-assurance procedures performed on the data: We manually read text snippets identified by the regular expressions. We read the full article context when the snippet was unclear. Regular expressions were developed to minimize fall negatives while allowing false positives. That is, we developed our regular expressions to avoid missing descriptions of outlier, interpolation, and averaging methodologies. Our data quality was higher by reading text snippets extracted by the regular expressions and concluding the authors did not document their data processing methodologies. In contrast, any false negatives would be articles missed by our regular expressions entirely, and we would only document data processing in those articles if we read the article by chance.


7. People involved with sample collection, processing, analysis and/or submission: Anton Hesse was responsible for collecting, processing, and submission. Manix White assisted with data processing. Chris Lundstrom was involved with the analysis and submission.


-----------------------------------------
DATA-SPECIFIC INFORMATION FOR: [FILENAME]
-----------------------------------------
<create sections for each dataset included>


1. Number of variables:


2. Number of cases/rows: 




3. Missing data codes:
        Code/symbol        Definition
        Code/symbol        Definition


4. Variable List
                  

    A. Name: <variable name>
       Description: <description of the variable>
                    Value labels if appropriate


    B. Name: <variable name>
       Description: <description of the variable>
                    Value labels if appropriate