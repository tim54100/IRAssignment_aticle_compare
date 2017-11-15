
# coding: utf-8

# In[58]:

import jieba
import jieba.posseg as pseg
jieba.load_userdict('./IRAssignment-master/dict.txt.big.txt')


# In[59]:

top = 0
temp = {}
for i in range(1,41):
    content = open('./articles/'+str(i)+'.txt', 'rb').read()
    words = pseg.cut(content)
    for word in words:
        if not temp.has_key(word.word):
            temp.update({word.word:top})
            top+=1
#     print str(i) + ".txt is finished"


# In[60]:

vec = []
for i in range(1,41):
    content = open('./articles/'+str(i)+'.txt', 'rb').read()
    words = pseg.cut(content)
    temp_vec = [0 for j in range(top)]
    for word in words:
        temp_vec[temp[word.word]]+=1
    vec.append(temp_vec)
#     print str(i) + ".txt is finished"


# In[61]:

from math import sqrt
import random

def readfile(filename):
    lines = [line for line in file(filename)]

  # First line is the column titles
    colnames = lines[0].strip().split('\t')[1:]
    rownames = []
    data = []
    for line in lines[1:]:
        p = line.strip().split('\t')
    # First column in each row is the rowname
        rownames.append(p[0])
    # The data for this row is the remainder of the row
        data.append([float(x) for x in p[1:]])
    return (rownames, colnames, data)


# In[62]:

def cosine(v1, v2):
    inner_product = sum([ v1[i]*v2[i] for i in range(len(v1))])
    length_v1 = sqrt(sum([ v1[i]*v1[i] for i in range(len(v1))]))
    length_v2 = sqrt(sum([ v2[i]*v2[i] for i in range(len(v2))]))
    cosine= inner_product/(length_v1*length_v2)
    return cosine


# In[63]:

class bicluster:

    def __init__(
        self,
        vec,
        left=None,
        right=None,
        distance=0.0,
        id=None,
        ):
        self.left = left
        self.right = right
        self.vec = vec
        self.id = id
        self.distance = distance


def hcluster(rows, distance=cosine):
    distances = {}
    currentclustid = -1

  # Clusters are initially just the rows
    clust = [bicluster(rows[i], id=i) for i in range(len(rows))]

    while len(clust) > 1:
        lowestpair = (0, 1)
        closest = distance(clust[0].vec, clust[1].vec)

    # loop through every pair looking for the smallest distance
        for i in range(len(clust)):
            for j in range(i + 1, len(clust)):
        # distances is the cache of distance calculations
                if (clust[i].id, clust[j].id) not in distances:
                    distances[(clust[i].id, clust[j].id)] =                         distance(clust[i].vec, clust[j].vec)

                d = distances[(clust[i].id, clust[j].id)]

                if d < closest:
                    closest = d
                    lowestpair = (i, j)

    # calculate the average of the two clusters
        mergevec = [(clust[lowestpair[0]].vec[i] + clust[lowestpair[1]].vec[i])
                    / 2.0 for i in range(len(clust[0].vec))]

    # create the new cluster
        newcluster = bicluster(mergevec, left=clust[lowestpair[0]],
                               right=clust[lowestpair[1]], distance=closest,
                               id=currentclustid)

    # cluster ids that weren't in the original set are negative
        currentclustid -= 1
        del clust[lowestpair[1]]
        del clust[lowestpair[0]]
        clust.append(newcluster)

    return clust[0]


# In[64]:

cluster_result = hcluster(vec)


# In[65]:

def getheight(clust):
  # Is this an endpoint? Then the height is just 1
    if clust.left == None and clust.right == None:
        return 1

  # Otherwise the height is the same of the heights of
  # each branch
    return getheight(clust.left) + getheight(clust.right)


def getdepth(clust):
  # The distance of an endpoint is 0.0
    if clust.left == None and clust.right == None:
        return 0

  # The distance of a branch is the greater of its two sides
  # plus its own distance
    return max(getdepth(clust.left), getdepth(clust.right)) + clust.distance


def drawdendrogram(clust, labels, jpeg='clusters.jpg'):
  # height and width
    h = getheight(clust) * 20
    w = 1200
    depth = getdepth(clust)

  # width is fixed, so scale distances accordingly
    scaling = float(w - 150) / depth

  # Create a new image with a white background
    img = Image.new('RGB', (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    draw.line((0, h / 2, 10, h / 2), fill=(255, 0, 0))

  # Draw the first node
    drawnode(
        draw,
        clust,
        10,
        h / 2,
        scaling,
        labels,
        )
    img.save(jpeg, 'JPEG')


def drawnode(
    draw,
    clust,
    x,
    y,
    scaling,
    labels,
    ):
    if clust.id < 0:
        h1 = getheight(clust.left) * 20
        h2 = getheight(clust.right) * 20
        top = y - (h1 + h2) / 2
        bottom = y + (h1 + h2) / 2
    # Line length
        ll = clust.distance * scaling
    # Vertical line from this cluster to children
        draw.line((x, top + h1 / 2, x, bottom - h2 / 2), fill=(255, 0, 0))

    # Horizontal line to left item
        draw.line((x, top + h1 / 2, x + ll, top + h1 / 2), fill=(255, 0, 0))

    # Horizontal line to right item
        draw.line((x, bottom - h2 / 2, x + ll, bottom - h2 / 2), fill=(255, 0,
                  0))

    # Call the function to draw the left and right nodes
        drawnode(
            draw,
            clust.left,
            x + ll,
            top + h1 / 2,
            scaling,
            labels,
            )
        drawnode(
            draw,
            clust.right,
            x + ll,
            bottom - h2 / 2,
            scaling,
            labels,
            )
    else:
    # If this is an endpoint, draw the item label
        draw.text((x + 5, y - 7), labels[clust.id], (0, 0, 0))


# In[66]:

from PIL import Image, ImageDraw
chapters_name = ["第一章　滅門",
"第二章　聆秘",
"第三章　救難",
"第四章　坐鬥",
"第五章　治傷",
"第六章　洗手",
"第七章　授譜",
"第八章　面壁",
"第九章　邀客",
"第十章　傳劍",
"第十一章　聚氣",
"第十二章　圍攻",
"第十三章　學琴",
"第十四章　論杯",
"第十五章　灌藥",
"第十六章　注血",
"第十七章　傾心",
"第十八章　聯手",
"第十九章　打賭",
"第二十章　入獄",
"第二十一章　囚居",
"第二十二章　脫困",
"第二十三章　伏擊",
"第二十四章　蒙冤",
"第二十五章　聞訊",
"第二十六章　圍寺",
"第二十七章　三戰",
"第二十八章　積雪",
"第二十九章　掌門",
"第三十章　密議",
"第三十一章　繡花",
"第三十二章　併派",
"第三十三章　比劍",
"第三十四章　奪帥",
"第三十五章　復仇",
"第三十六章　傷逝",
"第三十七章　迫娶",
"第三十八章　聚殲",
"第三十九章　拒盟",
"第四十章　曲諧"]
drawdendrogram(cluster_result,[str(i) for i in range(1,41)],jpeg='blogclust.jpg')


# In[67]:

