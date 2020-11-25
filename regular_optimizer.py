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
week11_data['CPT_salary'] = week11_data["salary"]*1.5
week11_data['CPT_ppg'] = week11_data['ppg_projection']*1.5
#week11_data = week11_data[week11_data['injury_status']!="Q"]
qb = week11_data[week11_data['position']=='QB'].reset_index()
hb = week11_data[week11_data['position']=='RB'].reset_index()
wr = week11_data[week11_data['position']=='WR'].reset_index()
te = week11_data[week11_data['position']=='TE'].reset_index()
flex = pd.concat([hb,wr,te]).reset_index()
dst = week11_data[week11_data['position']=='DST'].reset_index()

# Creating dictionaries for variables and constraints
qb_dict = {}
for num in range(len(qb)):
    qb_dict[qb['Name'][num]] = (float(qb['ppg_projection'][num]))

hb_dict = {}
for num in range(len(hb)):
    hb_dict[hb['Name'][num]] = (float(hb['ppg_projection'][num]))

wr_dict = {}
for num in range(len(wr)):
    wr_dict[wr['Name'][num]] = (float(wr['ppg_projection'][num]))

te_dict = {}
for num in range(len(te)):
    te_dict[te['Name'][num]] = (float(te['ppg_projection'][num]))

flex_dict = {}
for num in range(len(flex)):
    flex_dict[flex['Name'][num]] = (float(flex['ppg_projection'][num]))

dst_dict = {}
for num in range(len(dst)):
    dst_dict[dst['Name'][num]] = (float(dst['ppg_projection'][num]))

qb_dict_sal = {}
for num in range(len(qb)):
    qb_dict_sal[qb['Name'][num]] = (float(qb['salary'][num]))

hb_dict_sal = {}
for num in range(len(hb)):
    hb_dict_sal[hb['Name'][num]] = (float(hb['salary'][num]))

wr_dict_sal = {}
for num in range(len(wr)):
    wr_dict_sal[wr['Name'][num]] = (float(wr['salary'][num]))

te_dict_sal = {}
for num in range(len(te)):
    te_dict_sal[te['Name'][num]] = (float(te['salary'][num]))

flex_dict_sal = {}
for num in range(len(flex)):
    flex_dict_sal[flex['Name'][num]] = (float(flex['salary'][num]))

dst_dict_sal = {}
for num in range(len(dst)):
    dst_dict_sal[dst['Name'][num]] = (float(dst['salary'][num]))

qb_player, qb_ppg = multidict(qb_dict)
hb_player, hb_ppg = multidict(hb_dict)
wr_player, wr_ppg = multidict(wr_dict)
te_player, te_ppg = multidict(te_dict)
flex_player, flex_ppg = multidict(flex_dict)
dst_player, dst_ppg = multidict(dst_dict)
# Create Model
m = Model('netflow')

# Create variables
qbvar = m.addVars(qb_player, vtype=GRB.BINARY, name="qb players")
hbvar = m.addVars(hb_player, vtype=GRB.BINARY, name="hb players")
wrvar = m.addVars(wr_player, vtype=GRB.BINARY, name="wr players")
tevar = m.addVars(te_player, vtype=GRB.BINARY, name="te players")
flexvar = m.addVars(flex_player, vtype=GRB.BINARY, name="flex players")
dstvar = m.addVars(dst_player, vtype=GRB.BINARY, name="dst players")
m.update()

# demand constraints
m.addConstr(quicksum(qbvar[i] for i in qb_player)==1)
m.addConstr(quicksum(hbvar[i] for i in hb_player)==2)
m.addConstr(quicksum(wrvar[i] for i in wr_player)==3)
m.addConstr(quicksum(tevar[i] for i in te_player)==1)
m.addConstr(quicksum(flexvar[i] for i in flex_player)==1)
m.addConstr(quicksum(dstvar[i] for i in dst_player)==1)
m.addConstrs(hbvar[i]+flexvar[i]<=1 for i in hbvar)
m.addConstrs(wrvar[i]+flexvar[i]<=1 for i in wrvar)
m.addConstrs(tevar[i]+flexvar[i]<=1 for i in tevar)
salary_constraint = quicksum(qbvar[i]*qb_dict_sal[i] for i in qb_player)+quicksum(hbvar[i]*hb_dict_sal[i] for i in hb_player)+quicksum(wrvar[i]*wr_dict_sal[i] for i in wr_player)+quicksum(tevar[i]*te_dict_sal[i] for i in te_player)+quicksum(flexvar[i]*flex_dict_sal[i] for i in flex_player)+quicksum(dstvar[i]*dst_dict_sal[i] for i in dst_player)
m.addConstr(salary_constraint<=50000)
m.update()
# Compute optimal solution
#m.setObjective(sum(hs_prod[i] for i in hsp)+sum(fl_prod[i] for i in flp), GRB.MAXIMIZE)
obj = quicksum(qbvar[i]*qb_dict[i] for i in qb_player)+quicksum(hbvar[i]*hb_dict[i] for i in hb_player)+quicksum(wrvar[i]*wr_dict[i] for i in wr_player)+quicksum(tevar[i]*te_dict[i] for i in te_player)+quicksum(flexvar[i]*flex_dict[i] for i in flex_player)+quicksum(dstvar[i]*dst_dict[i] for i in dst_player)
m.setObjective(obj,GRB.MAXIMIZE)
#m.optimize()

# Print solution
#if m.status == GRB.Status.OPTIMAL:
#    Retrieve variables value
#    print('Player Lineup')
#
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
    for v in m.getVars():
        if v.xn > 0.9:
            print('%s = %g' % (v.varName, v.x))
