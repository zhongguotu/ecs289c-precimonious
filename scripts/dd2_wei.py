#!/usr/bin/env python

import sys
import os
import math
import json
import utilities


# global search counter
SEARCH_COUNTER = 0

# initialized in main
ORIGINAL_SCORE = -1

# bitcode file name, initialized in main
BITCODE = None

# json objects, initialized in main
ORIGINAL_CONF = None
SEARCH_CONF = None


def run_config():
    global SEARCH_CONF, ORIGINAL_CONF, BITCODE, SEARCH_COUNTER
    result = utilities.run_config(SEARCH_CONF, ORIGINAL_CONF, BITCODE, SEARCH_COUNTER)
    SEARCH_COUNTER += 1
    return result


def is_valid_config():
    """
    Test if current configuration is valid
    """
    global ORIGINAL_SCORE
    result = run_config()
    if result == 1:
        new_score = utilities.get_dynamic_score()
        if new_score <= ORIGINAL_SCORE:
            return True
    return False


def to_highest_precision(change_set, type_set, switch_set):
    """
    modify change set so that each variable maps to its highest type
    """
    for i in range(0, len(change_set)):
        change = change_set[i]
        type_list = type_set[i]
        if len(type_list) > 0:
            change["type"] = type_list[-1]
        if len(switch_set) > 0:
            switch_list = switch_set[i]
            if len(switch_list) > 0:
                change["switch"] = switch_list[-1]


def to_2nd_highest_precision(change_set, type_set, switch_set):
    """
    modify change set so that each variable maps to its 2nd highest type
    """
    for i in range(0, len(change_set)):
        change = change_set[i]
        type_list = type_set[i]
        if len(type_list) > 1:
            change["type"] = type_list[-2]
        if len(switch_set) > 0:
            switch_list = switch_set[i]
            if len(switch_list) > 1:
                change["switch"] = switch_list[-2]


def to_highest_precision_by_group(change_set, type_set, switch_set, group_set):
    """
    modify change set so that each variable maps to its highest type
    """
    for group in group_set:
        for idx in group:
            change = change_set[idx]
            type_list = type_set[idx]
            if len(type_list) > 0:
                change["type"] = type_list[-1]
            if len(switch_set) > 0:
                switch_list = switch_set[idx]
                if len(switch_list) > 0:
                    change["switch"] = switch_list[-1]


def to_2nd_highest_precision_by_group(change_set, type_set, switch_set, group_set):
    """
    modify change set so that each variable maps to its 2nd highest type
    """
    for group in group_set:
        for idx in group:
            change = change_set[idx]
            type_list = type_set[idx]
            if len(type_list) > 1:
                change["type"] = type_list[-2]
            if len(switch_set) > 0:
                switch_list = switch_set[idx]
                if len(switch_list) > 1:
                    change["switch"] = switch_list[-2]


