from treelib import Node, Tree
import os, sys, getopt, re, random
import html, requests
from fuzzer.basedata import *
from config import BASE_DIR, logger, CONFIG_RULES

rule_list = {}
debug = 0

BUILT_IN_RULES = {
    'ALPHA': Alpha(),
    'BIT': Bit(),
    'CHAR': Char(),
    'CR': Cr(),
    'CRLF': Crlf(),
    'CTL': Ctl(),
    'DIGIT': Digit(),
    'DQUOTE': Dquote(),
    'HEXDIG': Hexdig(),
    'HTAB': Htab(),
    'LF': Lf(),
    'SP': Sp(),
    'WSP': Wsp(),
    'LWSP': Lwsp(),
    'OCTET': Octet(),
    'VCHAR': Vchar()
}


# util
def find_pair(left_idx, right_char, string):
    left_char = string[left_idx]
    curr_idx = left_idx + 1

    if right_char == " ":
        while curr_idx < len(string):
            curr_char = string[curr_idx]
            if curr_char == right_char:
                break

            curr_idx = curr_idx + 1
    elif left_char == "*":  # seem un-used?
        while curr_idx < len(string):
            curr_char = string[curr_idx]
            if curr_char == right_char:
                break

            curr_idx = curr_idx + 1
    elif left_char == "\"":  # 不允许存在双引号嵌套
        while curr_idx < len(string):
            curr_char = string[curr_idx]
            if curr_char == right_char:
                break

            curr_idx = curr_idx + 1
    else:
        left_count = 0
        while curr_idx < len(string):
            curr_char = string[curr_idx]
            if curr_char == right_char:  # 不允许存在类似< "<s" >
                if left_count == 0:
                    break
                else:
                    left_count = left_count - 1

            if curr_char == left_char:
                left_count = left_count + 1

            curr_idx = curr_idx + 1

    return curr_idx


# util
def get_repeat(tag):
    atleast = tag[1:].split(',')[0]
    if atleast == '':
        atleast = 0
    else:
        atleast = int(atleast)

    atmost = tag[1:].split(',')[1]
    if atmost == '':
        atmost = sys.maxsize
    else:
        atmost = int(atmost)

    return atleast, atmost


# make an expression-tree for a given rule
def parse_rule(rule, tree, curr_nid):
    rule = rule.strip()
    # logger.debug(rule)

    if len(rule) == 0:
        return

    idx = 0
    if rule[0] == '/':
        parent_node = tree.parent(curr_nid)
        if parent_node.tag != '/':
            new_node = tree.create_node(tag='/', parent=parent_node.identifier)
            subtree = tree.remove_subtree(curr_nid)
            tree.paste(new_node.identifier, subtree)

            curr_node = tree.create_node(tag='+', parent=new_node.identifier)
            curr_nid = curr_node.identifier
        else:
            curr_node = tree.create_node(tag='+', parent=parent_node.identifier)
            curr_nid = curr_node.identifier
    elif rule[0] == '[':
        node = tree.create_node(tag='[]', parent=curr_nid)
        node = tree.create_node(tag='+', parent=node.identifier)
        idx = find_pair(0, ']', rule)
        parse_rule(rule[1:idx], tree, node.identifier)
    elif rule[0] == '<':
        idx = find_pair(0, '>', rule)

        reg = re.compile('.*<(?P<name>[^,]*), .*RFC(?P<rfc_num>[0-9]*).*')
        match = reg.match(rule)
        if match == None:
            node = tree.create_node(tag='<>', parent=curr_nid)
            node = tree.create_node(tag='+', parent=node.identifier)

            parse_rule(rule[1:idx], tree, node.identifier)
        else:
            res = match.groupdict()
            node = tree.create_node(tag='=>', parent=curr_nid)
            node = tree.create_node(tag=res['name'] + ',' + res['rfc_num'], parent=node.identifier)
    elif rule[0] == '(':
        node = tree.create_node(tag='()', parent=curr_nid)
        node = tree.create_node(tag='+', parent=node.identifier)
        idx = find_pair(0, ')', rule)
        parse_rule(rule[1:idx], tree, node.identifier)
    elif rule[0] == '"':
        node = tree.create_node(tag='""', parent=curr_nid)
        idx = find_pair(0, '"', rule)
        node = tree.create_node(tag=rule[1:idx].encode(), parent=node.identifier)
    elif rule[0] == '%':
        node = tree.create_node(tag='%', parent=curr_nid)
        idx = find_pair(0, ' ', rule)
        node = tree.create_node(tag=rule[1:idx], parent=node.identifier)
    elif rule[0] == '*' or (len(rule) > 1 and rule[1] == '*'):
        reg = re.compile('^(?P<min>[0-9]*)[*](?P<max>[0-9]*)(?P<paren>[(]*)')
        match = reg.match(rule)
        res = match.groupdict()

        node = tree.create_node(tag="*" + res["min"] + "," + res["max"], parent=curr_nid)
        if res["paren"] != "":
            idx = find_pair(len(res["min"] + '*' + res["max"]), ")", rule)
            parse_rule(rule[len(res["min"] + '*' + res["max"]):idx + 1], tree, node.identifier)
        else:
            idx = find_pair(len(res["min"] + '*' + res["max"]), " ", rule)
            parse_rule(rule[len(res["min"] + '*' + res["max"]):idx], tree, node.identifier)
    elif rule[0].isdigit():
        reg = re.compile('^(?P<num>[0-9]*)(?P<paren>[(]*)')
        match = reg.match(rule)
        res = match.groupdict()

        node = tree.create_node(tag="*" + res["num"] + "," + res["num"], parent=curr_nid)
        if res["paren"] != "":
            idx = find_pair(len(res["num"]), ")", rule)
            parse_rule(rule[len(res["num"]):idx + 1], tree, node.identifier)
        else:
            idx = find_pair(len(res["num"]), " ", rule)
            parse_rule(rule[len(res["num"]):idx], tree, node.identifier)
    else:
        idx = find_pair(0, " ", rule)
        node = tree.create_node(tag=rule[:idx], parent=curr_nid)

    parse_rule(rule[idx + 1:], tree, curr_nid)


