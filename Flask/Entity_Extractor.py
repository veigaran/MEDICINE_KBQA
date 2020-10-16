#!/usr/bin/env python3
# coding: utf-8
import os
import pickle
import ahocorasick
from sklearn.externals import joblib
import jieba
import numpy as np


class EntityExtractor:
    def __init__(self):
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        # 路径
        self.vocab_path = os.path.join(cur_dir, 'data/vocab.txt')
        self.stopwords_path = os.path.join(cur_dir, 'data/stopword.txt')
        self.word2vec_path = os.path.join(cur_dir, 'data/merge_sgns_bigram_char300.txt')
        self.stopwords = [w.strip() for w in open(self.stopwords_path, 'r', encoding='utf8') if w.strip()]

        # 意图分类模型文件
        self.tfidf_path = os.path.join(cur_dir, 'model/tf.pkl')
        self.nb_test_path = os.path.join(cur_dir, 'model/NB.m')  # 测试nb模型
        self.tfidf_model = pickle.load(open(self.tfidf_path, "rb"))
        self.nb_model = joblib.load(self.nb_test_path)

        self.medicine_path = os.path.join(cur_dir, 'data/药物.txt')
        self.generic_path = os.path.join(cur_dir, 'data/通用名称.txt')
        self.cate_path = os.path.join(cur_dir, 'data/类别.txt')
        self.indication_path = os.path.join(cur_dir, 'data/适应症.txt')

        self.medicine_entities = [w.strip() for w in open(self.medicine_path, encoding='utf8') if w.strip()]
        self.generic_entities = [w.strip() for w in open(self.generic_path, encoding='utf8') if w.strip()]
        self.cate_entities = [w.strip() for w in open(self.cate_path, encoding='utf8') if w.strip()]
        self.indication_entities = [w.strip() for w in open(self.indication_path, encoding='utf8') if w.strip()]

        self.region_words = list(set(self.medicine_entities + self.generic_entities + self.indication_entities))

        # 构造领域actree
        self.medicine_tree = self.build_actree(list(set(self.medicine_entities)))
        self.generic_tree = self.build_actree(list(set(self.generic_entities)))
        self.cate_tree = self.build_actree(list(set(self.cate_entities)))
        self.indication_tree = self.build_actree(list(set(self.indication_entities)))

        self.name_qwds = ['英文名是什么', '通用名是什么', '一般叫什么', '哪些名字', '什么名字']
        self.cate_qwds = ['属于哪一类', '哪一类', '什么种类', '属于哪些种类', '种类']
        self.indication_qwds = ['吃什么药', '买什么药', '用什么药', '药', '用药', '怎么治', '药物']
        self.dosage_qwds = ['吃几次', '吃多少', '吃几顿', '什么时候吃', '服用', '怎么吃', '吃']
        self.cautions_qwds = ['注意', '注意什么', '什么注意事项']
        self.symptom_qwds = ['适用什么症状', '哪些适用症状', '适用症状有哪些', '适用症状是什么', '什么表征', '哪些表征', '表征是什么', ]  # 询问症状

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

    def entity_reg(self, question):
        """
        模式匹配, 得到匹配的词和类型。如药物、通用名、类别、适应症
        :param question:str
        :return:
        """
        self.result = {}

        for i in self.medicine_tree.iter(question):
            word = i[1][1]
            if "Medicine" not in self.result:
                self.result["Medicine"] = [word]
            else:
                self.result["Medicine"].append(word)

        for i in self.generic_tree.iter(question):
            word = i[1][1]
            if "genericNameFormat" not in self.result:
                self.result["genericNameFormat"] = [word]
            else:
                self.result["genericNameFormat"].append(word)

        for i in self.cate_tree.iter(question):
            wd = i[1][1]
            if "list_cate" not in self.result:
                self.result["list_cate"] = [wd]
            else:
                self.result["list_cate"].append(wd)

        for i in self.indication_tree.iter(question):
            wd = i[1][1]
            if "indications" not in self.result:
                self.result["indications"] = [wd]
            else:
                self.result["indications"].append(wd)

        return self.result

    def find_sim_words(self, question):
        """
        当全匹配失败时，就采用相似度计算来找相似的词
        :param question:
        :return:
        """
        import re
        import string
        from gensim.models import KeyedVectors

        jieba.load_userdict(self.vocab_path)
        self.model = KeyedVectors.load_word2vec_format(self.word2vec_path, binary=False)

        sentence = re.sub("[{}]", re.escape(string.punctuation), question)
        sentence = re.sub("[，。‘’；：？、！【】]", " ", sentence)
        sentence = sentence.strip()

        words = [w.strip() for w in jieba.cut(sentence) if w.strip() not in self.stopwords and len(w.strip()) >= 2]

        alist = []

        for word in words:
            temp = [self.medicine_entities, self.generic_entities, self.cate_entities, self.indication_entities]
            for i in range(len(temp)):
                flag = ''
                if i == 0:
                    flag = "Medicine"
                elif i == 1:
                    flag = "genericNameFormat"
                elif i == 2:
                    flag = "list_cate"
                else:
                    flag = "indications"
                scores = self.simCal(word, temp[i], flag)
                alist.extend(scores)
        temp1 = sorted(alist, key=lambda k: k[1], reverse=True)
        if temp1:
            self.result[temp1[0][2]] = [temp1[0][0]]

    def editDistanceDP(self, s1, s2):
        """
        采用DP方法计算编辑距离
        :param s1:
        :param s2:
        :return:
        """
        m = len(s1)
        n = len(s2)
        solution = [[0 for j in range(n + 1)] for i in range(m + 1)]
        for i in range(len(s2) + 1):
            solution[0][i] = i
        for i in range(len(s1) + 1):
            solution[i][0] = i

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i - 1] == s2[j - 1]:
                    solution[i][j] = solution[i - 1][j - 1]
                else:
                    solution[i][j] = 1 + min(solution[i][j - 1], min(solution[i - 1][j],
                                                                     solution[i - 1][j - 1]))
        return solution[m][n]

    def simCal(self, word, entities, flag):
        """
        计算词语和字典中的词的相似度
        相同字符的个数/min(|A|,|B|)   +  余弦相似度
        :param word: str
        :param entities:List
        :return:
        """
        a = len(word)
        scores = []
        for entity in entities:
            sim_num = 0
            b = len(entity)
            c = len(set(entity + word))
            temp = []
            for w in word:
                if w in entity:
                    sim_num += 1
            if sim_num != 0:
                score1 = sim_num / c  # overlap score
                temp.append(score1)
            try:
                score2 = self.model.similarity(word, entity)  # 余弦相似度分数
                temp.append(score2)
            except:
                pass
            score3 = 1 - self.editDistanceDP(word, entity) / (a + b)  # 编辑距离分数
            if score3:
                temp.append(score3)

            score = sum(temp) / len(temp)
            if score >= 0.7:
                scores.append((entity, score, flag))

        scores.sort(key=lambda k: k[1], reverse=True)
        return scores

    def check_words(self, wds, sent):
        """
        基于特征词分类
        :param wds:
        :param sent:
        :return:
        """
        for wd in wds:
            if wd in sent:
                return True
        return False

    def tfidf_features(self, text, vectorizer):
        """
        提取问题的TF-IDF特征
        :param text:
        :param vectorizer:
        :return:
        """
        jieba.load_userdict(self.vocab_path)
        words = [w.strip() for w in jieba.cut(text) if w.strip() and w.strip() not in self.stopwords]
        sents = [' '.join(words)]

        tfidf = vectorizer.transform(sents).toarray()
        return tfidf

    def other_features(self, text):
        """
        提取问题的关键词特征
        :param text:
        :return:
        """
        features = [0] * 6
        for d in self.name_qwds:
            if d in text:
                features[0] += 1

        for s in self.cate_qwds:
            if s in text:
                features[1] += 1

        for c in self.indication_qwds:
            if c in text:
                features[2] += 1

        for c in self.dosage_qwds:
            if c in text:
                features[3] += 1
        for p in self.cautions_qwds:
            if p in text:
                features[4] += 1
        for r in self.symptom_qwds:
            if r in text:
                features[5] += 1
        m = max(features)
        n = min(features)
        normed_features = []
        if m == n:
            normed_features = features
        else:
            for i in features:
                j = (i - n) / (m - n)
                normed_features.append(j)

        return np.array(normed_features)

    def model_predict(self, x, model):
        """
        预测意图
        :param x:
        :param model:
        :return:
        """
        pred = model.predict(x)
        return pred

    # 实体抽取主函数
    def extractor(self, question):
        self.entity_reg(question)
        if not self.result:
            self.find_sim_words(question)

        types = []  # 实体类型
        for v in self.result.keys():
            types.append(v)

        intentions = []  # 查询意图

        # 意图预测
        tfidf_feature = self.tfidf_features(question, self.tfidf_model)
        predicted = self.model_predict(tfidf_feature, self.nb_model)
        intentions.append(predicted[0])

        # 已知药物，查询适用的症状
        if self.check_words(self.symptom_qwds, question) and ('Medicine' in types or 'genericNameFormat' in types):
            intention = "query_symptom"
            if intention not in intentions:
                intentions.append(intention)

        # 已知药物，查询别称
        if self.check_words(self.name_qwds, question) and ('Medicine' in types):
            intention = "query_generic"
            if intention not in intentions:
                intentions.append(intention)

        # 已知药物，查询所属种类
        if self.check_words(self.cate_qwds, question) and ('Medicine' in types or 'genericNameFormat' in types):
            intention = "query_cate"
            if intention not in intentions:
                intentions.append(intention)

        # 已知药物，查询用量
        if self.check_words(self.dosage_qwds, question) and ('Medicine' in types or 'genericNameFormat' in types):
            intention = "query_dosage"
            if intention not in intentions:
                intentions.append(intention)

        # 已知药物，查询注意事项
        if self.check_words(self.cautions_qwds, question) and ('Medicine' in types or 'genericNameFormat' in types):
            intention = "query_caution"
            if intention not in intentions:
                intentions.append(intention)

        # 已知适用症状，查询药物
        if self.check_words(self.indication_qwds, question) and ("indications" in types):
            intention = "query_medicine"
            if intention not in intentions:
                intentions.append(intention)

        # 若没有检测到意图，且已知药物，则返回药物的描述
        if not intentions and ('Medicine' in types or 'genericNameFormat' in types):
            intention = "medicine_describe"
            if intention not in intentions:
                intentions.append(intention)

        # 若没有识别出实体或意图则调用其它方法
        if not intentions or not types:
            intention = "QA_matching"
            if intention not in intentions:
                intentions.append(intention)

        self.result["intentions"] = intentions

        return self.result


if __name__ == '__main__':
    test = EntityExtractor()
    question = '盐酸左西替利嗪胶囊还叫什么？'
    a = test.extractor(question)
    print(a)
