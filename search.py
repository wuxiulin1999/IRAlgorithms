import os


import math

import re

import json

#different path
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-m","--option")
options,args= parser.parse_args()
option_dict = vars(options)
mode=option_dict['option']

#get the category
root=os.getcwd()
d_root=root+'\\documents'
f_root=root+'\\files'+'\\'
d_name=d_root+'\\'

import sys
sys.path.append(f_root)
import porter

#evaluation
def precision(ret,rel):
	correct=0
	try:
		for r in ret:
			if r in rel and rel[r]:
				correct+=1
		return correct/len(ret)
	except:
		pass


def recall(ret,rel):
	correct=0
	try:
		for r in ret:
			if r in rel and rel[r]:
				correct+=1
		return correct/len(rel)
	except:
		pass
		
def P_at_10(ret,rel):
	correct=0
	l=1
	try:
		for r in ret :
			if r in rel and rel[r]:
				correct+=1
			l+=1
			if(l>10):
				break
		return correct/10
	except:
		pass
		
def R_precision(ret,rel):
	correct=0
	l=1
	try:
		for r in ret:
			if r in rel and rel[r]:
				correct+=1
			l+=1
			if l>len(rel):
				break
		return correct/len(rel)
	except:
		pass


def MAP(ret,rel):
	per=0
	correct=0
	l=1
	try:
		for r in ret:
			if r in rel and rel[r]:
				correct+=1
				per+=(correct/l)
			l+=1
		return per/len(rel)
	except:
		pass

def b_pref(ret,rel):
	pref=0
	r_count=0
	n_count=0
	try:
		for r in ret :
			if r in rel and rel[r]:
				r_count+=1
		for r in ret:
			if r not in rel:
				n_count+=1
			if r in rel and rel[r]:
				pref = pref +(1 - n_count/ r_count)
		return pref/r_count
	except:
		pass
		
#stopwords
with open(f_root+'stopwords.txt','r') as f:
	stopwords=set(f.read().split())


#precalculate
lengths={}#key(docid), value(length of document)
idfs={}#key(term),value(number of documents contain the term)
vectors={}#key(docid),value(key(term),value(fi,j))

#store information in an external file
ex=root+'/files/index.txt'
ex2=root+'/files/index2.txt'
ex3=root+'/files/index3.txt'
stemmer=porter.PorterStemmer()


if not os.path.exists(ex):
	#dictionary :key(doc id), value(list of words)
	documents={}

	#get the documents in the category
	files= os.listdir(d_root)
	for file in files:
		if not os.path.isdir(file): 
			with open( d_name+file, 'r',encoding='UTF-8')  as f:
				doc=f.read()
				allwords=re.compile("[a-z|\']+|[\d.]+", re.I).findall(doc)
				allwords.insert(0,file)
				documents[allwords[0]]=allwords[1:]
	#store terms we have stored before
	cache={}
	for did in documents:
		freq={}#key(term),value(frequency)
		lengths[did]=0
		for term in documents[did]:#iterate all terms
			term=term.lower()
			if term not in stopwords and term !='.':
				if term not in cache:
					cache[term]=stemmer.stem(term)
				term=cache[term]
				#one term length+1
				lengths[did]+=1
				#have seen this term in this document before
				if term in freq:
					freq[term]+=1
				#first time have seen
				else:
					freq[term]=1
					#this term was in a previous document
					if term in idfs:
						idfs[term]+=1
					#we've never seen this term before
					else:
						idfs[term]=1
	#get fi,j
		vectors[did]=freq
	js=json.dumps(vectors)
	js2=json.dumps(idfs)
	js3=json.dumps(lengths)
	file=open(ex,'w')
	file.write(js)
	file.close
	file=open(ex2,'w')
	file.write(js2)
	file.close
	file=open(ex3,'w')
	file.write(js3)
	file.close
else:
	file = open(ex, 'r') 
	js = file.read()
	vectors = json.loads(js)
	file.close()
	file = open(ex2, 'r') 
	js2 = file.read()
	idfs = json.loads(js2)
	file.close()
	file = open(ex3, 'r') 
	js3 = file.read()
	lengths = json.loads(js3)
	file.close()
	

#calculate part of BM25
for term in idfs:
	idfs[term]=math.log((len(vectors)-idfs[term]+0.5)/(idfs[term]+0.5),2)

#calculate average lengths
sum_len=0
for did in vectors:
	sum_len+=lengths[did]
avg_len=sum_len/len(vectors)
#print(avg_len)

queries={}#queries key(qid) value(list of words)
sims={}#queries key(qid)value(key:did,value:sim25))
k=1
b=0.75
query_vectors={}#key:id,value:key:term,value:frequency

