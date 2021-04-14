import pandas as pd
import os
import re
import json
import matplotlib.pyplot as plt
#读取一卡通数据
def read_data_yikatong(file_name,isonboard):
    if isonboard:
        path = os.getcwd()+'/ykt_onboard/'+file_name
    else:
        path = os.getcwd()+'/ykt_offboard/'+file_name
    data = pd.read_csv(path)
    return data

#分类公交车数据和地铁数据
#参数为dataframe和分类依据
def classify_data(df):
    #df_group = df.groupby(by='type')
    #Cata_list = list(df_group.groups.keys())
    #for cata in Cata_list:
        #temp_df = df[df['type']==cata]
    df_bus = df[df['type'] == "公交"]
    df_metro = df[df['type'] == "地铁"]
    return df_bus,df_metro
#处理小时数据
def solve_data_hour(df,type,scale,lng,lat,station_ls,date,board):
    df_group_hour_station = df.groupby(['timezone','station_name'])
    cnt = df_group_hour_station['popnum'].sum()
    for i in range(24):
        if i < 9:
            time_slot = '0'+str(i)+':00-'+'0'+str(i+1)+':00'
        elif i == 9:
            time_slot = '09:00-10:00'
        else:
            time_slot = str(i)+':00-'+str(i+1)+':00'
        #解析日期
        year = date[0:4]
        month = date[4:6]
        day = date[6:8]
        cwd = os.getcwd()
        #生成txt文件，暂时用于js读取
        # cur_dir_txt = cwd+'/'+year+'/'+month+'/'+day+'/'+board
        # if not os.path.exists(cur_dir_txt):
        #     os.makedirs(cur_dir_txt)
        # with open(cur_dir_txt+'/'+type+'_'+date+'_'+str(i)+".txt", "w") as f:
        #     for station in station_ls:
        #         if (time_slot,station) in cnt.index:
        #             f.write(' {"lat": ' + str(lat[station]) + ', "lng":' + str(lng[station])+ ', "count": '+str(cnt[time_slot,station])+'},'+'\r\n')
        #         else:
        #             f.write(' {"lat": '+ str(lat[station]) +', "lng":' + str(lng[station])+', "count": 0},'+'\r\n')

        #生成csv文件，方便以后处理使用
        # cur_dir_csv = cwd+'/'+year+'_csv'+'/'+month+'/'+day+'/'+board
        # if not os.path.exists(cur_dir_csv):
        #     os.makedirs(cur_dir_csv)
        # contents = []
        # for station in station_ls:
        #     data_ls = []
        #     data_ls.append(station)
        #     data_ls.append(lat[station])
        #     data_ls.append(lng[station])
        #     if (time_slot,station) in cnt.index:
        #         data_ls.append(cnt[time_slot, station])
        #     else:
        #         data_ls.append(0)
        #     contents.append(data_ls)
        # df = pd.DataFrame(contents)
        # df.columns = ["station_name",'lat','lng','pop_num']
        # df.to_csv(cur_dir_csv+'/'+type+'_'+date+'_'+str(i)+".csv",index=False)

        #生成json文件，供给网页读取
        cur_dir_json = cwd+'/'+year+'_json'+'/'+month+'/'+day+'/'+board
        if not os.path.exists(cur_dir_json):
            os.makedirs(cur_dir_json)
        dicts = {}
        contents = []
        for station in station_ls:
            content = []
            content.append(station)
            content.append(str(lat[station]))
            content.append(str(lng[station]))
            if(time_slot,station) in cnt.index:
                content.append(str(cnt[time_slot,station]))
            else:
                content.append("0")
            contents.append(content)
        dicts["data"] = contents
        file_name = cur_dir_json+'/'+type+'_'+date+'_'+str(i)+".json"
        file = open(file_name, 'w', encoding='utf-8')
        json.dump(dicts, file, ensure_ascii=False)


def solve_data_hour_pic(df,type,date,board):
    df_group_hour = df.groupby(['timezone'])
    cnt = df_group_hour['popnum'].sum()
    res = [0 for i in range(24)]
    for i in range(24):
        if i < 9:
            time_slot = '0'+str(i)+':00-'+'0'+str(i+1)+':00'
        elif i == 9:
            time_slot = '09:00-10:00'
        else:
            time_slot = str(i)+':00-'+str(i+1)+':00'

        if time_slot in cnt.index:
            res[i] = cnt[time_slot]
        else:
            res[i] = 0
    return res

#文件名为天
#
def solve_data_day(df,type,scale,date,board):
    #以每个站点划分数据
    #粗粒度，站点聚合，经纬度均值代表该聚类点经纬度
    if scale == 'large':
        df_group_station = df.groupby(by = 'station_name')
        #生成站点列表
        station_ls = list(df_group_station.groups.keys())
        #经纬度列表
        lng = df_group_station['lng'].mean()
        lat = df_group_station['lat'].mean()
        #lng_lat = pd.merge(lat,lng,on = 'station_name')
        #print(lng_lat)
        print(date)
        #solve_data_hour(df,type,scale,lng,lat,station_ls,date,board)
        y_data = solve_data_hour_pic(df,type,date,board)
        #绘图并保存
        x_data = [str(i) for i in range(24)]
        plt.xlabel("time_slot")
        plt.ylabel("flow")
        plt.plot(x_data, y_data, color='red', linewidth=2.0)
        pic_name = date + '_' +board + '_' + type + ".jpg"
        plt.savefig("day_fig/"+pic_name)
        plt.clf()

        #公交数据处理
        if type == "bus":
            pass
        #地铁数据处理
        else:
            pass
    else:
        pass

#文件名为月和年
def solve_data_month_and_year(df,type,scale,board):
    df_group_date = df.groupby(by='date')
    # 生成站点列表
    date_ls = list(df_group_date.groups.keys())
    for date in date_ls:
        temp_df = df[df['date'] == date]
        solve_data_day(temp_df,type,scale,str(date),board)

if __name__ == '__main__':

    #参数配置
    scale = 'large'
    year = '2020'
    month = '09'
    day = '03'
    date = year+month+day
    if os.path.exists('day_fig'):
        pass
    else:
        os.mkdir('day_fig')
    #参数配置

    #测试区
    # test_data = read_data_yikatong("xicheng"+board+"num"+date+".csv",onboard)
    # df_bus,df_metro = classify_data(test_data)
    # solve_data_day(df_bus,'bus',scale)
    #测试区
    #solve_data(df_metro,'metro',scale)

    #业务区
    for onboard in [True,False]:
        path = os.getcwd()
        if onboard:
            path = path+"/ykt_onboard"
            board = 'onboard'
        else:
            path = path+"/ykt_offboard"
            board = 'offboard'
        files = os.listdir(path)
        for file in files:
            date = re.sub("\D", "", file)
            # if date == '2018':
            #     my_data = read_data_yikatong(file,onboard)
            #     df_bus,df_metro = classify_data(my_data)
            #     solve_data_month_and_year(df_bus,'bus',scale,board)
            #     solve_data_month_and_year(df_metro,'metro',scale,board)

            if date != '':
                my_data = read_data_yikatong(file,onboard)
                df_bus,df_metro = classify_data(my_data)
            else:
                continue
            if len(str(date)) == 8:
                solve_data_day(df_bus,'bus',scale,date,board)
                solve_data_day(df_metro,'metro',scale,date,board)
            else:
                solve_data_month_and_year(df_bus,'bus',scale,board)
                solve_data_month_and_year(df_metro,'metro',scale,board)
