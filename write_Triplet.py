import re
import copy
import os

zhongwen = re.compile(u'[\u4e00-\u9fa5]')  # 检查非中文
t = '{'
don = '、'
comma = '，'
colon = '：'

find_all = lambda data, s: [r for r in range(len(data)) if data[r] == s]


# 句子结构转换
def index2tag(sentence):
	names = []
	attrs = []
	tag_list = find_all(sentence, t)
	don_list = find_all(sentence, don)
	comma_list = find_all(sentence, comma)
	colon_list = find_all(sentence, colon)
	# print(pun1_list)
	pun_list = sorted(don_list + comma_list + colon_list)
	all_list = sorted(pun_list + tag_list)
	# 将标点索引替换成标点符号
	for i in range(len(all_list)):
		#  替换出除大括号以外其他的标点符号
		if sentence[all_list[i]] != '{':
			all_list[i] = sentence[all_list[i]]

	entity_list = copy.deepcopy(all_list)
	entity_type_list = copy.deepcopy(all_list)
	# endfor

	# 据姚觐元{-3 PER}、钱保塘{-3 PER}《涪州石鱼文字所见录》{-11 BOOK}，耆后可补入“□□□□□□□瑾公琰。
	# ['姚觐元', '、', '钱保塘', '《涪州石鱼文字所见录》', '，']
	# ['PER', '、', 'PER', ' BO', '，']
	for i in range(len(all_list)):
		for j in range(len(tag_list)):
			if tag_list[j] == all_list[i]:  # all_list[i] = '{'
				brace_index = int(tag_list[j])  # 括号索引
				abb_index = int(tag_list[j]) + 4  # 实体类型标注索引
				length = int(sentence[brace_index + 2: brace_index + 4])  # 标注长度
				entity_content = sentence[brace_index - length: brace_index]  # 实体
				entity_type = sentence[brace_index + 4: brace_index + 7]  # 类型
				changdu = zhongwen.findall(str(entity_content))  # 获取中文字符个数

				L1 = length - len(changdu)  # 非中文个数
				ss = 1
				entity_content = list(entity_content)
				for ii in range(L1):
					while 1:
						ch = sentence[brace_index - length - ss]
						ss += 1
						if '\u4e00' <= ch <= '\u9fff':
							entity_content.insert(0, ch)
							break

				count = 0
				# 去除括号等
				for iii in range(len(entity_content)):
					if '\u4e00' > entity_content[iii] or entity_content[iii] > '\u9fff':
						count += 1
						entity_content[iii] = 0

				for jj in range(count):
					entity_content.remove(0)

				entity_content = ''.join(entity_content)  # 列表转换字符串
				entity_type_list[i] = entity_type
				entity_list[i] = entity_content

	# endfor

	return entity_list, entity_type_list


