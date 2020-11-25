import numpy as np
import csv
import pandas as pd
import math
from gurobipy import *
pd.set_option('display.max_columns', None)
week11_data = pd.read_csv("DFF_NFL_cheatsheet_2020-11-26.csv")
week11_data = week11_data.drop(columns=["slate","ppg_actual","value_actual"])
week11_data['Name'] = week11_data['first_name']+' '+week11_data['last_name'].fillna('')
week11_data = week11_data.drop(columns=["first_name","last_name"])
#week11_data = week11_data[week11_data['position']!="QB"]
week11_data = week11_data[week11_data['Name']!="Matthew Stafford"]
team1 = week11_data[week11_data['team']=='HOU'].reset_index()
team2 = week11_data[week11_data['team']=='DET'].reset_index()
dk_matchup = pd.read_csv("DKSalaries (1).csv")
dk_matchup = dk_matchup[dk_matchup['Roster Position']=='FLEX']

team1 = team1.join(dk_matchup.set_index('Name'),on='Name')
team1 = team1.drop(columns=['Position','Name + ID','ID','Roster Position','Game Info','TeamAbbrev','salary'])
team2 = team2.join(dk_matchup.set_index('Name'),on='Name')
team2 = team2.drop(columns=['Position','Name + ID','ID','Roster Position','Game Info','TeamAbbrev','salary'])
print(team2)

team1['CPT_salary'] = team1["Salary"]*1.5
team1['CPT_ppg'] = team1['ppg_projection']*1.5
team2['CPT_salary'] = team2["Salary"]*1.5
team2['CPT_ppg'] = team2['ppg_projection']*1.5
# Creating dictionaries for variables and constraints
team1_reg_dict = {}
for num in range(len(team1)):
    team1_reg_dict[team1['Name'][num]] = (float(team1['ppg_projection'][num]))

team1_cpt_dict = {}
for num in range(len(team1)):
    team1_cpt_dict[team1['Name'][num]] = (float(team1['CPT_ppg'][num]))

team2_reg_dict = {}
for num in range(len(team2)):
    team2_reg_dict[team2['Name'][num]] = (float(team2['ppg_projection'][num]))

team2_cpt_dict = {}
for num in range(len(team2)):
    team2_cpt_dict[team2['Name'][num]] = (float(team2['CPT_ppg'][num]))

team1_reg_sal = {}
for num in range(len(team1)):
    team1_reg_sal[team1['Name'][num]] = (int(team1['Salary'][num]))

team1_cpt_sal = {}
for num in range(len(team1)):
    team1_cpt_sal[team1['Name'][num]] = (int(team1['CPT_salary'][num]))

team2_reg_sal = {}
for num in range(len(team2)):
    team2_reg_sal[team2['Name'][num]] = (int(team2['Salary'][num]))

team2_cpt_sal = {}
for num in range(len(team2)):
    team2_cpt_sal[team2['Name'][num]] = (int(team2['CPT_salary'][num]))

t1_player, t1_ppg = multidict(team1_reg_dict)
t1_player_cpt, t1_cpt_ppg = multidict(team1_cpt_dict)
t2_player, t2_ppg = multidict(team2_reg_dict)
t2_player_cpt, t2_cpt_ppg = multidict(team2_cpt_dict)
# Create Model
m = Model('netflow')

# Create variables
t1_reg = m.addVars(t1_player, vtype=GRB.BINARY, name="team1 regular players")
t1_cpt = m.addVars(t1_player_cpt, vtype=GRB.BINARY, name="team1 captain")
t2_reg = m.addVars(t2_player, vtype=GRB.BINARY, name="team2 regular players")
t2_cpt = m.addVars(t2_player_cpt, vtype=GRB.BINARY, name="team2 captain")
m.update()

# demand constraints
m.addConstr(quicksum(t1_reg[i] + t1_cpt[i] for i in t1_player)>=1)
m.addConstr((quicksum(t2_reg[i] for i in t2_player)+quicksum(t2_cpt[i] for i in t2_player))>=1)
m.addConstr((quicksum(t1_cpt[i] for i in t1_player)+quicksum(t2_cpt[i] for i in t2_player))==1)
m.addConstrs(t1_reg[i] + t1_cpt[i] <= 1 for i in t1_player)
m.addConstrs(t2_reg[i] + t2_cpt[i] <= 1 for i in t2_player)
m.addConstr((quicksum(t1_reg[i] for i in t1_player)+quicksum(t1_cpt[i] for i in t1_player)+quicksum(t2_reg[i] for i in t2_player)+quicksum(t2_cpt[i] for i in t2_player))==6)
m.addConstr((quicksum(t1_reg[i]*team1_reg_sal[i] + t1_cpt[i]*team1_cpt_sal[i] for i in t1_player)+quicksum(t2_reg[i]*team2_reg_sal[i]+t2_cpt[i]*team2_cpt_sal[i] for i in t2_player))<=50000)
m.update()
# Compute optimal solution
#m.setObjective(sum(hs_prod[i] for i in hsp)+sum(fl_prod[i] for i in flp), GRB.MAXIMIZE)
obj = quicksum(t1_reg[i]*team1_reg_dict[i] for i in t1_player)+quicksum(t2_reg[i]*team2_reg_dict[i] for i in t2_player)+quicksum(t1_cpt[i]*team1_cpt_dict[i] for i in t1_player)+quicksum(t2_cpt[i]*team2_cpt_dict[i] for i in t2_player)

m.setObjective(obj,GRB.MAXIMIZE)
#m.optimize()

# Print solution
#if m.status == GRB.Status.OPTIMAL:
#    Retrieve variables value
#    print('Player Lineup')
#    for v in m.getVars():
#        if v.x > 0:
#            print('%s = %g' % (v.varName, v.x))
m.setParam(GRB.Param.PoolSolutions, 20)
# Limit the search space by setting a gap for the worst possible solution
# that will be accepted
m.setParam(GRB.Param.PoolGap, 0.10)
# do a systematic search for the k-best solutions
m.setParam(GRB.Param.PoolSearchMode, 2)

# Optimize
m.optimize()

m.setParam(GRB.Param.OutputFlag, 0)

# Status checking
status = m.Status
if status in (GRB.INF_OR_UNBD, GRB.INFEASIBLE, GRB.UNBOUNDED):
    print('The m cannot be solved because it is infeasible or '
          'unbounded')
    sys.exit(1)

if status != GRB.OPTIMAL:
    print('Optimization was stopped with status ' + str(status))
    sys.exit(1)

# Print number of solutions stored
nSolutions = m.SolCount
print('Number of solutions found: ' + str(nSolutions))

# Print objective values of solutions
for e in range(nSolutions):
    m.setParam(GRB.Param.SolutionNumber, e)
    print('%g ' % m.PoolObjVal, end='')
    print('')
    for v in m.getVars():
        if v.xn > 0.9:
            print('%s = %g' % (v.varName, v.x))
