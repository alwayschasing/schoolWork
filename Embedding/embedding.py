#!/usr/bin/env python
# coding=utf-8

import numpy as np
import csv
import tensorflow as tf
import cPickle as pickle
import time


def getSkipGramData():
    print "start getSkipGramData"
    #文件每一行是基于用户的数据，首项为用户编号
    start = time.time()
    fp = open("../data/ml-1m/userbased.train.csv","r")
    reader = csv.reader(fp)
    #用于skip-gram模型训练的数据为二维，第二维是一个[target,content]的pair，
    #因为skip-gram是用target预测content

    data = list() 

    maxitem = 0
    for line in reader:
        for i in line[1:]:
            #if maxitem < i:
                #maxitem = i
            for j in line[1:]:
                if i == j:
                    continue
                else:
                    data.append([i,j])
    fp.close()
    print "get the skip-gram data"
    #返回物品最大索引，即物品集的大小与训练数据
    print maxitem
    print data[0]
    savefp = open("../data/ml-1m/embedding/data.csv","w")
    writer = csv.writer(savefp) 
    writer.writerow([maxitem])
    for line in data:
        writer.writerow(line)
    savefp.close()
    end = time.time()
    print "get data has run %d miniutes"%((end-start)/60)
    return maxitem,data 

def getCBOWData():
    #文件每一行是基于用户的数据，首项为用户编号
    fp = open("../data/ml-1m/userbased.train.csv","r")
    reader = csv.reader(fp)
    data = list()
    maxitem = 0

    pass

class EmbeddingModel(object):
    #num_sampled为负采样的数量
    def __init__(self,batch_size,item_vocabulary_size,embedding_size,num_sampled):

        self.train_inputs = tf.placeholder(tf.int32, shape=[batch_size])
        self.train_labels = tf.placeholder(tf.int32, shape=[batch_size,1])

        self.embeddings = tf.Variable(
            tf.random_uniform([item_vocabulary_size,embedding_size],-1.0,1.0)
            )

        embed = tf.nn.embedding_lookup(self.embeddings,self.train_inputs)

        nce_weights = tf.Variable(
            tf.random_uniform([item_vocabulary_size,embedding_size],-1.0,1.0)
            )

        nce_biases = tf.Variable(tf.zeros([item_vocabulary_size]))

        self.loss = tf.reduce_mean(tf.nn.nce_loss(nce_weights,nce_biases,embed,self.train_labels,num_sampled,item_vocabulary_size))


    def getEmbeddings(self,sess,training_epoch,inputs,labels,learning_rate):
        #初始化所有变量 

        train_op = tf.train.AdamOptimizer(learning_rate).minimize(self.loss)
        tf.global_variables_initializer().run()
        
        for i in range(training_epoch):

            _,loss_val = sess.run([train_op,self.loss],feed_dict={self.train_inputs:inputs,self.train_labels:labels})

            print "the %d epoch loss is %f"%(i,loss_val)

        return self.embeddings.eval()

def main():
    #预备训练数据，设置训练参数
    item_vocabulary_size,train_data = getSkipGramData()
    train_data = np.asarray(train_data,dtype=np.int32)
    item_vocabulary_size = 3953
    start = time.time()
    #train_data = []
    #with open("../data/ml-1m/embedding/data.csv","r") as fp:
        #reader = csv.reader(fp)
        #lines = list(reader)
        #train_data = lines[1:]
    print item_vocabulary_size
    batch_size = len(train_data)
    embedding_size = 10
    num_sampled = 100
    print "set parameters"
    emb = EmbeddingModel(batch_size,item_vocabulary_size,embedding_size,num_sampled)

    train_epoch = 100
    learning_rate = 0.05

    print "has build the model"
    with tf.Session() as sess:
        embeddings = emb.getEmbeddings(sess,train_epoch,train_data[:,0],train_data[:,1],learning_rate) 

    end = time.time() 
    print "train and predict run %d miniutes"%((end-start)/60)
    savefp = open("../data/ml-1m/embeddings","wb")
    pickle.dump(embeddings,savefp)
    savefp.close()

if __name__ == "__main__":
    main()
    #getSkipGramData()
        
    

    

