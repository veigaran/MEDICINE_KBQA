#!/usr/bin/env python  
# -*- coding:utf-8 _*-  
"""
@Time:2020-06-09 14:36
@Author:Veigar
@File: Params.py
@Github:https://github.com/veigaran
"""
import os
import pickle
import ahocorasick
import joblib


class Params:
    def __init__(self):
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        # 路径
        self.vocab_path = os.path.join(cur_dir, 'data/vocab.txt')
        self.stopwords_path = os.path.join(cur_dir, 'data/stop_words.utf8')
        self.word2vec_path = os.path.join(cur_dir, 'data/merge_sgns_bigram_char300.txt')
        self.stopwords = [w.strip() for w in open(self.stopwords_path, 'r', encoding='utf8') if w.strip()]

        # 意图分类模型文件
        self.tfidf_path = os.path.join(cur_dir, 'model/tf.pkl')
        self.nb_test_path = os.path.join(cur_dir, 'model/SVM.m')  # 测试nb模型
        self.tfidf_model = pickle.load(open(self.tfidf_path, "rb"))
        self.nb_model = joblib.load(self.nb_test_path)

        self.medicine_path = os.path.join(cur_dir, 'data/药物.txt')
        self.generic_path = os.path.join(cur_dir, 'data/通用名称.txt')
        self.cate_path = os.path.join(cur_dir, 'data/类别.txt')
        self.indication_path = os.path.join(cur_dir, 'data/适应症.txt')
        self.disease_path = os.path.join(cur_dir, 'data/disease_vocab.txt')
        self.alias_path = os.path.join(cur_dir, 'data/alias_vocab.txt')

        self.medicine_entities = [w.strip() for w in open(self.medicine_path, encoding='utf8') if w.strip()]
        self.generic_entities = [w.strip() for w in open(self.generic_path, encoding='utf8') if w.strip()]
        self.cate_entities = [w.strip() for w in open(self.cate_path, encoding='utf8') if w.strip()]
        self.indication_entities = [w.strip() for w in open(self.indication_path, encoding='utf8') if w.strip()]
        self.disease_entities = [w.strip() for w in open(self.disease_path, encoding='utf8') if w.strip()]
        self.alias_entities = [w.strip() for w in open(self.alias_path, encoding='utf8') if w.strip()]
        self.region_words = list(set(self.medicine_entities + self.generic_entities + self.indication_entities))

        # 构造领域actree
        self.medicine_tree = self.build_actree(list(set(self.medicine_entities)))
        self.generic_tree = self.build_actree(list(set(self.generic_entities)))
        self.cate_tree = self.build_actree(list(set(self.cate_entities)))
        self.indication_tree = self.build_actree(list(set(self.indication_entities)))
        self.disease_tree = self.build_actree(list(set(self.disease_entities)))
        self.alias_tree = self.build_actree(list(set(self.alias_entities)))

        self.name_qwds = ['英文名是什么', '通用名是什么', '一般叫什么', '哪些名字', '什么名字']
        self.cate_qwds = ['属于哪一类', '哪一类', '什么种类', '属于哪些种类', '种类']
        self.cureway_qwds = ['药', '药品', '用药', '胶囊', '口服液', '炎片', '吃什么药', '用什么药', '怎么办',
                             '买什么药', '怎么治疗', '如何医治', '怎么医治', '怎么治', '怎么医', '如何治',
                             '医治方式', '疗法', '咋治', '咋办', '咋治', '治疗方法']  # 询问治疗方法

        self.dosage_qwds = ['吃几次', '吃多少', '吃几顿', '什么时候吃', '服用', '怎么吃', '吃']
        self.cautions_qwds = ['注意', '注意什么', '什么注意事项']
        self.symptom_qwds = ['适用什么症状', '哪些适用症状', '适用症状有哪些', '是什么', '适用症状是什么', '什么表征', '哪些表征', '表征是什么', ]  # 询问症状

    def build_actree(self, wordlist):
        """
        构造actree，加速过滤
        :param wordlist:
        :return:
        """
        actree = ahocorasick.Automaton()
        # 向树中添加单词
        for index, word in enumerate(wordlist):
            actree.add_word(word, (index, word))
        actree.make_automaton()
        return actree
