#!/usr/bin/env python

import transform2


def get_dynamic_score():
    scorefile = open("score.cov")
    score = scorefile.readline()
    score = score.strip()
    return int(score)

# def get_dynamic_score(inx):
#  scorefile = open("score_" + str(inx) + ".cov")
#  score = scorefile.readline()
#  score = score.strip()
#  return int(score)


def log_fast_config(logfile, counter, score):
    f = open(logfile, "a")
    f.write(str(counter) + ": " + str(score))
    f.write("\n")


def log_config(config, msg, logfile, counter):
    f = open(logfile, "a")
    f.write(str(counter) + ". ")
    changeSet = config["config"]
    for change in changeSet:
        changeKey = change.keys()[0]
        t = change.values()[0]["type"]
        log = False
        if t == "float":
            t = "f"
            log = True
        elif t == "double":
            t = "d"
            log = True
        elif t == "longdouble":
            t = "ld"
            log = True
        if log:
            if changeKey == "localVar" or changeKey == "globalVar":
                name = change.values()[0]["name"]
                f.write(name + ":" + t + " ")
            elif changeKey == "op":
                name = change.values()[0]["id"]
                f.write(name + ":" + t + " ")
        if changeKey == "call":
            name = change.values()[0]["name"]
            swit = change.values()[0]["switch"]
            f.write(name + ":" + swit + " ")
    f.write(": " + msg)
    f.write("\n")


def print_config(config, configFile):
    f = open(configFile, 'w+')
    f.write("{\n")
    changeList = config["config"]
    for change in changeList:
        f.write("\t\"" + change.keys()[0] + "\": {\n")
        changeValue = change.values()[0]
        for valueInfo in changeValue.keys():
            if isinstance(changeValue[valueInfo], list):
                valueInfoList = changeValue[valueInfo]
                valueInfoListString = "["
                if len(valueInfoList) > 0:
                    valueInfoListString += "\"" + valueInfoList[0] + "\""
                for i in xrange(1, len(valueInfoList)):
                    valueInfoListString += ",\"" + valueInfoList[i] + "\""
                valueInfoListString += "]"
                f.write("\t\t\"" + valueInfo + "\": " + valueInfoListString + ",\n")
            else:
                f.write("\t\t\"" + valueInfo + "\": \"" + changeValue[valueInfo] + "\",\n")
        f.write("\t},\n")
    f.write("}\n")
    f.close()


def print_diff(changeConfig, originalConfig, diffFile):
    f = open(diffFile, 'w+')
    originalList = originalConfig["config"]
    changeList = changeConfig["config"]
    count = 0
    while count < len(originalList):
        change = changeList[count]
        origin = originalList[count]
        changeType = change.keys()[0]
        if changeType == "call":
            newSwitch = change.values()[0]["switch"]
            originalSwitch = origin.values()[0]["switch"]
            if newSwitch != originalSwitch:
                function = change.values()[0]["function"]
                f.write("call: " + change.values()
                        [0]["name"] + " at " + function + originalSwitch + " -> " + newSwitch + "\n")
        else:
            newType = change.values()[0]["type"]
            originType = origin.values()[0]["type"]
            if newType != originType:
                if changeType == "localVar":
                    function = change.values()[0]["function"]
                    if "file" in change.values()[0].keys():
                        fileName = change.values()[0]["file"]
                        f.write("localVar: " + change.values()[0]["name"] + "  at " + function +
                                " at " + fileName + " " + originType + " -> " + newType + "\n")
                    else:
                        f.write("localVar: " + change.values()[0]["name"] + "  at " + function +
                                " " + originType + " -> " + newType + "\n")
                elif changeType == "op":
                    function = change.values()[0]["function"]
                    f.write("op: " + change.values()[0]["id"] + " at " + function +
                            " " + originType + " -> " + newType + "\n")
                elif changeType == "globalVar":
                    f.write("globalVar: " + change.values()[0]["name"] +
                            " " + originType + " -> " + newType + "\n")
        count += 1
    f.close()


def is_number(s):
    """
    Check if a string is a number
    """
    try:
        float(s)
        return True
    except ValueError:
        return False

#
# check if we have search through all
# types in type_set
#


def is_empty(type_set):
    for t in type_set:
        if len(t) > 1:
            return False
    return True


#
# modify change set so that each variable
# maps to its highest type
#
def to_highest_precision(change_set, type_set):
    for i in range(0, len(change_set)):
        c = change_set[i]
        t = type_set[i]
        if len(t) > 0:
            c["type"] = t[-1]

#
# modify change set so that each variable
# maps to its 2nd highest type
#


def to_2nd_highest_precision(change_set, type_set):
    for i in range(0, len(change_set)):
        c = change_set[i]
        t = type_set[i]
        if len(t) > 1:
            c["type"] = t[-2]


def run_config(search_config, original_config, bitcode, inx):
    """
    run bitcode file with the current search configuration
    return  1   bitcode file is valid
            0   bitcode file is invalid
            < 0 some internal transformation error happens
    """
    # write the search_conf to a temp file
    print_config(search_config, "config_temp.json")
    # transform bitcode file using temp config file
    result = transform2.transform(bitcode, "config_temp.json")

    code = "VALID"
    if result == 1:
        pass
    elif result == 0:
        code = "INVALID"
    else:
        code = "FAIL" + str(result)

    # write log file
    log_config(search_config, code, "log.dd", inx)
    # write result files
    config_filename = code + "_config_" + bitcode + "_" + str(inx) + ".json"
    print_config(search_config, config_filename)
    if result == 1:
        diff_filename = "dd2_diff_" + bitcode + "_" + str(inx) + ".txt"
        print_diff(search_config, original_config, diff_filename)

    return result
