import tweepy as tp
import numpy as np
import pandas as pd
import twint as tt
from pytrends.request import TrendReq
import sys,csv,os,collections,json,datetime

class DataIngest:

    

    def __init__(self):
        
        dir = os.path.dirname(__file__)
        coords = "states_coords.json"
        filename = os.path.join(dir, coords )

        with open(filename, "r") as read_file:
            self.us_states = json.load(read_file)
    
   
    def pytrends_pull(self, query:str, query_loc:str, start_yr:int, start_mo:int, end_yr:int, end_mo:int):
        """
        pytrends_pull(query:str, query_loc:str, start_yr:int, start_mo:int, end_yr:int, end_mo:int)
        Generates .csv file in raw_data folder with tweets based on query
        """

        # geocode = "US-{}".format(self.us_states[query_loc.lower()]['abbr'])
        geocode = ""

        #creating connection to trend.google.com
        pytrend = TrendReq()

        # creating historical interest query on give params
        historical_interest = pytrend.get_historical_interest(keywords=[query], cat=0, geo=geocode, year_start=start_yr, month_start=start_mo, day_start=1, hour_start=0, year_end=end_yr, month_end=end_mo, day_end=30, hour_end=0)

        # creating a pytrend payload based on keyword for time_interest and related_queries
        pytrend.build_payload(kw_list=[query])

        #time_interest dataframe and related_queries dictionary dict(dict)
        time_interest = pytrend.interest_over_time()
        related_queries = pytrend.related_queries()

        no_spaces = query.replace(" ", "_")

        dir = os.path.dirname(__file__)

        filename = os.path.join(dir, "..", "exported_files", "trend_history_interest_{}.csv".format(no_spaces))
        filename = filename.replace("/", "\\")

        #exporting historical interest to csv
        historical_interest.to_csv(filename)

        filename = os.path.join(dir, "..", "exported_files", "trend_time_interest_{}.csv".format(no_spaces))
        filename = filename.replace("/", "\\")

        #exporting time interest to csv
        time_interest.to_csv(filename)

        filename = os.path.join(dir, "..", "exported_files", "trend_related_queries_{}.csv".format(no_spaces))
        filename = filename.replace("/", "\\")

        #exporting related_queries to csv
        try:
            with open(filename,'w') as csvf:
                writer = csv.DictWriter(csvf, fieldnames=related_queries[query].keys())
                writer.writeheader()
                for data in related_queries.values():
                    writer.writerow(data)

        except IOError:
            print("Error writing related queries file.")

    
    def tweepy_pull(self, query:str, query_loc:str):
        """
        tweepy_pull(query:str, query_loc:str)
        Generates .csv file in raw_data folder with tweets based on query
        """
        # Authenticate to Twitter
        auth = tp.OAuthHandler("5lRjapsApADvuslQnB8DTKrjh", "RMT4e6pjwmH2iwgT6Gs1ofms8bz12DTb9yrFrODrshy6e0b0Yt")

        # Create API object
        api = tp.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        
        # searchQuery = 'axe AND throwing AND massachussetts' # Searching on keywords, all 3 must be in a tweet
        # searchQuery = '\"Revolution%20Axe%20Throwing\"' # Searching on EXACT phrase, '\"I%20Feel%20Happy\"' means it must contain the exact phrase "I feel happy" not case sensitive

        # geo = "{},{},{}".format(self.us_states[query_loc.lower()]['lat'], self.us_states[query_loc]['long'],'200mi')
        geo = "US"

        mass_search = "42,-71,200mi" #geocoding coords/radius
        tweets = api.search(q=query, 
                            rpp = 100, #max # of tweets, can pull up to 100 at a time
                            geocode = geo
                            )

                            

        dir = os.path.dirname(__file__)
        no_spaces = query.replace(" ", "_")
        filename = os.path.join(dir, "..", "exported_files", "tweepy_{}.csv".format(no_spaces))
        filename = filename.replace("/", "\\")

        

        with open(filename, 'a', encoding='utf-8') as csvf:

            writer = csv.writer(csvf)

            for tweet in tweets:

                val_text = tweet.text.replace(","," ")
                val_auth = tweet.user.screen_name.replace(","," ")
                val_date = tweet.created_at

                tweet_cond = (val_text,val_auth,val_date)

                writer.writerow(tweet_cond)


    def hourly_pytrend(self):

        """
        hourly_pytrend(query:str)
        Pulls down hourly data in a time range
        """


        """Specify start and end date as well es the requiered keyword for your query"""
        start_date = datetime.date(2018, 1, 1)
        end_date = datetime.date(2018, 1, 31)
        keyword_list = ["Christian Scott"]  # If you add a second string, minor adjustments in the code have to be made

        """Since we want weekly data for our query, we will create lists which include 
        the weekly start and end date in the specified timeframe - 2018.01.01 to 2019.5.01"""

        weekly_date_list = []

        # Adds the start date as first entry in our weekly_date_list
        start_date_temp = start_date
        weekly_date_list.append(start_date_temp)

        # This will return in list of weekly datetime.date objects - except the end date
        while start_date_temp + datetime.timedelta(days=7) <= end_date:
            start_date_temp += datetime.timedelta(days=7)
            weekly_date_list.append(start_date_temp)

        # This will add the end date to the weekly_date list. We now have a complete list in the specified timeframe
        if start_date_temp + datetime.timedelta(days=7) > end_date:
            weekly_date_list.append(end_date)

        """Now we can start to downloading the data via Google Trends API
        therefore we have to specify a key which includes the start date
        and the end-date with T00 as string for hourly data request"""

        # This List will contain pandas Dataframes of weekly data with the features "date",
        # "keyword"(which contains weekly scaling bettwen 0 and 100), "isPartial".
        # Up to this point, the scaling is not correct.
        interest_list = []

        datetime_list = []

        # Here we download the data and print the current status of the process
        for i in range(len(weekly_date_list) - 1):
            key = str(weekly_date_list[i]) + "T00 " + str(weekly_date_list[i + 1]) + "T00"
            print(key)
            datetime_list.append(key)
            p = TrendReq()
            p.build_payload(kw_list=keyword_list, timeframe=key)
            try:
                interest = p.interest_over_time()
            except:
                None

            if interest.empty: # pre-processing, if dataframe is empty, substitute all zeros instead

                d = pd.DataFrame(0, index=np.arange(169), columns=["date", "{}".format(keyword_list[0]), "isPartial"])
                # print(len(datetime_list))
                d['date'] = ["NAN"]*169
                interest = d


            interest_list.append(interest)
            print("GoogleTrends Call {} of {} : Timeframe: {} ".format(i + 1, len(weekly_date_list) - 1, key))

        """Now we have to rescale our weekly data. We can do this
        by overlapping the weekly timeframes by one data point."""

        # We define a ratio list, which includes the correction parameters =
        # (scaling last hour of week i / scaling first hour of week i+1)
        ratio_list = []

        # here we apply the correction parameter to all dfs in the interest list except interest_list[0]
        print("-----------------")
        
        print(interest_list)
        
        print("-----------------")

        # exit()

        for i in range(len(interest_list) - 1):
            # Calculation of the ratio

            print(float(interest_list[i + 1][keyword_list[0]].iloc[0]))

            if float(interest_list[i + 1][keyword_list[0]].iloc[0] == 0.0):
                denom = 1.0
            else:
                denom = float(interest_list[i + 1][keyword_list[0]].iloc[0])

            ratio = float(interest_list[i][keyword_list[0]].iloc[-1]) / denom
            ratio_list.append(ratio)
            print("{} of {}: Ratio = {}, Scale 1st hour of week {} = {}, scale last hour of week {} = {}" \
                  .format(i + 1, len(interest_list) - 1, ratio_list[i],
                          i + 1, float(interest_list[i + 1][keyword_list[0]].iloc[0]),
                          i, float(interest_list[i][keyword_list[0]].iloc[-1]),
                          )
                  )
            # Multiply the ratio with the scales of week i+1
            # Therefore we add the column "Scale" and multiply times the value in ratio_list[i]
            # The make the calculations work for round i+1, we overwrite the values column of the df[keyword] with df["Scale"] in the interest list
            interest_list[0]["Scale_{}".format(keyword_list)] = interest_list[0][keyword_list[0]]
            interest_list[i + 1]["Scale_{}".format(keyword_list)] = interest_list[i + 1][keyword_list[0]].apply(lambda x: x * ratio_list[i])
            interest_list[i + 1][keyword_list[0]] = interest_list[i + 1]["Scale_{}".format(keyword_list)]

            """We now combine the dataframes in the interest list to a Pandas Dataframe.
            The data has the correct scaling now. But not yet in the range of 0 and 100."""
            df = pd.concat(interest_list)
            df.drop(labels=keyword_list[0], axis=1, inplace=True)
            df.drop(labels="isPartial", axis=1, inplace=True)



            """As last step we scale the data back like google to a range between 0 and 100."""
            max_interest = np.max(df["Scale_{}".format(keyword_list)])
            df["Scale_{}".format(keyword_list)] = df["Scale_{}".format(keyword_list)] / max_interest * 100

            df.to_csv("{}_hourly_data.csv".format(keyword_list[0]))


    def twint_pull(self, search):

        """
        :param search: Str
        :return: None
        Dumps file into root of "this" directory
        """

        # search = 'from:trentoonmusic'

        t_config = tt.Config()
        t_config.Search = search
        t_config.Limit = 1000
        t_config.Store_object = True

        tt.run.Search(t_config)

        if search[0:5] == 'from:':

            param = 'user'
            param2 = search[5:]
        else:
            param = 'keyword'
            param2 = search



        tlist = t_config.search_tweet_list

        print(tlist)

        with open('twint_{}_{}.json'.format(param2, param), 'w') as outfile:
            for item in tlist:
                json.dump(item, outfile)


if __name__ == "__main__":
   o = DataIngest()
   o.tweepy_pull("Christian Scott", "")
#    o.pytrends_pull("Christian Scott", "", 2018, 1, 2018, 1)
#    o.hourly_pytrend()
#    o.twint_pull('from:trentoonmusic')