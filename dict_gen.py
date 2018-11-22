import os
import numpy as np
import json
import pdb



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
					ent = ent[:len(ent)-1];
					break;
				c = c + 1;
			elif('}' in sp[i+c]):
				m = 1;
				ent = ent +' '+ sp[i+c][:len(sp[i+c])-1];
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
							tem[j] = '@'+dictb[E];
			
			for i,T in enumerate(tem):
				if (('{' in T)|('}' in T)):
					del(tem[i]);	
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

