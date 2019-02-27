# *_*coding:utf-8 *_*
'''Writen by YAN Xu'''
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
import datetime

comment = pd.read_csv('./data/comment20181201_03.csv')
tweet = pd.read_csv('./data/tweet20181201_03.csv')

experiment_dir = Path('./result/')
experiment_dir.mkdir(exist_ok=True)

'''合并数据集'''
comment['merge_id'] = comment['weibo_id']
tweet['merge_id'] = tweet['_id']
merge = comment.merge(tweet, on='merge_id')


merge7 = pd.read_csv('./data/merge7.csv',encoding='gbk')
merge_nohaze = pd.read_csv('./data/merge12.csv',encoding='gbk')
merge_nohaze['haze'] = 0
merge_haze = merge.append(merge7)
merge_haze['haze'] = 1
merge = merge_nohaze.append(merge_haze)
merge.index = range(len(merge))

merge['comment_time'] = merge['created_at_x'].map(lambda x: datetime.datetime(int(x[0:4]),int(x[5:7]),int(x[8:10]),int(x[11:13]),int(x[14:16])))
merge['weibo_time'] = merge['created_at_y'].map(lambda x: datetime.datetime(int(x[0:4]),int(x[5:7]),int(x[8:10]),int(x[11:13]),int(x[14:16])))
merge['is_beijing'] = merge['province'].map(lambda x: 1 if x == '北京' else 0)
merge['is_guangdong'] = merge['province'].map(lambda x: 1 if x == '广东' else 0)
merge = merge[(merge['province']!='其他')&(merge['province']!='海外')]

'''描述统计'''
# Draw
plt.style.use('seaborn-white')
comment_counts = merge.groupby('merge_id').size()
plt.hist(comment_counts.values,bins=60, alpha=0.5,
         color='steelblue', edgecolor='white')
plt.xlim(100,1000)
plt.ylim(0,25)
plt.xlabel("comment counts")
plt.ylabel("proportion")
plt.title('Distribution of number of comments of one weibo',fontsize=15)
# plt.savefig('./result/%s.png'%name)
plt.show()

'''评论中北京的占比'''
merge_guangdong = merge[merge.is_guangdong == 1]
merge_beijing = merge[merge.is_beijing == 1]
a,b = len(merge_beijing[merge_beijing.haze==1]),len(merge_beijing[merge_beijing.haze==0])
c,d = len(merge_guangdong[merge_guangdong.haze==1]),len(merge_guangdong[merge_guangdong.haze==0])
beijing = [a/(a+c),b/(b+d)]
guangdong = [c/(a+c),d/(b+d)]
x = ['haze', 'no haze']

# Draw
width = 0.5
idx = np.arange(len(x))
plt.figure(figsize=(5,5))
plt.bar(idx, beijing, width, color='red',alpha=0.5, label='Beijing')
plt.bar(idx, guangdong, width, bottom=beijing, color='steelblue',alpha=0.5, label='Guangdong')
plt.xlabel('Haze or not')
plt.ylabel('Proportion')
plt.text(-0.11,0.5,"39.8%",fontdict={'size':'16','color':'black'})
plt.text(0.9,0.5,"41.6%",fontdict={'size':'16','color':'black'})
plt.xticks(idx + width / 2, x, rotation=40)
plt.title('Comment ratio between Guangdong and Beijing',fontsize = 13)
plt.legend()
plt.show()

beijing_comment = merge[merge['is_beijing']==1]

'''时间段统计'''
beijing_comment['comment_time'] = beijing_comment['created_at_x'].map(lambda x: datetime.datetime(int(x[0:4]),int(x[5:7]),int(x[8:10]),int(x[11:13]),int(x[14:16])))
beijing_comment['weibo_time'] = beijing_comment['created_at_y'].map(lambda x: datetime.datetime(int(x[0:4]),int(x[5:7]),int(x[8:10]),int(x[11:13]),int(x[14:16])))

beijing_comment['hour'] = beijing_comment['comment_time'].apply(lambda x: x.hour)
beijing_comment['weekday'] = beijing_comment['comment_time'].apply(lambda x: x.weekday())

beijing_comment_weekday = beijing_comment[(beijing_comment['weekday']!=6) & (beijing_comment['weekday']!=0)]
beijing_comment_weekend = beijing_comment[(beijing_comment['weekday']==6) | (beijing_comment['weekday']==0)]

