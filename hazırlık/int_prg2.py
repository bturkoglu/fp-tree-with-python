#!/usr/bin/python
# -*- coding: utf-8 -*-
#author: Tianming Lu

import operator
#import data
import sys
from itertools import combinations

sys.maxint = 100000

class Pattern:
    def __init__(self, itemset, support):
        self.itemset = itemset
        self.support = support

    def merge(self, p):
        self.itemset += p.itemset
        self.support = min(self.support, p.support)


class FPnode:
    def __init__(self, item, count):
        self.item = item
        self.count = count
        self.children = []
        self.parent = None
        self.mark = 0   # dummpy property, used when building conditional tree
        self.condition_count = 0

    def append(self, child_node):
        self.children.append(child_node)
        if child_node.parent is not None:
            child_node.parent.remove(child_node)
        child_node.parent = self

    def remove(self, node):
        self.children.remove(node)
        node.parent = None

    def is_single_prefix(self):
        if len(self.children) == 1:
            return True
        else:
            return False

    def seperate(self):
        """
        seperate into single prefix and branch
        """
        #find branch node
        node = self
        while len(node.children) == 1:
            node = node.children[0]
        parent = node.parent
        parent.remove(node)
        new_node = FPnode(node.item, node.count)
        parent.append(new_node)
        node.item = None
        node.count = 0
        return self, node

    def items(self):
        counts = {}
        self._items(counts)
        return counts.keys()

    def _items(self, counts):
        if self.item is not None:
            if self.item in counts:
                counts[self.item] += 1
            else:
                counts[self.item] = 1
        for c in self.children:
            c._items(counts)


def _frequent_items(transaction, threshold):
    """
    scan transaction once, to get the frequent items
    """
    counts = {}
    for t in transactions:
        for item in t:
            if item in counts:
                counts[item] += 1
            else:
                counts[item] = 1
    frequent_items = {k: v for k, v in counts.items() if v >= threshold}
    sorted_items = sorted(frequent_items.items(),
                           key=operator.itemgetter(1), reverse=True)
    return [i[0] for i in sorted_items]


def _build_tree(transactions, frequent_items):
    """
    build the FP tree
    """
    root = FPnode(None, 0)
    header_table = {i: [] for i in frequent_items}

    node = root
    for t in transactions:
        #filter and sort items in t in the order of frequent_items
        filtered_t = [i for i in t if i in frequent_items]
        sorted_t = sorted(filtered_t, key=lambda x: frequent_items.index(x))

        for item in sorted_t:
            subnode = _find_subnode(node, item)
            if subnode is None:
                subnode = FPnode(item, 1)
                node.append(subnode)

                #new node, add to header_table
                header_table[item].append(subnode)
            else:
                subnode.count += 1
            node = subnode
        node = root

    return root, header_table


def _build_conditional_tree(node, nodes_link, condition):
    """
    build conditional FP tree base on the condition
    """
    if node is None or (node.item is None and len(node.children) == 0):
        return None, None

    #mark nodes that should be included in the conditional tree
    for n in nodes_link:
        p = n.parent
        while p is not None:
            p.mark = 1
            p.condition_count += n.count
            p = p.parent

    #generate conditional tree
    items = node.items()

    header_table = {i: [] for i in items}
    root = FPnode(node.item, node.count)

    for subnode in node.children:
        subn = _build_conditional_subtree(subnode, header_table)
        if subn is not None:
            root.append(subn)
    if len(root.children) == 0:
        return None, header_table
    return root, header_table


def _build_conditional_subtree(node, header_table):
    """
    sub routine recursive used when building conditional FP tree
    """
    if node.mark == 0:
        return None

    n = FPnode(node.item, node.condition_count)
    node.mark = 0
    node.condition_count = 0

    #new node, add to header_table
    header_table[n.item].append(n)
    for sub in node.children:
        subn = _build_conditional_subtree(sub, header_table)
        if subn is not None:
            n.append(subn)
    return n


def _find_subnode(node, item):
    for subnode in node.children:
        if subnode.item == item:
            return subnode
    return None


def FP_growth(node, header_table, prefix, threshold):
    patterns_P = []
    patterns_Q = []
    patterns_all = []

    if node.is_single_prefix():
        P, Q = node.seperate()
        patterns_P = single_freq_pattern_set(P, threshold)
        for p in patterns_P:
            p.merge(prefix)

    else:
        Q = node

    for i in Q.items():
        support = 0
        node_link = header_table[i]
        for n in node_link:
            support += n.count
        p = Pattern([i], support)
        p.merge(prefix)
        if p.support < threshold:
            continue

        patterns_Q.append(p)
        tree_p, header_p = _build_conditional_tree(node, node_link, p)
        if tree_p is not None:
            patterns = FP_growth(tree_p, header_p, p, threshold)
            patterns_Q.extend(patterns)

    patterns_all.extend(patterns_P)
    patterns_all.extend(patterns_Q)

    for p in patterns_P:
        for q in patterns_Q:
            itemset = []
            itemset.extend(p.itemset)
            itemset.extend(q.itemset)
            patterns_all.append(Pattern(itemset, min(p.support, q.support)))
    return patterns_all


def single_freq_pattern_set(node, threshold):
    """
    freq_pattern_set for single prefix path
    """
    items = []
    n = node
    while True:
        if n.item is None:
            n = n.children[0]
            continue
        items.append(n)

        if len(n.children) == 0:
            break
        else:
            n = n.children[0]

    patterns = []
    for i in range(len(items)):
        coms = combinations(items, i + 1)
        for c in coms:
            min_support = sys.maxint
            pattern = []
            for i in c:
                pattern.append(i.item)
                if i.count < min_support:
                    min_support = i.count
            if min_support >= threshold:
                patterns.append(Pattern(pattern, min_support))
    return patterns


def print_tree(node, depth):
    s = ""
    for i in range(depth):
        s += "    "
    print((s + "{0}:{1}").format(node.item, node.count))
    for child in node.children:
        print_tree(child, depth + 1)


def print_patterns(patterns):
    sorted_p = sorted(patterns, key=lambda p: (len(p.itemset), p.support))
    for p in sorted_p:
        print("pattern: {0}, support:{1}".format(p.itemset, p.support))

def dosyayiOku(dosya):
    tr = []
    with open(dosya) as f:
        for line in f:
            tr.append(line.strip().split(','))
    return tr

def nodeBas(node):
    if node.parent:
        msjp = node.parent.item
    else:
        msjp = 'Root'
    msj = 'item: %s, count:%s Parent:%s, Mark:%s,Condition:%s, child adedi:%s' % (
        node.item, node.count, msjp,node.mark,
        node.condition_count, len(node.children))

    print(msj)
    print('Childrens:')
    for n in node.children:
        nodeBas(n)
    
    print()

    
if __name__ == "__main__":
    transactions = dosyayiOku("faturalar.txt")
    frequent_items = _frequent_items(transactions, 3)
    
    fp_tree, header_table = _build_tree(transactions, frequent_items)

    print('frequent_items:')
    print(frequent_items)
    print()
    print('fp_tree:')
    nodeBas(fp_tree)
    print()
    print('header_table:')
    for k,v in header_table.items():
        print(k,':',v)

    p = Pattern([], sys.maxint)    
    patterns = FP_growth(fp_tree, header_table, p, 3)
    print_patterns(patterns)
