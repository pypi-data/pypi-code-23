import wordcloud as wd
import jieba
import urllib.request as req
import imageio


def cut(text):
	''' 返回分词之后的列表'''
	if text:
		return list(jieba.cut(text))
	else:
		return -1


def cut2str(text):
	'''返回切分之后的字符串'''
	res = cut(text)
	return ' '.join(res)

def wordcloud(text,font=None,bgfile=None):
	'''生成词云，返回词云图片对象'''
	if text == '':
		return -1
	if bgfile:
		bg_mask = imageio.imread(bgfile)
	else:
		bg_mask = None
	cloud = wd.WordCloud(
		font_path = font,
		mask = bg_mask
	)
	word_cloud = cloud.generate(text)
	img = word_cloud.to_image()
	return img
