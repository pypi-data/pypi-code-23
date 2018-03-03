from krt import Graph 

def test_graph_properties():
    g = Graph.from_tuples([("a","b")])
    assert g.edges == g.__edges__ 
    assert g.nodes == g.__nodes__ 



### path tests 
def test_add_path_size_1():
    g = Graph()
    g.add_path(["a"])
    assert len(g.__edges__) == 0
    assert len(g.__nodes__) == 1 

def test_add_path_size_2():
    g = Graph()
    g.add_path(["a","b"])
    assert len(g.__edges__) == 1
    assert len(g.__nodes__) == 2 

def test_add_path_size_3():
    g = Graph()
    g.add_path(["a","b","c"])
    assert len(g.__edges__) == 2 
    assert len(g.__nodes__) == 3 


def test_add_paths():
    g = Graph()

    g.add_path(["a","b","c"])
    g.add_path(["e","b","g"]) 
    assert g.nodes ==  set(["a","b","c","e","g"])
    assert g.edges == set([("a","b"),("b","c"),("e","b"),("b","g")])
