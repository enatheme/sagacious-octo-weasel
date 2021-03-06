import os, sys, re

#remove \n char
def remove_newline(input_line):
	if ((input_line[len(input_line) - 1:] == ('\n')) | (input_line[len(input_line) - 1:] == ('\r'))):
		return(input_line[:-1])
	return(input_line)

#remove / in last char for a path
def add_final_slash(input_line):
	if (input_line[len(input_line) - 1:] == ('/')):
		return(input_line)
	return(input_line + '/')

#remove the ; at the end of an instruction (c, c++)
def remove_final_semicolon(input_line):
	if (input_line[len(input_line) - 1:] == (';')):
		return(input_line[: -1])
	return(input_line)	
	

#display information and ask if it is right
def check_information(checked_files, src_folder, head_folder):
	print("Files to check:")
	#if there is a lot of checked_files
	if(len(checked_files) > 10):
		if(input("%d files found, do you want to display all? Y/n\n") == 'Y'):
			for f in checked_files:
				print("\t- %s" % (f))
	else:
		for f in checked_files:
			print("\t- %s" % (f))
	print("\nFolder to copy source files: %s" % (src_folder))
	print("\nFolder to copy header files: %s" % (head_folder))
	return(input("\nIs this information correct ? Y/n\n"))


#split a path name and return only the file name
def get_proper_file_name(input_name):
	ret = input_name.split('/')
	return(ret[len(ret) - 1])

#geter generation
def gen_get(input_list, cname):
	h_ret = ""
	cpp_ret = ""
	for x in input_list:
		vtype = x[0]
		vname = x[1]
		h_ret += "\t\t%s get_%s(void);\n" % (vtype, vname)
		cpp_ret += "%s %s::get_%s(void){return(this.%s);}\n" % (vtype, cname, vname, vname)
	return([h_ret, cpp_ret])

#seter generation
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
	extension = input("Enter your extensions (only cpp) supported at this moment\n").split(' ')

	#re
	for tmp in extension:
		if(tmp[0] != '.'):
			tmp = "\." + tmp
		else:
			tmp = "\\" + tmp
		re_array.append(re.compile("([^ ]+)" + tmp + "$"))
	
	#we read the folder and catch files
	while((x != 'y') & (x != 'Y')):
		folder = input("Path to the folder to scan\n%s" % (os.popen("pwd").readlines()[0]))
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
					
		#we add the path to the name file!
		for i in range (0, len(checked_files)):
			checked_files[i] = folder + '/' + checked_files[i]
	
		#source path folder
		src_folder = input("Enter your output source folder\n")
		while(os.path.isdir(src_folder) != 1):
			print("%s is not a valid folder!" % (src_folder))
			src_folder = input("Enter your output source folder\n")
	
		head_folder = input("Enter your output header folder\n")
		while(os.path.isdir(head_folder) != 1):
			print("%s is not a valid folder!" % (head_folder))
			head_folder = input("Enter your output header folder\n")
		

		x = check_information(checked_files, add_final_slash(src_folder), add_final_slash(head_folder))
	
	
	
	return([checked_files, add_final_slash(src_folder), add_final_slash(head_folder)])

	

#parsing for Cpp file
def parsing_cpp_file (input_files, output_src, output_head, type_list):
	#var
	re_array = []
	for input_file in input_files:
		#definition of cname
		proper_name = get_proper_file_name(input_file)
		cname = proper_name.split('.')[0]
		head_file_name = cname + ".h"
		input_list = []

		f_input = open(input_file, 'r')
		f_output_src = open(output_src + proper_name, 'w')
		f_output_head = open(output_head + head_file_name, 'w')
		
		for i in range(len(type_list)):
			type_list[i].replace(' ', '\s*')
		#re
		for tmp in type_list:
			re_array.append(re.compile("^\s*%s\s*(.)*\s*;\s*$" % (tmp)))
		re_include = re.compile("^\s*#include+[(^ )]")
		empty_line = re.compile("^[\s, \n]*$")


		#parsing of the file
		for line in f_input:
			#if the line is not empty
			if(not(empty_line.match(line))):
				#detection of include
				if (re_include.match(line)):
					f_output_head.write(line)

				#detection of variable
				else:
					for tmp in range(0, len(re_array)):
						if(re_array[tmp].match(line)):
							#we clean the line
							line = remove_newline(line)
							line = remove_final_semicolon(line)
							t = line.split(" ")
							t = list(filter(None, t))
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
	

	
	
def main():
	folders = read_folder()
	
	#initialize variables
	type_list = ["char", "char16_t", "char32_t", "wchar_t", "signed char", "signed short int", "signed int", "signed long int", "signed long long int", 
	"unsigned char", "unsigned short int", "unsigned int", "unsigned long", "unsigned long int", "unsigned long long int", "float", "double", "long double", "bool", "void", 
	"int", "long", "short", "string", "std::string"]	
	
	parsing_cpp_file (folders[0], folders[1], folders[2], type_list)
	

main()
