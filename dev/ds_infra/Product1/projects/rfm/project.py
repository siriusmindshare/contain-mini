import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import base64
import squarify
from io import BytesIO
import seaborn as sns
import sys
import datetime as dt
import csv
from flask import request, jsonify
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from yellowbrick.cluster import KElbowVisualizer
import ds_infra.api.rest.common.db
sys.path.append('./')
import warnings
warnings.filterwarnings("ignore")
from ds_infra.api.wrapper.abstractproject import AbstractProject
from ds_infra.Product1.projects.rfm.utils import read_from_db, write_to_db, local_global_mean
import os

class RFMPredict(AbstractProject):

    def __init__(self, query, conn, test=False):
        if query['request_type'] == "async-train":
            # submit train call
            super().__init__(query, conn, test)
        elif query['request_type']== "async-predict":
            # submit predict call
            super().__init__(query, conn, test)
        else:
            # sync score
            super().__init__(query, conn, test, query['workflow_name_url'])
        self.df = None
        self.conn = conn
        self.query = query
    """
     Custom Train logic for RF model for SL 
    """

    def train(self, test=False):
        pass

    # Returns the prediction of SL performance given a new text
    def predict(self, test=False):
        return Main(self.conn, self.query).api()


    # Pre-processes ETL data.
    # Identifies RPL, cleanses subject line words, calculate overall SL metrics
    def preprocess(self, test=False):
        pass

class SklearnStart():
    def __init__(self, df, RFM_df3):
        self.RFM_log = df
        self.RFM_df3 = RFM_df3
    
    def preprocessing(self):
        scaler= StandardScaler()

        RFM_log_scaled= scaler.fit_transform(self.RFM_log)
        RFM_log_scaled_df= pd.DataFrame(RFM_log_scaled)
        RFM_log_scaled_df.columns = ['recency', 'frequency', 'monetary']
        self.RFM_log_scaled_df = RFM_log_scaled_df

        k_means = KMeans()
        elbow = KElbowVisualizer(k_means, k=(2, 20))
        elbow.fit(RFM_log_scaled_df)
        # elbow.show()    
        kmeans= KMeans(n_clusters=elbow.elbow_value_)
        kmeans.fit(RFM_log_scaled_df)

        RFM_log_scaled_df['Cluster']= kmeans.labels_
        self.RFM_log_scaled_df = RFM_log_scaled_df

        RFM_df4= self.RFM_df3.copy()
        RFM_df4['Cluster'] = kmeans.labels_ 
        RFM_df4.rename(columns = {'Recency':'recency', 'Frequency': 'frequency', 'Monetary': 'monetary', 'Cluster': 'cluster'}, inplace = True)
        return RFM_df4

