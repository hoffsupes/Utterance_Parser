import os
import numpy as np
import json
import pdb
import string
import re

### Put in a directory which has entity_label_set.txt, intent_label_set.txt and finally 
### the folder which will contain all the example dialogues in .txt format 'annotated_dataset'.
### Put the name of that folder in dname
### and the corresponding files in enam and inam for entity_label_set.txt, intent_label_set.txt
### This program should directly run if you place this in any directory which satisfies the above criteria
### If not, replace dname, enam and inam with the absolute (full) paths for the same
### add commhandler capabilites

def process_punc(tem,tem2,mode):
	p = string.punctuation;
	p = re.sub('[!{}\]\[]', '',p);
	if (mode):
		pos1 = tem.find('{');
		pos2 = len(tem) - 1;
	else:
		pos1 = 0;
		pos2 = len(tem) - 1;
	pos = np.asarray([pos1,pos2]);
	L = [];
	K = [];
	for i in p:
		if(i in tem):
			L.append(tem.find(i));
	for i,l in enumerate(L):
		K.append((np.abs(pos-l)).argmin());
	for i,k in enumerate(K):
		if(k):
			tem2 = tem2 + tem[L[i]];
		else:
			tem2  = tem[L[i]] + tem2;
	return tem2;		

def create_small_dict(entlist,entype,dct):
	for i,e in enumerate(entype):
		if e in dct:
			if(entlist[i] not in dct[e]):
				dct[e].append(entlist[i]);
		else:
			tem = [];
			tem.append(entlist[i]);
			dct.update({e:tem});
	return dct;

def get_ent_list(sp):
	entlist = [];
	enttype = [];
	p = [i for i,m in enumerate(sp) if ']{' in m];
	for i in p:
		m = 0;
		c = 0;
		ent = '';
		etype = '';
		while( (m == 0) & (i+c) < len(sp) ):
			if('{' in sp[i+c]):
				if '[' in sp[i+c]:
					etype = sp[i+c][sp[i+c].find('[')+1:sp[i+c].find(']')];
				ent = sp[i+c][sp[i+c].find('{') + 1:len(sp[i+c])];
				if('}' in sp[i+c]):
					ent = ent[:ent.find('}')];
					break;
				c = c + 1;
			elif('}' in sp[i+c]):
				m = 1;
				ent = ent + ' ';
				for i in sp[i+c][:len(sp[i+c])]:
					if(i == '}'):
						break;
					ent = ent + i;
				break;
			else:
				ent = ent +' '+ sp[i+c];
				c = c + 1;
		if(ent not in entlist):
			entlist.append(ent);
			enttype.append(etype);
	return entlist,enttype;	

def pross_file(fnam,dicta,dictb,mode):
	fptr = open(fnam, "r");
	for line in fptr:
		sp = line.split();
		intent = " ";
		joiner = " ";
		entity = " ";
		if mode == 1:
			if((sp == []) | (len(sp) == 0) | (len(line) == 1) | (line[0] == '=')):
				continue;
			entity = sp[0][0:len(sp[0])-1];
			entexample = joiner.join(sp[1:len(sp)]);
			dicta.update({entity:entexample});
			continue;
		if(('User:' in sp)&('Agent:' in sp)):
			findx = min(sp.index('User:'),sp.index('Agent:')) + 1;
		if('User:' in sp):
			findx = sp.index('User:') + 1;
		elif('Agent:' in sp):
			findx = sp.index('Agent:') + 1;
		tem = sp[findx:len(sp)];
		#print(tem)
		if mode == 2:
			elist,etype = get_ent_list(sp);
			dicta = create_small_dict(elist,etype,dicta);
			continue;
		if(dictb != {}): 
		### Process tem here to replace entities
			ekeys = list(dictb.keys());
			for E in ekeys:
				for j,T in enumerate(tem):
					if(('[' in T)| (']' in T)):
						if(T[ T.index('[')+1:T.index(']')] == E):
							tmp = tem[j];
							tem[j] = '@'+dictb[E];
							tem[j] = process_punc(tmp,tem[j],1);
			for i,T in enumerate(tem):
				if (('{' in T)|('}' in T)):
					yes = process_punc(tem[i],'',0);
					if(len(yes) == 0):
						del(tem[i]);	
					else:
						tem[i] = yes;
		utterance  = joiner.join(tem);
		if(sp[findx-2][0] != '[' ):
			print('Your file is formatted wrong, please format the input file correctly! \n The intent comes before the speaker label and is place in brackets [ ] for eg. [a001] for intent a001')
			exit(1);
		else:
			intent = sp[findx-2][sp[findx-2].index('[')+1:sp[findx-2].index(']')];
		if mode == 3:
			dicta.append(intent);
			continue;
		if(intent in dicta["sentence_set"]):
			dicta["sentence_set"][intent].append(utterance);
		else:
			temlist = [];
			temlist.append(utterance);
			dicta["sentence_set"].update({intent:temlist});
	fptr.close();
	return dicta;