# Draw
plt.hist(beijing_comment_weekend['hour'][beijing_comment_weekend.haze==1], alpha=0.5,
         color='steelblue', label='Haze', edgecolor='white',normed=True)
plt.hist(beijing_comment_weekend['hour'][beijing_comment_weekend.haze==0], alpha=0.5,
         color='red',label='No Haze', edgecolor='white',normed=True)

plt.xlabel("Haze or not")
plt.ylabel("Proportion")
plt.title('Time Distribution of comments on weekend',fontsize=15)
plt.legend()
# plt.savefig('./result/%s.png'%name)
plt.show()

plt.hist(beijing_comment_weekday['hour'][beijing_comment_weekday.haze==1], alpha=0.5,
         color='steelblue', label='Haze', edgecolor='white',normed=True)
plt.hist(beijing_comment_weekday['hour'][beijing_comment_weekday.haze==0], alpha=0.5,
         color='red',label='No Haze', edgecolor='white',normed=True)

plt.xlabel("Haze or not")
plt.ylabel("Proportion")
plt.title('Time Distribution of comments on weekday',fontsize=15)
plt.legend()
# plt.savefig('./result/%s.png'%name)
plt.show()

'''评论间隔'''
beijing_comment_weekend['time_interval'] = beijing_comment['comment_time'] - beijing_comment['weibo_time']
beijing_comment_weekend['day3'] = beijing_comment['time_interval'].map(lambda x: 1 if x.days<3 else 0)
beijing_comment_weekday['time_interval'] = beijing_comment['comment_time'] - beijing_comment['weibo_time']
beijing_comment_weekday['day3'] = beijing_comment['time_interval'].map(lambda x: 1 if x.days<3 else 0)

day3_weekend = beijing_comment_weekend[beijing_comment_weekend['day3']==1]
day3_weekend['interval_hour'] = day3_weekend.time_interval.apply(lambda x: int(x.seconds/3600)+1)
day3_weekday = beijing_comment_weekday[beijing_comment_weekday['day3']==1]
day3_weekday['interval_hour'] = day3_weekday.time_interval.apply(lambda x: int(x.seconds/3600)+1)


plt.hist(day3_weekend['interval_hour'][day3_weekend.haze==1], alpha=0.5,
         color='steelblue', label='No Haze', edgecolor='white',normed=True)
plt.hist(day3_weekend['interval_hour'][day3_weekend.haze==0], alpha=0.5,
         color='red', label='Haze', edgecolor='white',normed=True)

plt.xlabel("Comment interval")
plt.ylabel("Proportion")
plt.title('Time interval before comment on weekend',fontsize=15)
plt.legend()
# plt.savefig('./result/%s.png'%name)
plt.show()

plt.hist(day3_weekday['interval_hour'][day3_weekday.haze==1], alpha=0.5,
         color='steelblue', label='No Haze', edgecolor='white',normed=True)
plt.hist(day3_weekday['interval_hour'][day3_weekday.haze==0], alpha=0.5,
         color='red', label='Haze', edgecolor='white',normed=True)

plt.xlabel("Comment interval")
plt.ylabel("Proportion")
plt.title('Time interval before comment on weekday',fontsize=15)
plt.legend()
# plt.savefig('./result/%s.png'%name)
plt.show()

plt.figure(figsize=(10,6))
labels = ['Within 2 hours','2-10 hours','More than 10 hours']
a = len(day3_weekday[(day3_weekday.interval_hour<5) & (day3_weekday.haze==1)])
b = len(day3_weekday[(day3_weekday.interval_hour>5)&(day3_weekday.interval_hour<10)&(day3_weekday.haze==1)])
c = len(day3_weekday[(day3_weekday.interval_hour>10)&(day3_weekday.haze==1)])
sizes = [a,b,c]
colors = ['red','yellowgreen','lightskyblue']
explode = (0.05,0,0)

patches,l_text,p_text = plt.pie(sizes,explode=explode,labels=labels,colors=colors,
                                labeldistance = 1.1,autopct = '%3.1f%%',shadow = False,
                                startangle = 90,pctdistance = 0.6)
for t in l_text:
    t.set_size=(80)
for t in p_text:
    t.set_size=(80)
plt.axis('equal')
plt.legend()
plt.title('NO HAZE')
plt.savefig('./result/picture1.png')
plt.show()