# get a random result for a given rule
def generate(rule_name, rfc_number):
    logger.debug("Generate from ABNF rule: {}".format(rule_name))
    res = b''
    if rule_name in CONFIG_RULES:
        count = len(CONFIG_RULES[rule_name])
        res = CONFIG_RULES[rule_name][random.randint(0, count - 1)].encode()
    elif rule_name in BUILT_IN_RULES:
        res = BUILT_IN_RULES[rule_name].generate()
    elif rule_name in rule_list[rfc_number]:
        rule = rule_list[rfc_number][rule_name]
        logger.debug("Deep into next Node: {}".format(rule))
        tree = Tree()
        tree.create_node(tag="+")
        node = tree.create_node(tag="+", parent=tree.root)
        parse_rule(rule, tree, node.identifier)
        logger.debug(tree.show())
        res = parse_tree(tree, tree.root, rfc_number)
    else:
        logger.error("Error: unknown rule name <" + rule_name + ">")
    return res


# walk the tree for a random result
def parse_tree(tree, nid, rfc_number):
    tag = tree.get_node(nid).tag
    children = tree.children(nid)
    # print(tag)

    res = b''
    if tag == '+':
        for i in range(0, len(children)):
            res = res + parse_tree(tree, children[i].identifier, rfc_number)
    elif tag == '/':
        idx = random.randint(0, len(children) - 1)
        # print('idx=' + str(idx))
        res = res + parse_tree(tree, children[idx].identifier, rfc_number)
    elif tag == '()':
        res = res + parse_tree(tree, children[0].identifier, rfc_number)
    elif tag == '<>':
        res = res + parse_tree(tree, children[0].identifier, rfc_number)
    elif tag == '[]':
        temp = random.randint(0, 1)
        if temp == 1 and len(children) > 0:
            res = res + parse_tree(tree, children[0].identifier, rfc_number)
    elif tag[0] == '*':
        atleast, atmost = get_repeat(tag)
        for i in range(0, atleast):
            res = res + parse_tree(tree, children[0].identifier, rfc_number)
        repeat = atleast
        while repeat < atmost:
            temp = random.randint(0, 1)
            # print(temp)
            if temp == 1:
                res = res + parse_tree(tree, children[0].identifier, rfc_number)
                # print(res)
                repeat = repeat + 1
            else:
                break
    elif tag == '""':
        if len(children) > 0:
            res = children[0].tag
    elif tag == '%':
        numeric = Numeric(children[0].tag)
        res = numeric.generate()
    elif tag == '=>':
        rule_name = children[0].tag.split(',')[0]
        rfc_number = children[0].tag.split(',')[1]
        res = generate(rule_name, rfc_number)
    else:
        rule_name = tag
        res = generate(rule_name, rfc_number)
    return res


