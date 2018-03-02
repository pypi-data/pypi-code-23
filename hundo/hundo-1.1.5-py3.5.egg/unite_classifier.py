from Bio import Phylo
from itertools import zip_longest


class Tree(object):
    """"""
    def __init__(self, newick_tree):
        self.tree = Phylo.read(newick_tree,
                               "newick",
                               values_are_confidence=True,
                               rooted=True)

    def get_clade(self, tx, percent_id):
        if not tx:
            return None

        # Yarza, P. et al. Uniting the classification of cultured and uncultured bacteria and archaeal using 16S rRNA gene sequences. Nat. Rev. Microbiol. 12, 635–645 (2014).
        if percent_id < 0.83:
            cutoff = "k"
        elif percent_id >= 0.83 and percent_id < 0.86:
            cutoff = "p"
        elif percent_id >= 0.86 and percent_id < 0.89:
            cutoff = "c"
        elif percent_id >= 0.89 and percent_id < 0.92:
            cutoff = "o"
        elif percent_id >= 0.92 and percent_id < 0.96:
            cutoff = "f"
        elif percent_id >= 0.96 and percent_id < 0.99:
            cutoff = "g"
        else:
            cutoff = "s"

        c = [i for i in self.tree.find_clades(tx)][0]
        cpath = self.tree.get_path(c)
        cpath.insert(0, self.tree.root)
        for clade in cpath:
            if clade.name.startswith(cutoff):
                # cutoff due to alignment percentage
                return clade
        # target was less specific than cutoff
        return c

    @staticmethod
    def tax_str(tx):
        if isinstance(tx, str):
            tx = [tx]
        for i, t in zip_longest("kpcofgs", tx):
            if not t:
                tx.append("%s__?" % i)
            else:
                assert(t.startswith("%s__" % i))
        return tx

    def lca(self, tx, percent_id):
        if isinstance(tx, str):
            tx = [tx]
        c = [self.get_clade(i, percent_id) for i in tx]
        c = self.tree.common_ancestor(c)
        if c == self.tree.root:
            return self.tax_str([self.tree.root.name])
        else:
            l = self.tree.get_path(c)
            l.insert(0, self.tree.root)
            return self.tax_str([c.name for c in l])
