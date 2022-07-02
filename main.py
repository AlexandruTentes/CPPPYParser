import re
import pyperclip

path = "../../C++/GradScheme/"
headers = []
replaced_func = {}
indent_spaces_count = 0
indent_t_count = 0
nesting_count = 1
output = ""
include_header = ""
replace_list = []
replace_list.append("GEN_")
replace_list.append("GEN_CLASS_")
replace_list.append("GEN_STRUCT_")
replace_list.append("//START_OBJ_DEF")
replace_list.append("//END_OBJ_SIG")
replace_list.append("//END_OBJ_DEF")
replace_list.append("//GENERATED_INPUT_OUT")
file = None

def remove_multiple_substrings(word, rep):
    rep.sort(reverse = True)
    for item in rep:
        word = word.replace(item, '')

    return word

def compare_source_to_header_func(source, header):
    source_arr = source.split('-')
    header_arr = header.split('-')

    if source_arr[0] != header_arr[0]:
        return False

    for i, v in enumerate(header_arr):
        v = v.replace("const ", '')

        if i >= len(source_arr) and "def" not in v:
            return False

        if "def" in v:
            if i + 1 < len(source_arr):
                continue
            else:
                break
        
        if v != source_arr[i] and "tmp" not in v:
            return False

    if i < len(source_arr) - 1:
        return False
        
    return True   

def parse_line(elem):
    global replace_list
    types = []
    line = elem.strip()
    func = line.split("GEN_")
    if "//" not in func[0]:
        if len(func) > 1:
            func = re.split('\(|\)|\{|\}|\[|\]|\.', func[1])
            func_string = ""

            if "CLASS" in func[0]:
                out_data = func[0].replace("CLASS_", "").split(' ')[0]
                return (out_data, out_data)
            elif "STRUCT" in func[0]:
                out_data = func[0].replace("STRUCT_", "").split(' ')[0]
                return (out_data, out_data)
            
            if len(func) > 1:
                each_par = func[1].split(',')
                func_string = func_string + func[0] + "-"

                for item in each_par:
                    if "D" in item:
                        item = item.split('=')[0].strip()
                          
                    ch = item.strip().split(' ')
                    if len(ch) > 1:
                        item = ch[len(ch) - 1];
                    
                    var_data = item.split('_')
                    var_type = var_data[0].strip()
                    var_sufix = ""
                    var_prefix = ""
                    flags = ""

                    if len(var_data) > 2:

                        if "P" in var_data[1]:
                            var_sufix = var_sufix + "*"
                        elif "ARR" in var_data[1]:
                            var_sufix = var_sufix + "*"
                        if "C" in var_data[1]:
                            var_prefix = var_prefix + "const "
                        if "D" in var_data[1]:
                            var_prefix = var_prefix + "def "

                        if var_sufix != "" or var_prefix != "":
                            flags = "_" + var_data[1]

                    key = var_type + flags + "_"
                    
                    if key != "_":
                        replace_list.append(key)
                        
                    types.append([var_prefix + var_type.lower() + var_sufix])
                    func_string = func_string + var_prefix + var_type.lower() + var_sufix + "-"
                
                return (func[0], func_string)
    return(None, None)

#MAIN:
def main():
    global output
    global replace_list
    global headers
    global functions_included
    global replaced_func
    global nesting_count

    functions_used = []
    is_include = False
    spacing = ""
    content = []
    file = None
    is_comment = False

    if output == "":
        try:
            file = open(path + "main.cpp", "r")

        except Exception as err:
            pass

        content = file.readlines()
    else:
        content = output.split('\n')
        for i, v in enumerate(content):
            content[i] = v + "\n"
        output = ""

    for index, elem in enumerate(content):

        #Parsing the header files
        if "GENERATED_INPUT_OUT" in elem:
            is_include = False

        if "GENERATED_OUTPUT" in elem:
            indent_t_count = elem.count('\t')
            indent_spaces_count = elem.count(' ') + 8 * indent_t_count
            c = 0

            while c < indent_spaces_count:
                spacing = spacing + " "
                c = c + 1
        
        if is_include:
            new_include = content[index].split('"')[1].split('"')[0]
            headers.append(new_include)
        
        if "GENERATED_INPUT_IN" in elem:
            is_include = True

        #Parsing the used functions
        if is_include == False:
            
            if "/*MULTI_COMM" in elem and "MULTI_COMM*/" in elem:
                elem = elem.split('/*MULTI_COMM')[0] + elem.split('MULTI_COMM*/')[1]
                is_comment = False
            elif "/*MULTI_COMM" in elem:
                is_comment = True
                elem = elem.split('/*MULTI_COMM')[0].strip()

            if is_comment == False:
                output = output + elem    

            if "MULTI_COMM*/" in elem:
                is_comment = False

            if len(elem) != 0 and is_comment == False:
                key, val = parse_line(elem)
                if key != None:
                    functions_used.append(val)

    output = remove_multiple_substrings(output, replace_list)
    functions_added = ""
    structs_added = ""
    function_header = ""
    functions_used = list(dict.fromkeys(functions_used)) #possible vulnerability
    #print(functions_used)
    if len(functions_used) > 0:
        nesting_count = nesting_count + 1

    is_func = False
    is_func_sig = False
    is_func_header = False

    for elem in headers:
        try:
            header = open(path + elem, "r")

        except Exception as err:
            pass

        content = header.readlines()
        func_sig = ""
        whole_func = ""
        should_copy = False
        is_obj = False
        is_comment = False
        for line in content:
            if "/*MULTI_COMM" in line:
                is_comment = True

            if "MULTI_COMM*/" in line:
                is_comment = False

            if is_comment == True:
                continue
            
            if "START_OBJ_DEF" in line:
                is_func_header = False

            if is_func_header == True:
                function_header = function_header + remove_multiple_substrings(line, replace_list)
                #print(line)
            
            if "START_OBJ_HEADER" in line:
                is_func_header = True
                
            if "END_OBJ_SIG" in line:
                is_func_sig = False
            
            if "END_OBJ_DEF" in line:
                if should_copy == True:
                    if is_obj == False:
                        functions_added = function_header + functions_added + whole_func
                    else:
                        structs_added = function_header + structs_added + whole_func

                    should_copy = False
                whole_func = "\n"
                is_func = False
                function_header = ""

            formated_line = line

            if is_func_sig:
                if "CLASS" in line:
                    formated_line = line.replace("GEN_CLASS_", "")
                    is_obj = True
                elif "STRUCT" in line:
                    formated_line = line.replace("GEN_STRUCT_", "")
                    is_obj = True
                else:
                    formated_line = line.replace("GEN_", "")
                    is_obj = False
                
            if is_func:
                whole_func = whole_func + spacing + formated_line

            if is_func_sig:
                func_data = line.strip()
                
                key, val = parse_line(line)
                
                if key != None:
                    for item in functions_used:
                        
                        item = re.split(r"[^a-zA-Z0-9\s]", item)
                        item = item[0].split(' ')[0].strip()

                        if compare_source_to_header_func(item, val) or (is_obj and val == item):
                            if val not in replaced_func:
                                replaced_func[val] = 1
                                should_copy = True
            
            if "START_OBJ_DEF" in line:
                is_func = True
                is_func_sig = True

        
        header.close()

    if file:
        file.close()

    if functions_added != "" or structs_added != "":        
        output = output.replace("//GENERATED_OUTPUT\n\n", "//GENERATED_OUTPUT\n\n" + structs_added + functions_added)

main()
while nesting_count > 0:
    main()
    nesting_count = nesting_count - 1
    
pyperclip.copy(output)