def dd_search_config(change_set, type_set, switch_set, group_set, div):
    #
    # partition change_set into deltas and delta inverses
    #
    delta_change_set = []
    delta_type_set = []
    delta_switch_set = []
    delta_inv_change_set = []
    delta_inv_type_set = []
    delta_inv_switch_set = []
    div_size = int(math.ceil(float(len(group_set)) / float(div)))
    # import pdb; pdb.set_trace()
    for i in xrange(0, len(group_set), div_size):
        delta_change = []
        delta_type = []
        delta_switch = []
        delta_inv_change = []
        delta_inv_type = []
        delta_inv_switch = []
        for j in xrange(0, len(group_set)):
            group = group_set[j]
            if j >= i and j < i + div_size:
                for change_idx in group:
                    delta_change.append(change_set[change_idx])
                    delta_type.append(type_set[change_idx])
                    delta_switch.append(switch_set[change_idx])
            else:
                for change_idx in group:
                    delta_inv_change.append(change_set[change_idx])
                    delta_inv_type.append(type_set[change_idx])
                    delta_inv_switch.append(switch_set[change_idx])
        delta_change_set.append(delta_change)
        delta_type_set.append(delta_type)
        delta_switch_set.append(delta_switch)
        delta_inv_change_set.append(delta_inv_change)
        delta_inv_type_set.append(delta_inv_type)
        delta_inv_switch_set.append(delta_inv_switch)

    # iterate through all delta and inverse delta set
    # record delta set that passes with min score
    pass_inx = -1
    inv_is_better = False
    min_score = -1
    # import pdb; pdb.set_trace()
    for i in range(len(delta_change_set)):
        delta_change = delta_change_set[i]
        delta_type = delta_type_set[i]
        delta_switch = delta_switch_set[i]
        if len(delta_change) > 0:
            # always reset to lowest precision
            to_2nd_highest_precision_by_group(change_set, type_set, switch_set, group_set)
            # apply change for variables in delta
            to_highest_precision(delta_change, delta_type, delta_switch)
            # record i if config passes
            if is_valid_config():
                score = utilities.get_dynamic_score()
                if score < min_score or min_score == -1:
                    pass_inx = i
                    inv_is_better = False
                    min_score = score

        delta_inv_change = delta_inv_change_set[i]
        delta_inv_type = delta_inv_type_set[i]
        delta_inv_switch = delta_inv_switch_set[i]
        if len(delta_inv_change) > 0 and div > 2:
            # always reset to lowest precision
            to_2nd_highest_precision_by_group(change_set, type_set, switch_set, group_set)
            # apply change for variables in delta inverse
            to_highest_precision(delta_inv_change, delta_inv_type, delta_inv_switch)
            # record i if config passes
            if is_valid_config():
                score = utilities.get_dynamic_score()
                if score < min_score or min_score == -1:
                    pass_inx = i
                    inv_is_better = True
                    min_score = score
    # import pdb; pdb.set_trace()
    #
    # recursively search in pass delta or pass delta inverse
    # right now keep searching for the first pass delta or
    # pass delta inverse; later on we will integrate cost
    # model here
    #
    if pass_inx != -1:
        pass_group_set = group_set[pass_inx*div_size:(pass_inx+1)*div_size]
        if inv_is_better:
            pass_group_set = [grp for grp in group_set if grp not in pass_group_set]

        if len(pass_group_set) > 1:
            # always reset to lowest precision
            to_2nd_highest_precision_by_group(change_set, type_set, switch_set, group_set)
            dd_search_config(change_set, type_set, switch_set, pass_group_set, 2)
        else:
            to_2nd_highest_precision_by_group(change_set, type_set, switch_set, group_set)
            to_highest_precision_by_group(change_set, type_set, switch_set, pass_group_set)
        return

    # stop searching when cannot divide groups any more
    if div_size == 1:
        to_highest_precision_by_group(change_set, type_set, switch_set, group_set)
    else:
        dd_search_config(change_set, type_set, switch_set, group_set, 2 * div)


def search_config(change_set, type_set, switch_set, group_set):
    # keep searching while the type set is not searched throughout
    while not utilities.is_empty(type_set):
        # search from bottom up
        to_2nd_highest_precision(change_set, type_set, switch_set)
        if not is_valid_config():
            dd_search_config(change_set, type_set, switch_set, group_set, 2)
        # remove types and switches that cannot be changed  ??????????????????????????
        # change_set[i]["type"] = "longdouble"
        # type_set[i] = ["float", "double", "longdouble"]
        # this means change_set[i] cannot be changed, so clear type_set[i] and switch_set[i]
        for i in range(len(change_set)):
            if len(type_set[i]) > 0 and change_set[i]["type"] == type_set[i][-1]:
                del type_set[i][:]
                if len(switch_set[i]) > 0:
                    del switch_set[i][:]
        # remove highest precision from each type vector
        for i in range(len(type_set)):
            type_vector = type_set[i]
            switch_vector = switch_set[i]
            if len(type_vector) > 0:
                type_vector.pop()
            if len(switch_vector) > 0:
                switch_vector.pop()


def get_group_num(operand_name, fun_name, next_grp_num, group_nums):
    """
    Given an operand, find its idx in SEARCH_CONF and grp_num if not -1,
    return (idx, grp_num)
    """
    global SEARCH_CONF
    if utilities.is_number(operand_name):
        # operand is an expression, not a variable
        return (-1, -1)
    for idx, change in enumerate(SEARCH_CONF["config"]):
        # only consider grouping local variables
        if change.keys()[0] == "localVar":
            if change.values()[0]["function"] == fun_name and change.values()[0]["name"] == operand_name:
                grp_num = group_nums[idx]
                if grp_num < 0:
                    return (idx, next_grp_num)
                else:
                    return (idx, min(next_grp_num, grp_num))
    return (-1, -1)


