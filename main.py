def display(h_ret, cpp_ret):
	print("header generated: \n")
	print(h_ret)
	print("\nsource file generated: \n")
	print(cpp_ret)

def gen_get(input_list, cname):
	h_ret = ""
	cpp_ret = ""
	for x in input_list:
		vtype = x[0]
		vname = x[1]
		h_ret += "%s get_%s(void);\n" % (vtype, vname)
		cpp_ret += "%s %sget_%s(void){return(this.%s);}\n" % (vtype, cname, vname, vname)
	return([h_ret, cpp_ret])

def gen_set(input_list, cname):
	h_ret = ""
	cpp_ret = ""
	for x in input_list:
		vtype = x[0]
		vname = x[1]
		h_ret += "void set_%s(%s);\n" % (vname, vtype)
		cpp_ret += "void %sset_%s(%s input){this.%s = input;}\n" % (cname, vname, vtype, vname)
	return([h_ret, cpp_ret])	

def analyse():
	input_list = []
	
	args = raw_input("Insert your variable separete by a coma\n")
	#we separate args
	args = args.split(",")
	#we separate vtype to vname
	for x in args:
		t = x.split(" ")
		t = filter (None, t)
		ttype = ""
		tname = t[len(t) - 1]
		for i in range (0, len(t) - 1):
			ttype += t[i]
			if(i < len(t) - 2):
				ttype += " "
		input_list.append([ttype, tname])
	return(input_list)
	
keyword = {"unsigned", "int", "char", "string", "std::string", "bool", "long", "float", "double"}

def intro():
	ret = raw_input("Do you want to add the name of the class for cpp function?\n")
	if (ret != ""):
		ret += "::"
	return(ret)

h_ret = ""
cpp_ret = ""

#llist = [["int", "a"], ["char", "b"]]
cname = intro()
llist = analyse()
ret = gen_get(llist, cname)
h_ret += ret[0]
cpp_ret += ret[1]

ret = gen_set(llist, cname)
h_ret += ret[0]
cpp_ret += ret[1]

display(h_ret, cpp_ret)
