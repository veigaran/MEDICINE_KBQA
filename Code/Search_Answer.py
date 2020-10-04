#!/usr/bin/env python3
# coding: utf-8
from py2neo import Graph


class AnswerSearching:
    def __init__(self):
        self.graph = Graph("http://localhost:7474", username="neo4j", password="123456")
        self.top_num = 10

    def question_parser(self, data):
        """
        主要是根据不同的实体和意图构造cypher查询语句
        :param data: {"Disease":[], "Alias":[], "Symptom":[], "Complication":[]}
        :return:
        """
        sqls = []
        if data:
            for intent in data["intentions"]:
                sql_ = {}
                sql_["intention"] = intent
                sql = []
                if data.get("Medicine"):
                    sql = self.transfor_to_sql("Medicine", data["Medicine"], intent)
                elif data.get("genericNameFormat"):
                    sql = self.transfor_to_sql("genericNameFormat", data["genericNameFormat"], intent)
                elif data.get("list_cate"):
                    sql = self.transfor_to_sql("list_cate", data["list_cate"], intent)
                elif data.get("indications"):
                    sql = self.transfor_to_sql("indications", data["indications"], intent)
                elif data.get("Disease"):
                    sql = self.transfor_to_sql("Disease", data["Disease"], intent)
                elif data.get("Alias"):
                    sql = self.transfor_to_sql("Alias", data["Alias"], intent)

                if sql:
                    sql_['sql'] = sql
                    sqls.append(sql_)
        return sqls

    def transfor_to_sql(self, label, entities, intent):
        """
        将问题转变为cypher查询语句
        :param label:实体标签
        :param entities:实体列表
        :param intent:查询意图
        :return:cypher查询语句
        """
        if not entities:
            return []
        sql = []

        # 查询症状
        if intent == "query_symptom" and label == "Medicine":
            sql = ["MATCH(m:Medicine)-[:indications_are]->(i) WHERE m.name=~'{0}.*' RETURN m.name,i.name".format(e)
                   for e in entities]
        if intent == "query_symptom" and label == "genericNameFormat":
            sql = ["MATCH(g:genericNameFormat)<-[:genericNameFormat_is]-(m:Medicine)-[:indications_are]->(i)" \
                   " WHERE g.name='{0}' RETURN m.name,i.name".format(e) for e in entities]

        # 查询治疗方法(查询用什么药)
        if intent == "query_cureway" and label == "Disease":
            sql = ["MATCH (d:Disease)-[:HAS_DRUG]->(n) WHERE d.name='{0}' return d.name," \
                   "n.name".format(e) for e in entities]
        if intent == "query_cureway" and label == "Alias":
            sql = ["MATCH (n)<-[:HAS_DRUG]-(d:Disease)-[]->(a:Alias) WHERE a.name='{0}' " \
                   "return d.name, n.name".format(e) for e in entities]

        # 查询别称
        if intent == "query_generic" and label == "Medicine":
            sql = ["MATCH(m:Medicine)-[:genericNameFormat_is]->(n) WHERE m.name=~'{0}.*' return m.name,n.name". \
                       format(e) for e in entities]

        # 查询所属种类
        if intent == "query_cate" and label == "Medicine":
            sql = ["MATCH(m:Medicine)-[:lsit_cate_is]->(c) WHERE m.name =~'{0}.*' RETURN m.name,c.name".format(e)
                   for e in entities]
        if intent == "query_cate" and label == "genericNameFormat":
            sql = ["MATCH(g:genericNameFormat)<-[:genericNameFormat_is]-(m:Medicine)-[:lsit_cate_is]->(c)" \
                   " WHERE g.name='{0}' RETURN m.name,c.name".format(e) for e in entities]

        # 查询用量
        if intent == "query_dosage" and label == "Medicine":
            sql = ["MATCH(m:Medicine) WHERE m.name=~'{0}.*' return m.name,m.dosageAndAdministration".format(e) for e in
                   entities]
        if intent == "query_dosage" and label == "genericNameFormat":
            sql = [
                "MATCH(m:Medicine)-[]->(g:genericNameFormat) WHERE g.name='{0}' return m.name,m.dosageAndAdministration".format(
                    e)
                for e in entities]

        # 查询注意事项
        if intent == "query_caution" and label == "Medicine":
            sql = ["MATCH(m:Medicine) WHERE m.name=~'{0}.*' return m.name,m.cautions".format(e) for e in entities]
        if intent == "query_caution" and label == "genericNameFormat":
            sql = ["MATCH(m:Medicine)-[]->(g:genericNameFormat) WHERE g.name='{0}' return m.name,m.cautions".format(e)
                   for e in entities]

        # 查询药物
        if intent == "query_medicine" and label == "indications":
            sql = ["MATCH(m:Medicine)-[]->(i:indications) WHERE i.name=~'{0}.*' return m.name".format(e) for e in entities]

        # 查询用药禁忌
        if intent == "query_contraindications" and label == "Medicine":
            sql = ["MATCH(m:Medicine) WHERE m.name=~'{0}.*' return m.name,m.contraindications".format(e) for e in entities]
        if intent == "query_contraindications" and label == "genericNameFormat":
            sql = ["MATCH(m:Medicine)-[]->(g:genericNameFormat) WHERE g.name='{0}' " \
                   "return m.name,m.contraindications".format(e) for e in entities]

        # 查询药品成分
        if intent == "query_ingredients" and label == "Medicine":
            sql = ["MATCH(m:Medicine)-[:ingredients_are]->(c) WHERE m.name =~'{0}.*' RETURN m.name,c.name".format(e)
                   for e in entities]
        if intent == "query_ingredients" and label == "genericNameFormat":
            sql = ["MATCH(g:genericNameFormat)<-[:genericNameFormat_is]-(m:Medicine)-[:ingredients_are]->(c)" \
                   " WHERE g.name='{0}' RETURN m.name,c.name".format(e) for e in entities]

        # 查询不良反应
        if intent == "query_adverseRea" and label == "Medicine":
            sql = ["MATCH(m:Medicine) WHERE m.name=~'{0}.*' return m.name,m.adverseReactions".format(e) for e in entities]
        if intent == "query_adverseRea" and label == "genericNameFormat":
            sql = ["MATCH(m:Medicine)-[]->(g:genericNameFormat) WHERE g.name='{0}' " \
                   "return m.name,m.adverseReactions".format(e) for e in entities]

        # 查询药物描述
        if intent == "medicine_describe" and label == "Medicine":
            sql = ["MATCH(m:Medicine) WHERE m.name=~'{0}.*' return m.name,m.list_cate,m.indications" \
                   "m.dosageAndAdministration,m.cautions".format(e) for e in entities]
        if intent == "medicine_describe" and label == "genericNameFormat":
            sql = [
                "MATCH(m:Medicine)-[]->(g:genericNameFormat) WHERE g.name='{0}' return m.name,m.list_cate,m.indications" \
                "m.dosageAndAdministration,m.cautions".format(e) for e in entities]

        return sql

    def searching(self, sqls):
        """
        执行cypher查询，返回结果
        :param sqls:
        :return:str
        """
        final_answers = []
        for sql_ in sqls:
            intent = sql_['intention']
            queries = sql_['sql']
            answers = []
            for query in queries:
                ress = self.graph.run(query).data()
                answers += ress
            final_answer = self.answer_template(intent, answers)
            if final_answer:
                final_answers.append(final_answer)
        return final_answers

    def answer_template(self, intent, answers):
        """
        根据不同意图，返回不同模板的答案
        :param intent: 查询意图
        :param answers: 知识图谱查询结果
        :return: str
        """
        final_answer = ""
        if not answers:
            return ""

        # 查询症状
        if intent == "query_symptom":
            medicine_dic = {}
            for data in answers:
                d = data['m.name']
                s = data['i.name']
                if d not in medicine_dic:
                    medicine_dic[d] = [s]
                else:
                    medicine_dic[d].append(s)
            i = 0
            for k, v in medicine_dic.items():
                if i >= 10:
                    break
                final_answer += "药物 {0} 的适应症状有：{1}\n".format(k, ','.join(list(set(v))))
                i += 1

        # 查询治疗方法
        if intent == "query_cureway":
            disease_dic = {}
            for data in answers:
                disease = data['d.name']
                # treat = data["d.treatment"]
                drug = data["n.name"]
                if disease not in disease_dic:
                    disease_dic[disease] = [drug]
                else:
                    disease_dic[disease].append(drug)
            i = 0
            for d, v in disease_dic.items():
                if i >= 10:
                    break
                # final_answer += "疾病 {0} 可用药品包括：{1}\n".format(d, v[0], ','.join(v[1:]))
                final_answer += "{0}可用药品包括：{1}\n".format(d, ','.join(v))
                i += 1

        # 查询别称
        if intent == "query_generic":
            dic = {}
            for data in answers:
                m = data['m.name']
                g = data['n.name']
                if m not in dic:
                    dic[m] = [g]
                else:
                    dic[m].append(g)
            i = 0
            for k, v in dic.items():
                if i >= 10:
                    break
                final_answer += "药物{0}的通用名称为：{1}\n".format(k, ','.join(list(set(v))))
                i += 1

        # 查询所属种类
        if intent == "query_cate":
            dic = {}
            for data in answers:
                m = data['m.name']
                g = data['c.name']
                if m not in dic:
                    dic[m] = [g]
                else:
                    dic[m].append(g)
            i = 0
            for k, v in dic.items():
                if i >= 10:
                    break
                final_answer += "药物 {0} 的所属种类为：{1}\n".format(k, ','.join(list(set(v))))
                i += 1

        # 查询药品成份
        if intent == "query_ingredients":
            dic = {}
            for data in answers:
                m = data['m.name']
                g = data['c.name']
                if m not in dic:
                    dic[m] = [g]
                else:
                    dic[m].append(g)
            i = 0
            for k, v in dic.items():
                if i >= 10:
                    break
                final_answer += "药物 {0} 的成分为：{1}\n".format(k, ','.join(list(set(v))))
                i += 1

        # 查询用量
        if intent == "query_dosage":
            dic = {}
            for data in answers:
                m = data['m.name']
                g = data['m.dosageAndAdministration']
                if m not in dic:
                    dic[m] = [g]
                else:
                    dic[m].append(g)
            i = 0
            for k, v in dic.items():
                if i >= 10:
                    break
                final_answer += "药物 {0} 的用法用量为：{1}\n".format(k, ','.join(list(set(v))))
                i += 1

        # 查询注意事项
        if intent == "query_caution":
            dic = {}
            for data in answers:
                m = data['m.name']
                g = data['m.cautions']
                if m not in dic:
                    dic[m] = [g]
                else:
                    dic[m].append(g)
            i = 0
            for k, v in dic.items():
                if i >= 10:
                    break
                final_answer += "药物 {0} 的注意事项为：{1}\n".format(k, ','.join(list(set(v))))
                i += 1

        # 查询用药禁忌
        if intent == "query_contraindications":
            dic = {}
            for data in answers:
                m = data['m.name']
                g = data['m.contraindications']
                if m not in dic:
                    dic[m] = [g]
                else:
                    dic[m].append(g)
            i = 0
            for k, v in dic.items():
                if i >= 10:
                    break
                final_answer += "药物 {0} 的用药禁忌为：{1}\n".format(k, ','.join(list(set(v))))
                i += 1

        # 查询不良反应
        if intent == "query_adverseRea":
            dic = {}
            for data in answers:
                m = data['m.name']
                g = data['m.contraindications']
                if m not in dic:
                    dic[m] = [g]
                else:
                    dic[m].append(g)
            i = 0
            for k, v in dic.items():
                if i >= 10:
                    break
                final_answer += "药物 {0} 的不良反应为：{1}\n".format(k, ','.join(list(set(v))))
                i += 1

        # # 查询药物
        # if intent == "query_medicine":
        #     disease_freq = {}
        #     for data in answers:
        #         d = data["m.name"]
        #         disease_freq[d] = disease_freq.get(d, 0) + 1
        #     freq = sorted(disease_freq.items(), key=lambda x: x[1], reverse=True)
        #     for d, v in freq[:10]:
        #         final_answer += "药物为 {0} 的概率为：{1}\n".format(d, v / 10)

        # 查询药物描述
        if intent == "medicine_describe":
            medicine_infos = {}
            for data in answers:
                name = data['m.name']
                cate = data['m.list_cate']
                indications = data['m.indications']
                dosage = data['m.dosageAndAdministration']
                cautions = data['m.cautions']
                if name not in medicine_infos:
                    medicine_infos[name] = [cate, indications, dosage, cautions]
                else:
                    medicine_infos[name].extend([cate, indications, dosage, cautions])
            i = 0
            for k, v in medicine_infos.items():
                if i >= 10:
                    break
                message = "药物{0}的信息如下：\n所属类别：{1}\n适用症：{2}\n用法用量：{3}\n注意事项：{4}\n"
                final_answer += message.format(k, v[0], v[1], v[2], v[3], v[4])
                i += 1

        return final_answer


if __name__ == '__main__':
    searcher = AnswerSearching()
    entities = {'Medicine': ['盐酸氨溴索片'], 'intentions': ['query_generic']}
    sqls = searcher.question_parser(entities)
    final_answer = searcher.searching(sqls)
    print(final_answer)