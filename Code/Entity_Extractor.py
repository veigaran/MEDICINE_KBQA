#!/usr/bin/env python3
# coding: utf-8
from Params import Params
import jieba
from predict import predict
from FindSim import FindSim


class EntityExtractor(Params):
    def __init__(self):
        super().__init__()
        self.result = {}
        self.find_sim_words = FindSim.find_sim_words

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

        for i in self.disease_tree.iter(question):
            word = i[1][1]
            if "Disease" not in self.result:
                self.result["Disease"] = [word]
            else:
                self.result["Disease"].append(word)

        for i in self.alias_tree.iter(question):
            word = i[1][1]
            if "Alias" not in self.result:
                self.result["Alias"] = [word]
            else:
                self.result["Alias"].append(word)

        return self.result

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
            # LSTM命名实体识别
            self.result = predict(question)
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

        # 已知疾病或症状，查询治疗方法
        if self.check_words(self.cureway_qwds, question) and \
                ('Disease' in types or 'Symptom' in types or 'Alias' in types):
            intention = "query_cureway"
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
        # print(self.result)
        return self.result


if __name__ == '__main__':
    test = EntityExtractor()
    question = '盐酸氨溴索片有哪些名字'
    a = test.extractor(question)
    print(a)