# unused, for debug
def walk_tree(tree, nid):
    children = tree.children(nid)
    for i in range(0, len(children)):
        logger.debug(children[i].tag)
        walk_tree(tree, children[i].identifier)


# download and save the abnf list from a given rfc-link
def download_rfc(rfc_number):
    html_content = requests.get('https://tools.ietf.org/html/rfc' + rfc_number).content
    real_html = html_content.decode('utf8')
    pattern = re.compile(r'<.+?>', re.S)
    content = pattern.sub('', real_html)
    content = html.unescape(content)
    # logger.debug(content)

    if 'Collected ABNF' in content:
        content = 'Collected ABNF\n' + content.split('Collected ABNF')[2]
    content_list = content.split('\n')

    if 'Collected ABNF' in content:
        while ' = ' not in content_list[0]:
            content_list.pop(0)
        i = 0
        while i < len(content_list):
            if '[Page ' in content_list[i]:
                content_list.pop(i)
            elif content_list[i].startswith('RFC '):
                content_list.pop(i)
            elif len(content_list[i]) < 3:  # white space line
                content_list.pop(i)
            elif not content_list[i].startswith('   '):
                break
            else:
                i = i + 1
        while i < len(content_list):
            content_list.pop(i)
    else:
        i = 0
        while i < len(content_list):
            if '[Page ' in content_list[i]:
                content_list.pop(i)
            elif content_list[i].startswith('RFC '):
                content_list.pop(i)
            else:
                i = i + 1

        i = 0
        while True:
            while i < len(content_list):
                reg = re.compile('[ ]*[a-zA-Z0-9-]*[ ]* = .*')
                match = reg.match(content_list[i])
                if match == None:
                    content_list.pop(i)
                else:
                    break

            if i >= len(content_list):
                break

            while len(content_list[i]) > 3:  # not white space line
                i = i + 1
    content = '\n'.join(content_list)
    file_path = BASE_DIR + '/fuzzer/rfc/rfc' + rfc_number + '.txt'
    with open(file_path, 'w') as f:
        f.write(content)
    return


# read the abnf list from a given file
def get_rule_list(rfc_number):
    logger.debug('Get ABNF list from RFC' + rfc_number)
    file_path = BASE_DIR + '/fuzzer/rfc/rfc' + rfc_number + '.txt'
    if not os.path.exists(file_path):
        download_rfc(rfc_number)

    rule_list[rfc_number] = {}

    key = ''
    f = open(file_path, 'r')
    for line in f:
        line = line.strip()

        i = 0
        while i < len(line):
            if line[i] == ';':
                line = line[:i]
                break
            if line[i] == '"':
                i = find_pair(i, '"', line)
            i = i + 1

        if len(line) == 0:
            continue

        i = 0
        while i < len(line):
            if line[i] == '=':
                break
            if line[i] == '"':
                i = find_pair(i, '"', line)
            i = i + 1

        if i < len(line):
            if len(line[i + 1:].strip()) <= 1:
                continue
            key = line[:i].strip()
            rule_list[rfc_number][key] = line[i + 1:]
        else:
            rule_list[rfc_number][key] = rule_list[rfc_number][key] + " " + line
    f.close()

    expand_rule_list(rfc_number)


# expand the abnf list when it comes to another rfc
def expand_rule_list(rfc_number):
    rfc_list = []
    for key in rule_list[rfc_number]:
        rule = rule_list[rfc_number][key]
        if 'see [RFC' not in rule:
            continue
        reg = re.compile('.*<(?P<name>[^,]*), .*RFC(?P<rfc_num>[0-9]*).*')
        match = reg.match(rule)
        res = match.groupdict()
        if res['rfc_num'] not in rfc_list:
            rfc_list.append(res['rfc_num'])
    # logger.debug(rfc_list)
    for rfc_number in rfc_list:
        logger.debug('Expand ABNF list from RFC' + rfc_number)
        get_rule_list(rfc_number)
    return




#
# if __name__ == "__main__":
#     count = 1
#     rule_name = ''
#     rfc_number = '2234'
#
#     opts, args = getopt.getopt(sys.argv[1:], "dn:r:", ["rfc="])
#     for opt, arg in opts:
#         if opt == '-d':
#             debug = 1
#         if opt == '-n':
#             count = int(arg)
#         if opt == '-r':
#             rule_name = arg
#         if opt == '--rfc':
#             rfc_number = arg
#
#     print(randabnf(rule_name, rfc_number, count))