def integrity_check(entset,ent_dict,intset,int_dict,fnam): #Checks for the honesty of the input data 
	def get_brak_props(line):
		return [i for i,m in enumerate(line) if '[' == m],\
		[i for i,m in enumerate(line) if ']' == m],\
		[i for i,m in enumerate(line) if '{' == m],\
		[i for i,m in enumerate(line) if '}' == m];	
	def ischar(line,SO,ch,mod):
		for i in SO:
			if mod:
				if line[i+1] == ch:
					return 0;
			else:
				if line[i-1] == ch:
					return 0;
		return 1;
	for i in list(entset.keys()):
		if i not in list(ent_dict.keys()):
			print('Erring entity:', i)
			print('ERROR in ',fnam,'\n');
			print('FILE INTEGRITY ERROR! The file entity_label_set.txt has not been updated with the latest entity labels, please do so before running this program!');
			return 0;
	for i in intset:
		if i not in list(int_dict.keys()):
			print('Erring intent:', i)
			print('ERROR in ',fnam,'\n');
			print('FILE INTEGRITY ERROR! The file intent_label_set.txt has not been updated with the latest intent labels, please do so before running this program!');
			return 0;
	fptr = open(fnam, "r");
	for line in fptr:
		SO,SC,CO,CC = get_brak_props(line);
		if(not (ischar(line,SO,' ',1) & ischar(line,SC,' ',0)& ischar(line,CO,' ',1)& ischar(line,CC,' ',0))):
			print('ERROR in ',fnam,'\n');
			print('Erring line:', line);
			print('FILE INTEGRITY ERROR! Incorrect formatting in the file in terms of how the brackets are structured, there are spaces in the wrong places after the brackets, please correct them before running this program!');
	fptr.close();
	return 1;
	
def gen_dict(fnam,enam,inam):
	dicto = {
		"sentence_set":{
		} 

	};
	ent_dict = {};
	int_dict = {};
	entset = {};
	intset = [];
	ent_dict = pross_file(enam,ent_dict,{},1);
	int_dict = pross_file(inam,int_dict,{},1);
	dicto = pross_file(fnam,dicto,ent_dict,0);
	entset = pross_file(fnam,entset,{},2);
	intset = pross_file(fnam,intset,{},3);
	
	if(!integrity_check(entset,ent_dict,intset,int_dict,fnam)):
		print('\n\nThere is an error in either your file content or its formatting, please see the error message above! Please be careful before running the program again! \n')
		exit(1);
	
	dicto['entity_set'] = entset;
	dicto['intent_seq'] = intset;
	return dicto;


def get_dict_list(dname,enam,inam):
	all_dict = [];
	for txtpath in os.listdir(dname):
		if(txtpath.endswith(".txt")):
			all_dict.append(gen_dict(dname+'/'+txtpath,enam,inam));
	return all_dict;

enam = "entity_label_set.txt";
inam = "intent_label_set.txt";
dname = "annotated_dataset";

new_dict = get_dict_list(dname,enam,inam);
print(json.dumps(new_dict,indent=4));