def find_index(path, Triplepath):
	Triple_Set = []

	pun_distance = {'：': 1, '、': 2, '，': 5}
	# relation=[('GZ','PE'),{'PE':'GZ'},{'PE':'GM'},{'PE':'ZH'},{'PE':'TI'},{'PE':'LO'},{'PE':'BO'},{'PE':'PE'}{'BO':'TI'},{'TK':'TI'},{'TK','Content'},{'TK':'BO'},{'TK':'PE'}]
	# relation=[('GZ}','PER'),('PER','GZ}'),('PER',' BO'),('PER','GM}'),('PER','ZH}'),('PER','TIM'),('PER','LOC'),('PER','BOO'),('BOO','TIM')]
	relation = [('GZ}', 'PER'), ('TIM', 'PER'), ('BOO', 'PER'), ('GZ}', 'PER'), ('GM}', 'PER'), ('PER', 'GZ}'),
				('PER', ' BO'), ('PER', 'GM}'), ('PER', 'ZZ}'), ('PER', 'TIM'),
				('PER', 'LOC'), ('PER', 'BOO'), ('BOO', 'TIM'), ('PER', 'HH}')]
	with open(path, 'r', encoding='utf-8') as f:
		for txt in f:
			txt = txt.replace('\n', '')
			txt = txt.split('。')  # 按句分割
			# entity_list ['姚觐元', '、', '钱保塘', '：', '《涪州石鱼文字所见录》', '，', '，', '广陵书社', '，', '，']
			# entity_type_list ['PER', '、', 'PER', '：', ' BO', '，', '，', 'ORG', '，', '，']
			for sentence in txt:
				entity_list, entity_type_list = index2tag(sentence)
				for i in range(len(entity_type_list)):
					distance = 0
					sdcount = 0
					gzcount = 0
					zcount = 0
					hcount = 0
					dmcount = 0
					gmcount = 0
					flag_start_type = entity_type_list[i]
					flag_start_content = entity_list[i]
					# print('flag_start_type:', flag_start_type)
					# print('flag_start_content:', flag_start_content)
					for j in range(i + 1, len(entity_type_list)):

						flag_end_type = entity_type_list[j]
						flag_end_content = entity_list[j]
						# print(flag_end_content)
						if flag_end_type == '：':
							distance = distance + 1
						elif flag_end_type == '，':
							distance = distance + 5
						elif flag_end_type == '、':
							distance = distance + 2
						else:
							distance = distance + 1
						# print('距离',distance)
						if distance > 100:
							break
						else:
							triple = (flag_start_type, flag_end_type)
							if triple in relation:
								if flag_start_type == 'GZ}' and flag_end_type == 'PER':
									if gzcount == 0:
										triple_content = (flag_end_content, '人物官职', distance, flag_start_content)
										Triple_Set.append(triple_content)
										gzcount += 1
									else:
										continue
								elif flag_start_type == 'PER' and flag_end_type == 'GZ}':
									if gzcount == 0:
										triple_content = (flag_start_content, '人物官职', distance, flag_end_content)
										Triple_Set.append(triple_content)
										gzcount += 1
									else:
										continue
								elif flag_start_type == 'PER' and flag_end_type == ' BO':
									if '题' in flag_end_content:
										triple_content = (flag_start_content, '人物题刻', distance, flag_end_content[2:])
									else:
										triple_content = (flag_start_content, '人物书名', distance, flag_end_content[2:])
									Triple_Set.append(triple_content)
								elif flag_start_type == 'PER' and flag_end_type == 'TIM':
									if sdcount == 0:
										triple_content = (flag_start_content, '人物时代', distance, flag_end_content)
										Triple_Set.append(triple_content)
										sdcount += 1
									else:
										continue
								elif flag_start_type == 'TIM' and flag_end_type == 'PER':
									if sdcount == 0:
										triple_content = (flag_end_content, '人物时代', distance, flag_start_content)
										Triple_Set.append(triple_content)
										sdcount += 1
									else:
										continue

								elif flag_start_type == 'ZZ}' and flag_end_type == 'PER':
									if zcount == 0:
										triple_content = (flag_end_content, '人物字号', distance, flag_start_content)
										Triple_Set.append(triple_content)
										zcount += 1
									else:
										continue
								elif flag_start_type == 'BOO' and flag_end_type == 'PER':
									if '题' in flag_start_type:
										triple_content = (flag_end_content, '人物题刻', distance, flag_start_content)
										Triple_Set.append(triple_content)
									else:
										triple_content = (flag_end_content, '人物书名', distance, flag_start_content)
										Triple_Set.append(triple_content)
								elif flag_start_type == 'PER' and flag_end_type == 'GM}':
									if gmcount == 0:
										triple_content = (flag_start_content, '人物功名', distance, flag_end_content)
										Triple_Set.append(triple_content)
										gmcount += 1
									else:
										continue
								elif flag_start_type == 'PER' and flag_end_type == 'ZZ}':
									if zcount == 0:
										triple_content = (flag_start_content, '人物字号', distance, flag_end_content)
										Triple_Set.append(triple_content)
										zcount += 1
									else:
										continue
								elif flag_start_type == 'PER' and flag_end_type == 'HH}':
									if hcount == 0:
										triple_content = (flag_start_content, '人物字号', distance, flag_end_content)
										Triple_Set.append(triple_content)
										hcount += 1
									else:
										continue

								elif flag_start_type == 'PER' and flag_end_type == 'LOC':
									if dmcount == 0:
										triple_content = (flag_start_content, '人物地名', distance, flag_end_content)
										Triple_Set.append(triple_content)
										dmcount += 1
									else:
										continue
								elif flag_start_type == 'PER' and flag_end_type == 'BOO':
									if '题' in flag_end_content:
										triple_content = (flag_start_content, '人物题刻', distance, flag_end_content[2:])
									else:
										triple_content = (flag_start_content, '人物书名', distance, flag_end_content[2:])
									Triple_Set.append(triple_content)
								elif flag_start_type == 'BOO' and flag_end_type == 'TIM':
									if '题' in flag_start_content:
										triple_content = (flag_start_content[2:], '题刻时代', distance, flag_end_content)
									else:
										triple_content = (flag_start_content[2:], '书名时代', distance, flag_end_content)
									Triple_Set.append(triple_content)

			with open(Triplepath + '\\' + 'Triple_Set副本.txt', 'a', encoding='utf-8') as ff:
				for item in Triple_Set:
					if len(item[0]) > 1 and len(item[3]) > 1:
						ff.write(str(item[0]))
						ff.write('\t')
						ff.write(str(item[1]))
						ff.write('\t')
						# f.write(str(item[2]))
						# f.write('\t')
						ff.write(str(item[3]))

						ff.write('\n')
			Triple_Set = []
			tfile = open(Triplepath + '\\' + 'Triple_Set副本.txt', 'r', encoding='utf-8')
			templist = tfile.readlines()
			templist = set(templist)
			filetemp = open(Triplepath + '\\' + 'Triple_Set.txt', 'w', encoding='utf-8')
			for ite in templist:
				filetemp.write(str(ite))
			filetemp.close()


# def judge_cate()

def relation_match(relation, flag):
	dic = []
	for item in relation:
		if item[0] == flag:
			dic.append(item)
	# endfor

	return dic


def quchong1(filepath):
	f = open(filepath, 'r', encoding='utf-8')
	guanzhi_list = []
	buff = f.readlines()
	f.close()
	fp = open(filepath, 'w+', encoding='utf-8')
	for guanzhi in buff:
		guanzhi_temp = guanzhi.strip()
		if guanzhi_temp in guanzhi_list:
			continue
		fp.write(guanzhi)
		guanzhi_list.append(guanzhi_temp)
	fp.close()


def main(path):
	files = os.listdir(path)

	for file in files:
		Triplepath = path + '\\' + file

		biaozhu_path = path + '\\' + file + '\\' + '原文标注.txt'
		find_index(biaozhu_path, Triplepath)
		os.remove(Triplepath + '\\' + 'Triple_Set副本.txt')
# print('end')
# quchong1(r'E:\项目文件\Triple_Set1.txt')