#input query		
if mode=="manual" or None:
	while True:
		u_input=None
		try:
			u_input=input("Input the Query:")
		except:
			pass
		if u_input == 'QUIT':
			break
		else:
			query = u_input.lower()
			allwords=re.compile("[a-z|\']+|[\d.]+", re.I).findall(query)
			for term in allwords:
				if term not in stopwords and term != '.':
					term = stemmer.stem(term)
					if term not in query_vectors:
						query_vectors[term]=1
					else:
						query_vectors[term]+=1
			for did in vectors:
				sim=0
				for term in query_vectors:
					if term in vectors[did]:
						sim+=(idfs[term]*vectors[did][term]*(k+1)/(vectors[did][term]+k*(1-b)+b*lengths[did]/avg_len))
					sims[did]=sim
			i=1
			for did in sorted(sims, key=sims.get, reverse=True)[:15]:
				print(' {} {} {} '.format( i, did, sims[did]))
				i=i+1
			
else:
#open queries
	with open(f_root+'queries.txt','r') as f:
		corpus=f.read()
		ques=corpus.split('\n')
		for que in ques:
			allwords=re.compile("[a-z|\']+|[\d.]+", re.I).findall(que)
			queries[allwords[0]]=allwords[1:]

	for qid in queries:
		q_vectors={}
		sim_r={}#key:did,value:sim
		for term in queries[qid]:
			if term not in stopwords and term != '.':
				term = stemmer.stem(term)
				if term not in q_vectors:
					q_vectors[term]=1
				else:
					q_vectors[term]+=1
		query_vectors[qid]=q_vectors

		for did in vectors:
			sim=0
			for term in query_vectors[qid]:
				if term in vectors[did]:
					sim+=(idfs[term]*vectors[did][term]*(k+1)/(vectors[did][term]+k*(1-b)+b*lengths[did]/avg_len))
			sim_r[did]=sim
		sims[qid]=sim_r

	#i=1
	#for did in sorted(sim_r, key=sim_r.get, reverse=True)[:15]:
		#print('{} Q0 {} {} {} 17205981'.format(qid, did, i, sim_r[did]))
		#i=i+1

#out put the result of each query
	ex2=root+'/files/output.txt'
	if not os.path.exists(ex2):
		with open(ex2, 'w') as f:
			for key1 in sims:
				i=1
				for key2 in sorted(sims[key1],key=sims[key1].get,reverse=True)[:30]:
					f.writelines(str(key1)+' '+'Q0'+' ')
					e_line=str(key2)+' '+str(i)+' '+str(sims[key1][key2])+' '+'17205981'
					f.writelines(e_line)
					f.write('\n')
					i+=1
		
			
	ret={}#key(qid)(key(did)value(relevantscore))
	rel={}#key(qid)(key(did)value(relevantscore))
	keys=list(queries.keys())
	i=keys[0]
	j=i
#read the output and qrels into ret,rel
	with open(f_root+'output.txt','r') as f:
		corpus2=f.read()
		docs=corpus2.split('\n')
		dreq={}
		for doc in docs:
			allwords=doc.split()
			if len(allwords)==6:
				if allwords[0]==i:
					dreq[allwords[2]]=0
					j=i
				else:
					i=allwords[0]
					ret[j]=dreq
					dreq={}
	keys=list(queries.keys())
	i=keys[0]
	j=i
	with open(f_root+'qrels.txt','r') as f:
		corpus2=f.read()
		docs=corpus2.split('\n')
		dreq={}
		for doc in docs:
			allwords=doc.split()
			if len(allwords)==4:
				if allwords[0]==i:
					dreq[allwords[2]]=allwords[3]
					j=i
				else:
					i=allwords[0]
					rel[j]=dreq
					dreq={}
	#calculate the avg evaluation score
	precision1=0
	recall1=0
	p_at_101=0
	r_precision1=0
	map1=0
	b_pref1=0
	for r in ret:
		try:
			precision1+=precision(ret[r],rel[r])
			recall1+=recall(ret[r],rel[r])
			p_at_101+=P_at_10(ret[r],rel[r])
			r_precision1+=R_precision(ret[r],rel[r])
			map1+=MAP(ret[r],rel[r])
			b_pref1+=b_pref(ret[r],rel[r])
		except:
			pass
	print("Evaluation score:")
	print("Precision: "+str(precision1/len(ret)))
	print("Recall: "+str(recall1/len(ret)))
	print("P_at_10: "+str(p_at_101/len(ret)))
	print("R_precision: "+str(r_precision1/len(ret)))
	print("MAP: "+str(map1/len(ret)))
	print("B_pref: "+str(b_pref1/len(ret)))