#TODO REMOVE MONETARY 
class Main():
    def __init__(self, conn, query):
        self.conn = conn
        self.query = query
        # self.cursor = self.conn.cursor()
    
    def mergeDf(self, customers_df,payments_df,  orders_df):
        merged_df= pd.merge(customers_df, orders_df, on="customer_id")
        #merged_df= merged_df.merge(reviews_df, on="order_id")
        #merged_df= merged_df.merge(items_df, on="order_id")
        #merged_df= merged_df.merge(products_df, on="product_id")
        merged_df= merged_df.merge(payments_df, on="order_id")
        #merged_df= merged_df.merge(sellers_df, on='seller_id')
        #merged_df= merged_df.merge(category_translation_df, on='product_category_name')

        self.merged_df = merged_df

    def dropNa(self, dataset):
        dataset = dataset.dropna(axis=0)
        dataset = dataset.drop(dataset[dataset.duplicated()].index, axis=0)
        
        return dataset

    def load_dataset(self):
        accountId = self.query.get('accountId', None)
        customers_df= read_from_db(sql="SELECT * FROM rfm_customers_data WHERE account_id={accountId}".format(accountId=accountId),
            con=self.conn,
            columns=["account_id","customer_id", "customer_unique_id", "customer_zip_code_prefix", "customer_city", "customer_state"])
        
        # geolocation_df= read_from_db(sql="SELECT * FROM rfm_geolocation_data WHERE account_id={accountId}".format(accountId=accountId),
        #     con=self.conn,
        #     columns=['account_id','geolocation_zip_code_prefix','geolocation_lat','geolocation_lng','geolocation_city','geolocation_state'])        
        
        # items_df= read_from_db(sql="SELECT * FROM rfm_order_item_data WHERE account_id={accountId}".format(accountId=accountId),
        #     con=self.conn,
        #     columns=['account_id','order_id', 'order_item_id', 'product_id', 'seller_id', 'shipping_limit_date', 'price', 'freight_value'])
        
        payments_df= read_from_db(sql="SELECT * FROM rfm_order_payment_data WHERE account_id={accountId}".format(accountId=accountId),
            con=self.conn,
            columns=['account_id','order_id', 'payment_sequential', 'payment_type', 'payment_installments', 'payment_value'])
        
        # reviews_df= read_from_db(sql="SELECT * FROM rfm_order_review_data WHERE account_id={accountId}".format(accountId=accountId),
        #     con=self.conn,
        #     columns=['account_id','review_id','order_id','review_score','review_comment_title','review_comment_message','review_creation_date', 'review_answer_timestamp'])
        
        orders_df= read_from_db(sql="SELECT * FROM rfm_order_data WHERE account_id={accountId}".format(accountId=accountId),
            con=self.conn,
            columns=['account_id','order_id','customer_id','order_status','order_purchase_timestamp','order_approved_at','order_delivered_carrier_date','order_delivered_customer_date','order_estimated_delivery_date'])
        
        # products_df= read_from_db(sql="SELECT * FROM rfm_product_data WHERE account_id={accountId}".format(accountId=accountId),
        #     con=self.conn,
        #     columns=['account_id','product_id','product_category_name','product_name_lenght','product_description_lenght','product_photos_qty','product_weight_g','product_length_cm','product_height_cm','product_width_cm'])
        
        # sellers_df= read_from_db(sql="SELECT * FROM rfm_seller_data WHERE account_id={accountId}".format(accountId=accountId),
        #     con=self.conn,
        #     columns=['account_id','seller_id', 'seller_zip_code_prefix', 'seller_city', 'seller_state'])
        
        # category_translation_df= read_from_db(sql="SELECT * FROM rfm_product_category_data WHERE account_id={accountId}".format(accountId=accountId),
        #     con=self.conn,
        #     columns=['account_id','product_category_name', 'product_category_name_english'])

        customers_df = customers_df.loc[:,customers_df.columns!='account_id']
        # geolocation_df = geolocation_df.loc[:,geolocation_df.columns!='account_id']
        # items_df = items_df.loc[:,items_df.columns!='account_id']
        payments_df = payments_df.loc[:,payments_df.columns!='account_id']
        #reviews_df = reviews_df.loc[:,reviews_df.columns!='account_id']
        orders_df = orders_df.loc[:,orders_df.columns!='account_id']
        #products_df = products_df.loc[:,products_df.columns!='account_id']
        #sellers_df = sellers_df.loc[:,sellers_df.columns!='account_id']
        #category_translation_df = category_translation_df.loc[:,category_translation_df.columns!='account_id']
        

        customers_df = self.dropNa(customers_df)
        orders_df = self.dropNa(orders_df)
        #geolocation_df = self.dropNa(geolocation_df)
        #items_df = self.dropNa(items_df)
        payments_df = self.dropNa(payments_df)
        #reviews_df = self.dropNa(reviews_df)
        #products_df = self.dropNa(products_df)
        #sellers_df = self.dropNa(sellers_df)
        #category_translation_df = self.dropNa(category_translation_df)
        
        #self.mergeDf(customers_df, geolocation_df, items_df, payments_df, reviews_df, orders_df, products_df, sellers_df, category_translation_df)
        self.mergeDf(customers_df, payments_df, orders_df)

    def convertTime(self):
        time_columns= ['order_purchase_timestamp', 'order_approved_at','order_delivered_carrier_date','order_delivered_customer_date',
               'order_estimated_delivery_date'] #,'review_creation_date', 'review_answer_timestamp', 'shipping_limit_date']
        
        self.merged_df[time_columns]=self.merged_df[time_columns].apply(pd.to_datetime)

    def recencyDf(self):
        present_day = self.merged_df['order_purchase_timestamp'].max() + dt.timedelta(days=2)
        recency_df= pd.DataFrame(self.merged_df.groupby(by='customer_unique_id', as_index=False)['order_purchase_timestamp'].max())
        recency_df['Recency']= recency_df['order_purchase_timestamp'].apply(lambda x: (present_day - x).days)
        self.recency_df = recency_df
    
    def frequencyDf(self):
        frequency_df = pd.DataFrame(self.merged_df.groupby(["customer_unique_id"]).agg({"order_id":"nunique"}).reset_index())
        frequency_df.rename(columns={"order_id":"Frequency"}, inplace=True)
        self.frequency_df = frequency_df
    
    def monetaryDf(self):
        self.monetary_df = self.merged_df.groupby('customer_unique_id', as_index=False)['payment_value'].sum()
        self.monetary_df.columns = ['customer_unique_id', 'Monetary']
        return self.monetary_df

    def rfDf(self):
        RF_df = self.recency_df.merge(self.frequency_df, on='customer_unique_id')
        RFM_df = RF_df.merge(self.monetary_df, on='customer_unique_id').drop(columns='order_purchase_timestamp')
        return RFM_df

    def remove_outlier(self, df_in, col_name):
        q1 = df_in[col_name].quantile(0.05)
        q3 = df_in[col_name].quantile(0.95)
        iqr = q3-q1     
        fence_low  = q1-1.5*iqr
        fence_high = q3+1.5*iqr
        index_outliers= df_in.loc[(df_in[col_name] < fence_low) | (df_in[col_name] > fence_high)].index
        df_in= pd.DataFrame(df_in.drop(index_outliers.to_list(), axis=0))
        return df_in

    def CreatingRFMSegments(self):
        self.RFM_df2["recency_score"]  = pd.qcut(self.RFM_df2['Recency'], 5, labels=[5, 4, 3, 2, 1])
        self.RFM_df2["frequency_score"]= pd.qcut(self.RFM_df2['Frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
        self.RFM_df2["monetary_score"] = pd.qcut(self.RFM_df2['Monetary'], 5, labels=[1, 2, 3, 4, 5])
        self.RFM_df2['RFM_SCORE'] = self.RFM_df2.recency_score.astype(str)+ self.RFM_df2.frequency_score.astype(str) + self.RFM_df2.monetary_score.astype(str)

        seg_map= {
                r'111|112|121|131|141|151': 'Lost customers',
                r'332|322|233|232|223|222|132|123|122|212|211': 'Hibernating customers', 
                r'155|154|144|214|215|115|114|113': 'Cannot Lose Them',
                r'255|254|245|244|253|252|243|242|235|234|225|224|153|152|145|143|142|135|134|133|125|124': 'At Risk',
                r'331|321|312|221|213|231|241|251': 'About To Sleep',
                r'535|534|443|434|343|334|325|324': 'Need Attention',
                r'525|524|523|522|521|515|514|513|425|424|413|414|415|315|314|313': 'Promising',
                r'512|511|422|421|412|411|311': 'New Customers',
                r'553|551|552|541|542|533|532|531|452|451|442|441|431|453|433|432|423|353|352|351|342|341|333|323': 'Potential Loyalist',
                r'543|444|435|355|354|345|344|335': 'Loyal',
                r'555|554|544|545|454|455|445': 'Champions'
            }
        
        self.RFM_df2['Segment'] = self.RFM_df2['recency_score'].astype(str) + self.RFM_df2['frequency_score'].astype(str) + self.RFM_df2['monetary_score'].astype(str)
        self.RFM_df2['Segment'] = self.RFM_df2['Segment'].replace(seg_map, regex=True)

        RFMStats = self.RFM_df2[["Segment", "Recency", "Frequency", "Monetary"]].groupby("Segment").agg(['mean','median', 'min', 'max', 'count'])
        RFMStats['Ratio']= (100*RFMStats['Monetary']["count"]/RFMStats['Monetary']["count"].sum()).round(2)

        self.RFMStats = RFMStats
    
    def clustering_withK_Means(self):
        RFM_df3= self.RFM_df2.drop(["recency_score", "frequency_score", "monetary_score", "RFM_SCORE", "Segment"], axis=1)
        self.RFM_df3 = RFM_df3

    def rfmLog(self):
        RFM_log= self.RFM_df3.copy()
        for i in RFM_log.columns[1:]:
            RFM_log[i] = np.log10(RFM_log[i])
        
        return RFM_log

    def api(self):
        try:
            self.load_dataset()
            self.convertTime()
            self.recencyDf()
            self.frequencyDf()
            self.monetaryDf()
            RFM_df = self.rfDf()
            df_in = self.remove_outlier(RFM_df, 'Monetary')
            df_in = self.remove_outlier(df_in, 'Recency')
            print("len df_in %s" % len(df_in))
            self.RFM_df2= df_in.set_index('customer_unique_id')
            self.CreatingRFMSegments()
            self.clustering_withK_Means()
            rfmLog = self.rfmLog()
            print("len rfmlog %s" % len(rfmLog))
            obj = SklearnStart(rfmLog, self.RFM_df3)
            processed_df = obj.preprocessing()
            processed_df = processed_df.rename_axis('customer_unique_id').reset_index()
            processed_df = processed_df.reset_index(drop=True)
            print("processed df 1 %s" % len(processed_df))
            accountId = self.query.get('accountId', None)
            processed_df['account_id'] = ['{accountId}'.format(accountId=accountId)]*len(processed_df)
            first_column = processed_df.pop('account_id')
            processed_df.insert(0, 'account_id', first_column)
            print("processed df 2 %s" % len(processed_df))

            write_to_db(sql="insert into rfm_output_data(account_id,customer_unique_id, recency, frequency, monetary, cluster_data) values (:1, :2, :3, :4, :5, :6)",
                    con=self.conn,
                    df=processed_df)
            print("Finished writing to db %s " % len(processed_df))
        except Exception as e:
            return jsonify({"message":str(e), "status":False})


def get_rfm_output_data():
    accountId = request.args.get("accountId", None)
    with open('config/ds_infra.env') as f:
        for line in f:
            key, value = line.strip().split('=')
            os.environ[key] = value
    user = os.environ.get("USER")
    host = os.environ.get("HOST")
    service = os.environ.get("SERVICE")
    port = os.environ.get("PORT")
    password = os.environ.get("PASSWORD")
    conn = ds_infra.api.rest.common.db.connect(user=user, host=host, service=service, port=port,db_encrypted_pwd = password,admin=False,db_dict = None,test=False)

    RFM_log_scaled_df= read_from_db(sql="SELECT * FROM rfm_output_data WHERE account_id={accountId}".format(accountId=accountId),
        con=conn,
        columns=['account_id','customer_unique_id','recency','frequency','monetary','cluster_data'])
    


    # RFM_log_scaled_df = RFM_log_scaled_df[RFM_log_scaled_df['account_id']=='123']
    RFM_log_scaled_df = RFM_log_scaled_df.loc[:,RFM_log_scaled_df.columns!='account_id']
    # RFM_df4 = RFM_log_scaled_df
    # customer_unique_id = RFM_log_scaled_df['customer_unique_id']
    del RFM_log_scaled_df['customer_unique_id']
    k_means = KMeans()
    elbow = KElbowVisualizer(k_means, k=(2, 20))
    elbow.fit(RFM_log_scaled_df)

    kmeans= KMeans(n_clusters=elbow.elbow_value_)
    kmeans.fit(RFM_log_scaled_df)
    RFM_log_scaled_df['Cluster'] = kmeans.labels_

    df_new = RFM_log_scaled_df.groupby(['Cluster']).agg({
            'recency'  : ['mean','median', 'min', 'max'],
            'frequency': ['mean','median', 'min', 'max'],
            'monetary' : ['mean','median', 'min', 'max', 'count']
        }).round(0)
    
    rfm_clusters_stat = df_new.style.background_gradient(cmap='YlGnBu')

    RFM_stats= pd.DataFrame(df_new)
    fig = plt.figure(figsize=(10, 6))
    squarify.plot(sizes=RFM_stats["monetary"]["count"], label=RFM_stats.index, color=["b","g","r","m","c", "y"], alpha=0.7)
    plt.suptitle("Segments of Customers", fontsize=25)
    tmpfile = BytesIO()
    fig.savefig(tmpfile, format='png')
    segments = base64.b64encode(tmpfile.getvalue()).decode('utf-8')

    return {"status": True, 'rfm_clusters_stat': rfm_clusters_stat.render(), 'segments': segments}