import os, sys, re

def gen_get(input_list, cname):
	h_ret = ""
	cpp_ret = ""
	for x in input_list:
		vtype = x[0]
		vname = x[1]
		h_ret += "\t\t%s get_%s(void);\n" % (vtype, vname)
		cpp_ret += "%s %s::get_%s(void){return(this.%s);}\n" % (vtype, cname, vname, vname)
	return([h_ret, cpp_ret])

def gen_set(input_list, cname):
	h_ret = ""
	cpp_ret = ""
	for x in input_list:
		vtype = x[0]
		vname = x[1]
		h_ret += "\t\tvoid set_%s(%s);\n" % (vname, vtype)
		cpp_ret += "void %s::set_%s(%s input){this.%s = input;}\n" % (cname, vname, vtype, vname)
	return([h_ret, cpp_ret])	

	
	
def read_folder():
	#variables
	x = 'n'
	checked_files = []
	re_array = []
	src_folder = ""
	head_folder = ""
	
	#add here your extension
	while((x != 'y') & (x != 'Y')):
		extension = raw_input("Enter your extensions (only cpp) supported at this moment\n").split(' ')
		x = raw_input("Is '%s' is correct ? Y/n\n" % (', '.join(extension)))
	x = 'n'
		
	#re
	for tmp in extension:
		if(tmp[0] != '.'):
			tmp = "\." + tmp
		else:
			tmp = "\\" + tmp
		re_array.append(re.compile("([^ ]+)" + tmp + "$"))
	
	#we read the folder and catch files
	while((x != 'y') & (x != 'Y')):
		folder = raw_input("Path to the folder to scan\n%s" % (os.popen("pwd").readlines()[0]))
		files = os.popen("ls " + folder).readlines()
		
		#we remove the '\n' at the end
		for f in range (0, len(files)):
			files[f] = remove_newline(files[f])
				
		#we check for extension
		checked_files = []
		for f in files:
			for reg in re_array:
				if(reg.match(f)):
					checked_files.append(f)
					break
				
		if(len(checked_files) > 10):
			x = raw_input("There is more than 10 files detected (%s) in , do you want to display it? Y/n\n" % (len(checked_files)))
			if((x == 'y') | (x == 'Y')):
				x = raw_input("Files detected '%s'. Is that correct ? Y/n\n" % (', '.join(checked_files)))
			else:
				x = raw_input("Validate the folder %s? Y/n\n" % (folder))
		else:
			x = raw_input("Files detected '%s'. Is that correct ? Y/n\n" % (', '.join(checked_files)))
	x = 'n'
	
	#source path folder
	while((x != 'y') & (x != 'Y')):
		src_folder = raw_input("Enter your output source folder\n")
		x = raw_input("Is '%s' is correct ? Y/n\n" % (src_folder))
		if((os.path.isdir(src_folder) != 1)):
			print("%s is not a valid folder!" % (src_folder))
			x = 'n'
	x = 'n'
		
	while((x != 'y') & (x != 'Y')):
		head_folder = raw_input("Enter your output header folder\n")
		x = raw_input("Is '%s' is correct ? Y/n\n" % (head_folder))
		if((os.path.isdir(head_folder) != 1)):
			print("%s is not a valid folder!" % (head_folder))
			x = 'n'
	x = 'n'
		
	
	return([checked_files, add_final_slash(src_folder), add_final_slash(head_folder)])

	

#parsing for Cpp file
def parsing_cpp_file (input_files, output_src, output_head, type_list):
	#var
	re_array = []
	for input_file in input_files:
		#definition of cname
		cname = input_file.split('.')[0]
		head_file_name = input_file.split('.')[0] + ".h"
		f_input = open(input_file, 'r')
		f_output_src = open(output_src + input_file, 'w')
		f_output_head = open(output_head + head_file_name, 'w')
		input_list = []
		

		for i in range(len(type_list)):
			type_list[i].replace(' ', '\s*')
		#re
		for tmp in type_list:
			re_array.append(re.compile("^\s*%s\s*(.)*\s*;\s*$" % (tmp)))
		re_include = re.compile("^\s*#include+[(^ )]")

		#parsing of the file
		for line in f_input:
			#detection of include
			if (re_include.match(line)):
				f_output_head.write(line)

			#detection of variable
			else:
				for tmp in range(0, len(re_array)):
					if(re_array[tmp].match(line)):
						line = remove_newline(line)
						line = remove_final_semicolon(line)
						t = line.split(" ")
						t = filter(None, t)
						input_list.append([type_list[tmp], remove_newline(t[len(t) - 1])])
						
						
		#generation
		gget = gen_get(input_list, cname)
		gset = gen_set(input_list, cname)
		#writting header
		f_output_head.write("class %s\n{\n\tpublic:\n" % (cname))
		f_output_head.write(gget[0])
		f_output_head.write(gset[0])
		f_output_head.write("\n\tprivate:\n")
		for x in input_list:
			f_output_head.write("\t\t%s;\n" % (" ".join(x)))
		f_output_head.write("};")
		
		#writting source file
		f_output_src.write("#include \"%s/%s\"\n\n" % (os.path.relpath(output_head, output_src), head_file_name))
		f_output_src.write(gget[1])
		f_output_src.write(gset[1])
	

def remove_newline(input_line):
	if ((input_line[len(input_line) - 1:] == ('\n')) | (input_line[len(input_line) - 1:] == ('\r'))):
		return(input_line[:-1])
	return(input_line)

def add_final_slash(input_line):
	if (input_line[len(input_line) - 1:] == ('/')):
		return(input_line)
	return(input_line + '/')
	
def remove_final_semicolon(input_line):
	if (input_line[len(input_line) - 1:] == (';')):
		return(input_line[: -1])
	return(input_line)	
	
	
	
def main():
	folders = read_folder()
	
	#initialize variables
	type_list = ["char", "char16_t", "char32_t", "wchar_t", "signed char", "signed short int", "signed int", "signed long int", "signed long long int", 
	"unsigned char", "unsigned short int", "unsigned int", "unsigned long", "unsigned long int", "unsigned long long int", "float", "double", "long double", "bool", "void", 
	"int", "long", "short", "string", "std::string"]	
	
	parsing_cpp_file (folders[0], folders[1], folders[2], type_list)
	

main()
