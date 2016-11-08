import pandas as pd
XL_FILE = dict(io="FCR_2017_2019.xls", sheet=1)
df = pd.read_excel(**XL_FILE).reset_index().fillna('')[1:]
#print(df.head())
assert not 'lev2' in df.columns

fc1 = ['r1', 'pr1', 'csr1', 'vr1']
fc2 = ['r2', 'pr2', 'csr2', 'vr2']
flag_cols = fc1 + fc2
df[flag_cols] = df[flag_cols].applymap(lambda x: str(x).strip()) #.replace(" ","")
cols1 = ['line1'] + fc1 + ['val1']
cols2 = ['line2'] + fc2 + ['val2', 'val3']
#print(df.head())

ix_t1 = (df.pr1=='') & (df.r1=='')
t1 = df[ix_t1][['line1', 'r1', 'val1']]
EXP_1 = round(t1.val1.iloc[0])
print("%-20s" % "Сумма всего", EXP_1)

ix_r1 = (df.pr1=='') & (df.r1!='')
r1 = df[ix_r1][['line1', 'r1', 'val1']]
r1_sum = round(r1.sum().val1)
print("%-20s" % "Сумма разделов", r1_sum)
assert EXP_1 == r1_sum

ix_pr1 = (df.r1!='') & (df.csr1=='')
pr1 = df[ix_r1][['line1', 'r1', 'pr1', 'val1']]
pr1_sum = round(pr1.sum().val1)
print("%-20s" % "Сумма подразделов", r1_sum)
assert pr1_sum == EXP_1

ix_csr1_lev1 = df.csr1.apply(len) == 2
csr11_sum = round(df[ix_csr1_lev1].val1.sum())
assert csr11_sum == EXP_1

assert [0, 2, 4, 7, 13] == sorted(list(set(df.csr1.apply(len).tolist())))
for d in [2, 4, 7, 13]:
   s = round(df[df.csr1.apply(len) == d].val1.sum())
   print("%-20s" % "Сумма {} знаков ЦСР".format(d), "%11d" % s)

df['lev'] = "_" 
df.loc[ix_t1, 'lev'] = "0"
df.loc[ix_pr1,'lev'] = "2"
df.loc[ix_r1, 'lev'] = "1"
df.loc[ix_csr1_lev1 ,'lev'] = "3"
df.loc[df.csr1.apply(len) == 4, 'lev'] = "4"
df.loc[df.csr1.apply(len) == 7, 'lev'] = "5"
df.loc[df.csr1.apply(len) == 13, 'lev'] = "6"


df1 = df[cols1+['lev']]
df1 = df1[~(df1.val1=='')]
df1['ix']=df1['r1']+df1['pr1']+df1['csr1']+df1['line1']
assert 0 == len(df1[df1['ix'].duplicated()])


df2 = df[cols2+['lev']]
df2 = df2[~(df2.val2=='')]
df2['ix']=df2['r2']+df2['pr2']+df2['csr2']+df2['line2']
assert 0 == len(df2[df2['ix'].duplicated()])


a = [x for x in df1['ix'].tolist() if x]
b = [x for x in df2['ix'].tolist() if x]
print(len(a), len(b))
print(len([x for x in a if x in b]))


md = df1.merge(df2, how='outer', on='ix')
md[['val1', 'val2', 'val3']] = md[['val1', 'val2', 'val3']].fillna('').applymap(lambda x: str(x).replace(".",","))


def sel(row, cols=['r1','r2']):
   a = row[cols[0]]
   b = row[cols[1]]   
   if a:
      return a
   elif b:
      return b
   else:
      return ''

      
md=md.fillna('')
D = dict(r=['r1','r2'], pr=['pr1','pr2'], csr=['csr1', 'csr2'], vr=['vr1','vr2'], lev=['lev_x','lev_y'])
for k,v in D.items():
   md[k] = md.apply(lambda x: sel(x, cols=v), axis=1)

md = md.sort(['r', 'pr', 'csr', 'vr'])

mapper={2:"3", 4:"4", 13:"5", 7:"6"}
ix = md.lev_x==''
z = md.loc[ix,['csr2']].applymap(lambda x: mapper[len(x)])
z.loc[4153].iloc[0] == '5'
# Problem: I'm trying to assign slice of column to another column, but the values do 
#          not appear in target column and assert below fails. Solution must pass assert below.
#md.loc[ix,['lev']] = z.csr2 
#assert all(md.loc[ix,['lev']].index == z.index)
#assert md.loc[4153,['lev']].iloc[0] == '5' # fails

for i in z.index:
   md.loc[i,'lev'] = z.loc[i].csr2
   print(md.loc[i,'lev'], z.loc[i].csr2)
   
ix = ['lev', 'line1', 'line2', 'val1', 'val2', 'val3'] +['r', 'pr', 'csr', 'vr'] #+  fc1 + fc2
md[ix].to_csv("merged.txt", sep="\t", decimal=",", encoding='utf-8')

n = "Федеральная целевая программа \"Жилище\" на 2015 - 2020 годы"