'''缺失/水评论统计'''
beijing_comment_weekday['water_rate'] = beijing_comment_weekday['content_x'].map(lambda x: 1 if pd.isnull(x) or len(str(x))<2 else 0)
total_water_rate = beijing_comment_weekday['water_rate'][beijing_comment_weekday.haze==1].mean()
print('雾霾时间段北京地区工作日的评论的水评论占比：%.2f%%'%(total_water_rate*100))
total_water_rate = beijing_comment_weekday['water_rate'][beijing_comment_weekday.haze==0].mean()
print('非雾霾时间段北京地区工作日的评论的水评论占比：%.2f%%'%(total_water_rate*100))
beijing_comment_weekend['water_rate'] = beijing_comment_weekend['content_x'].map(lambda x: 1 if pd.isnull(x) or len(str(x))<2 else 0)
total_water_rate = beijing_comment_weekend['water_rate'][beijing_comment_weekend.haze==1].mean()
print('雾霾时间段北京地区周末的评论的水评论占比：%.2f%%'%(total_water_rate*100))
total_water_rate = beijing_comment_weekend['water_rate'][beijing_comment_weekend.haze==0].mean()
print('非雾霾时间段北京地区周末的评论的水评论占比：%.2f%%'%(total_water_rate*100))

plt.figure(figsize=(10,6))
#定义饼状图的标签，标签是列表
labels = ['Robotic Comment ','Normal']
a = len(beijing_comment_weekday[(beijing_comment_weekday.haze==0)&(beijing_comment_weekday.water_rate==1)])
b = len(beijing_comment_weekday[(beijing_comment_weekday.haze==0)&(beijing_comment_weekday.water_rate==0)])

sizes = [a,b]
colors = ['red','lightskyblue']
explode = (0.05,0)

patches,l_text,p_text = plt.pie(sizes,explode=explode,labels=labels,colors=colors,
                                labeldistance = 1.1,autopct = '%3.1f%%',shadow = False,
                                startangle = 90,pctdistance = 0.6)
for t in l_text:
    t.set_size=(80)
for t in p_text:
    t.set_size=(80)
plt.axis('equal')
plt.legend()
plt.savefig('./result/picture1.png')
plt.show()

plt.bar(range(4), [3.4,6.67,6.05,6.63], width, alpha=0.5)

plt.ylabel('Proportion')
plt.title('Ratio of robotic comment')
plt.xticks(range(4), ('Haze on weekend', 'No haze on weekend', 'Haze on weekday', 'No haze on weekday'))
plt.yticks(np.arange(0, 10, 10))
plt.show()

'''评论的平均长度'''
beijing_comment_weekday['content_x'] = beijing_comment_weekday['content_x'].apply(lambda x: str(x).strip('@').strip('回复') if pd.notnull else x)
beijing_comment_weekday['word_lenth'] = beijing_comment_weekday['content_x'].map(lambda x: 0 if pd.isnull(x) else len(str(x)))
word_lenth1 = np.mean(beijing_comment_weekday['word_lenth'][beijing_comment_weekday.haze==1])
print('雾霾时间段北京地区工作的评论的平均长度：%.2f' % word_lenth1)
word_lenth1 = np.mean(beijing_comment_weekday['word_lenth'][beijing_comment_weekday.haze==0])
print('非雾霾时间段北京地区工作的评论的平均长度：%.2f' % word_lenth1)
beijing_comment_weekend['content_x'] = beijing_comment_weekend['content_x'].apply(lambda x: str(x).strip('@').strip('回复') if pd.notnull else x)
beijing_comment_weekend['word_lenth'] = beijing_comment_weekend['content_x'].map(lambda x: 0 if pd.isnull(x) else len(str(x)))
word_lenth1 = np.mean(beijing_comment_weekend['word_lenth'][beijing_comment_weekend.haze==1])
print('雾霾时间段北京地区周末的评论的平均长度：%.2f' % word_lenth1)
word_lenth1 = np.mean(beijing_comment_weekend['word_lenth'][beijing_comment_weekend.haze==0])
print('非雾霾时间段北京地区周末的评论的平均长度：%.2f' % word_lenth1)


plt.bar(range(4), [24.34,18.53,18.25,19.53], width, alpha=0.5)

plt.ylabel('Counts')
plt.title('Average length of comment')
plt.xticks(range(4), ('Haze on weekend', 'No haze on weekend', 'Haze on weekday', 'No haze on weekday'))
plt.yticks(np.arange(0, 20, 10))
plt.show()

