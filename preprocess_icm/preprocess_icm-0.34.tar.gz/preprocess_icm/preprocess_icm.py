import re

from preprocess_element import preprocess_element


class preprocess_icm:
    no_alpha = re.compile("^[^<>#A-Za-z0-9]*")
    no_dbl_space = re.compile("  +")
    fix_params = re.compile("<([^ ]+):([^>]+)>")
    inject_params_regex = re.compile("<([^ :]+)>")
    param_filters = re.compile("<[^ ]+\(.*\)>")
    nohash = re.compile(r"#\d+>")

    # Accepts file with tab delimited <regex> \t <sub>
    # And regex list of tuples (regex,sub)
    def __init__(self, regexes=None, file=None):
        self.regexes = []

        if regexes is not None:
            for regex in regexes:
                pattern, sub = regex
                self.regexes.append([re.compile(pattern.lower()), sub.lower()])

        if file is not None:
            for reg in file:
                reg = reg.rstrip("\r\n")
                if reg == "##":
                    break
                if reg.strip() == "":
                    continue
                print reg

                pattern, sub = reg.split("\t")

                # Finding filters
                if self.param_filters.search(pattern) is not None:
                    filters = []
                    all_params = re.finditer("<([^(>]*?)(\(([^)]*)\))?>", pattern)
                    for param in all_params:
                        if param.group(2) > "":
                            filter = param.group(3)
                        else:
                            filter = None
                        pattern = re.sub("<([^(>]*?)(\(([^)]*)\))?>", "@@+\\1@@-", pattern, 1)
                        filters.append(filter)

                    pattern = pattern.replace("@@+", "<")
                    pattern = pattern.replace("@@-", ">")
                else:
                    filters = None

                # Adjusting <> notations to support #num
                pattern = pattern.replace(">", "(#\d+)?>")

                print pattern

                self.regexes.append([re.compile(pattern.lower()), sub.lower(), filters])
                # regs.append([pattern,sub])

    def preprocess(self, icm, elements):
        icm = str(icm)
        sentences = []
        cur_param_num = max([0] + [p.get_num() for p in elements])
        for text in self.sentence_split(icm):
            text = text.lower()
            loops = 0
            text_nohash = self.nohash.sub("", text)
            while True:
                loops += 1
                prev = text_nohash
                text_nohash = self.nohash.sub("", text)
                for reg in self.regexes:
                    while True:
                        cur_reg_prev = text_nohash
                        pattern, sub, filters = reg
                        # print pattern.pattern
                        # print text
                        # print "!"+sub+"!"
                        additional_values = {}
                        elements2remove = []

                        match = pattern.search(text)

                        if match is None:
                            break
                        my_sub = str(sub)
                        element_match = re.search("<([^>]*)>", my_sub)
                        if element_match is not None:
                            source_element_matches = re.finditer("<[^>]*#(\d+)>", match.group(0))
                            for source_element_match in source_element_matches:
                                param_num = int(source_element_match.group(1))

                                cur_param = [e for e in elements if e.get_num() == param_num][0]
                                additional_values.update(cur_param.get_params())

                                # removing element
                                elements2remove.append(param_num)
                            element_title = element_match.group(1)

                        my_params = {}
                        sub_param_match = self.fix_params.search(my_sub)
                        if sub_param_match is not None:
                            my_params = {}
                            for cur_param in sub_param_match.group(2).split(","):
                                key, value = cur_param.split("=")
                                try:
                                    value = value.replace("\\1", match.group(1))
                                    value = value.replace("\\2", match.group(2))
                                    value = value.replace("\\3", match.group(3))
                                    value = value.replace("\\4", match.group(4))
                                    value = value.replace("\\5", match.group(5))
                                    value = value.replace("\\6", match.group(6))
                                    value = value.replace("\\7", match.group(7))
                                    value = value.replace("\\8", match.group(8))
                                    value = value.replace("\\9", match.group(9))
                                except:
                                    dummy = 1

                                my_params[key] = value
                            element_title = sub_param_match.group(1)

                        my_params.update(additional_values)

                        do_sub = True

                        if filters is not None:
                            for filter in filters:
                                if filter is None:
                                    continue
                                params = filter.split(",")
                                for param in params:
                                    key, value = param.split("=")
                                    if key in my_params and my_params[key] != value or key not in my_params:
                                        do_sub = False
                                        break

                        if len(my_params) > 0 and do_sub:
                            cur_param_num += 1
                            my_sub = "<" + element_title + "#" + str(cur_param_num) + ">"
                            elements.append(
                                preprocess_element(num=cur_param_num, title=element_title, params=my_params))

                        if do_sub:
                            elements = [e for e in elements if e.get_num() not in elements2remove]
                            try:
                                text = pattern.sub(my_sub, text, 1)
                            except:
                                print "Error during sub"
                                print my_sub, text, pattern.sub("sss", text, 1)
                                m = pattern.search(text)
                                print m.group(1)
                            text = self.no_alpha.sub("", text)
                            text = self.no_dbl_space.sub(" ", text)
                        else:
                            break

                        text_nohash = self.nohash.sub("", text)
                        if cur_reg_prev == text_nohash:
                            break
                text_nohash = self.nohash.sub("", text)
                if prev == text_nohash:
                    break

            if (text + " ")[0].isalpha():
                text = text.capitalize()
            sentences.append(text.strip())

        icm = " ".join(sentences).strip()

        return icm, elements

    def sentence_split(self, s):
        sentence_break = re.compile("^(.*?[\.!\?] ?)([A-Za-z].*)")

        sentences = []
        cur_sentence = str(s)

        while True:
            match = sentence_break.match(cur_sentence)
            if match is not None:
                sentences.append(match.group(1).strip())
                cur_sentence = match.group(2)
            else:
                sentences.append(cur_sentence.strip())
                break

        return sentences

    def inject_params(self, text, params):
        used = []
        while True:
            match = self.inject_params_regex.search(text)
            if match is not None:
                fit = [i for i, p in enumerate(params) if p["name"] == match.group(1) and i not in used]
                if len(fit) > 0:
                    print 1
                    found_param = fit[0]
                    used.append(found_param)
                    sub = "#" + match.group(1) + ":" + params[found_param]["value"] + "#"
                    text = self.inject_params_regex.sub(sub, text, 1)
                else:
                    sub = "#" + match.group(1) + ":xxdummy#"
                    text = self.inject_params_regex.sub(sub, text, 1)
            else:
                break

        text = text.replace(":xxdummy", "")
        return text
