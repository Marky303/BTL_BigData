USE stockAnalysis;

CREATE TABLE stockentriesdailyMSFT
(
  index_        MEDIUMINT,
  openStat		double,	
  highStat		double,
  lowStat		double,
  closeStat		double,
  senP			double  	DEFAULT 0,
  datetime_    	VARCHAR(50),
  PRIMARY KEY   (index_)	
); 	
SELECT * FROM stockentriesdailyMSFT;

CREATE TABLE stockPredictionMSFT
(
	datetime_    	VARCHAR(50),
    predOpen		double,
    PredClose		double,
    PRIMARY KEY (datetime_)
);
SELECT * FROM stockPredictionMSFT;

-- __________________________________________________________________________DEMO

USE stockAnalysis;

CREATE TABLE stockentriesdailyAMZN
(
  index_        MEDIUMINT,
  openStat		double,	
  highStat		double,
  lowStat		double,
  closeStat		double,
  senP			double  	DEFAULT 0,
  datetime_    	VARCHAR(50),
  PRIMARY KEY   (index_)	
); 	
SELECT * FROM stockentriesdailyAMZN;

CREATE TABLE stockPredictionAMZN
(
	datetime_    	VARCHAR(50),
    predOpen		double,
    PredClose		double,
    PRIMARY KEY (datetime_)
);
SELECT * FROM stockPredictionAMZN;