def init_groups():
    """
    initialize global grouping info
    """
    global SEARCH_CONF
    group_set = []
    group_nums = [-1]*len(SEARCH_CONF["config"])
    next_grp_num = 0
    # parse search configuration file
    for idx, item in enumerate(SEARCH_CONF["config"]):
        if item.keys()[0] == "op":
            is_new_grp = False
            fun_name = item.values()[0]["function"]
            operands = item.values()[0]["operands"]
            if isinstance(operands, list):
                cur_grp_num = -1
                op_grp = []
                if len(operands) == 1:
                    idx1, op_grp_num1 = get_group_num(operands[0], fun_name, next_grp_num, group_nums)
                    if (idx1 >= 0):
                        cur_grp_num = op_grp_num1
                        op_grp = [idx, idx1]
                elif len(operands) == 2:
                    # first operand
                    idx1, op_grp_num1 = get_group_num(operands[0], fun_name, next_grp_num, group_nums)
                    # second operand
                    idx2, op_grp_num2 = get_group_num(operands[1], fun_name, next_grp_num, group_nums)
                    if (idx1 >= 0 and idx2 >= 0):
                        op_grp = [idx, idx1, idx2]
                        if op_grp_num1 == op_grp_num2:
                            cur_grp_num = op_grp_num1
                        else:
                            cur_grp_num = min(op_grp_num1, op_grp_num2)
                            if cur_grp_num != next_grp_num:
                                del_grp_num = max(op_grp_num1, op_grp_num2)
                                if del_grp_num != next_grp_num:
                                    # move del_grp_num to cur_grp_num
                                    group_set[cur_grp_num].extend(group_set[del_grp_num])
                                    for each_idx in group_set[del_grp_num]:
                                        group_nums[each_idx] = cur_grp_num
                                    group_set[del_grp_num] = []  # there may be empty group
                    elif (idx1 >= 0):
                        cur_grp_num = op_grp_num1
                        op_grp = [idx, idx1]
                    elif (idx2 >= 0):
                        cur_grp_num = op_grp_num2
                        op_grp = [idx, idx2]
                else:
                    pass
                if cur_grp_num >= 0 and len(op_grp) > 0:
                    if cur_grp_num == next_grp_num:
                        is_new_grp = True
                        group_set.append(op_grp)
                    else:
                        group_set[cur_grp_num].extend(op_grp)
                    for each_idx in op_grp:
                        group_nums[each_idx] = cur_grp_num
            if is_new_grp:
                next_grp_num += 1

    group_set = [frozenset(grp) for grp in group_set]
    for idx, grp_num in enumerate(group_nums):
        if grp_num == -1:
            # add individual var as a group, but omit op
            if SEARCH_CONF["config"][idx].keys()[0] == "op":
                pass
            else:
                group_set.append(frozenset([idx]))
                group_nums[idx] = len(group_set) - 1
    return group_set


def main():
    """
    main function receives
        - argv[1] : bitcode file location
        - argv[2] : search file location
        - argv[3] : original config file location
    """
    global BITCODE, SEARCH_CONF, ORIGINAL_CONF, ORIGINAL_SCORE
    BITCODE = sys.argv[1]
    SEARCH_CONF = json.loads(open(sys.argv[2], 'r').read())
    ORIGINAL_CONF = json.loads(open(sys.argv[3], 'r').read())

    # delete log file if exists
    try:
        os.remove("log.dd")
    except OSError:
        pass

    # use index to find corresponding type
    change_set = []
    type_set = []
    switch_set = []

    # parse search configuration file
    for idx, item in enumerate(SEARCH_CONF["config"]):
        type_list = item.values()[0]["type"]
        if isinstance(type_list, list):
            type_set.append(type_list)
            change_set.append(item.values()[0])
        # put function calls into switch_set
        if item.keys()[0] == "call":
            switch_set.append(item.values()[0]["switch"])
        else:
            switch_set.append([])

    # parse search grouping
    group_set = init_groups()
    print "groups: "
    print group_set
    print "\n"

    # get original score
    to_highest_precision(change_set, type_set, switch_set)
    run_config()
    ORIGINAL_SCORE = utilities.get_dynamic_score()

    # search for valid configuration using delta-debugging algorithm
    search_config(change_set, type_set, switch_set, group_set)

    # get the score of modified program
    if is_valid_config():
        print "Check valid_" + BITCODE + ".json for the valid configuration file"
        # print valid configuration file and diff file
        utilities.print_config(SEARCH_CONF, "dd2_valid_" + BITCODE + ".json")
        utilities.print_diff(SEARCH_CONF, ORIGINAL_CONF, "dd2_diff_" + BITCODE + ".txt")
    else:
        print "No configuration is found!"


if __name__ == "__main__":
    main()
