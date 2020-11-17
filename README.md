# DraftkingsNFL-PredicitonModel

## Planning
### Requirements
1. Backtest-able: The strategy should be fully backtest-able. We should be able to validate that any changes made to any part of the pipeline lead to better performance than in the past.
2. Human Intervention: Zero “expert knowledge” should be required. For instance, if LeBron has consistently underperformed when matched up against Kawhi, the strategy should figure this out, rather than being told-so explicitly.
3. Replicable: Any data used should be public information (i.e., no subscription services, no private historical data like cash lines).
4. Scalable: The pipeline should scale to multiple platforms and sports with minimal additional work.
5. Fast: Development should be fluid — each step of the pipeline should be able to run independently, and long-running or I/O intensive segments should be performed infrequently and offline.
6. Automated (Optional): The entire pipeline should be automated, including entering competitions. 

### Goals
* Initially limit games to only showdown 50/50 and double ups. Advance to full lineup 50/50 and double ups.
* Profitability: win rate over 50%
* Above Average Results: win rate over Draftkings average %

### Steps
1. Stats Retrieval: We start by retrieving historical data that we will use as the basis for making per-player predictions. For the NBA, this includes per-game player and team stats scraped from basketball-reference, as well as auxiliary data such as betting lines and predicted starting lineups.
2. Feature Creation: Using these stats, we construct derived Features that will be the basis of the learning algorithm.
3. Model Fit: Using these derived features, we fit a model that creates a mapping from Features to FantasyPoints.
4. Roster Retrieval: Retrieve the eligible players, injury status, matchups, and, most importantly, cost-per-player (salaries) for the day.
5. Prediction Feature Creation: Apply the same process we use to create Features to transform roster data into the same exact Features we used to create the player model.
6. Prediction: Using the model we created earlier and the PredictionFeatures, we make fantasy point predictions.
7. Team Selection: We run a linear-optimization (maximize predicted fantasy points subject to salary and position constraints) to produce the team we will enter.

These above Requirements and Steps were taken from https://towardsdatascience.com/creating-a-fully-automated-daily-fantasy-sports-strategy-6842d2e1ccb6


## Data
Most data will likely need to be scraped using some python XML or HTML tool.

### Player Data
### Team Data

### DraftKings Data
The data for any given draftkings contest can be retrieved from a csv file provided on their website. 

### DraftKings Rules
Rules vary by contest, so a hardcode file is likely the best option to determine scoring. Most importantly, there is a salary cap of $50,000.
