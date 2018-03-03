from krt import Graph,Traverser
import pytest 


###  node properties like in degree and out degree

###   walk properties like cycles, path length etc 

def test_cycles_expects_excpetion():
    g = Graph()
    g.add_path(["a","b","c","a"]) 

    t = Traverser()
    t.grouper_add("cycle", lambda n,e,contxt: (n,e) ) 
    with pytest.raises(Exception):
        t.dfs(g) 

def test_cycles_expects_excpetion():
    g = Graph()
    g.add_path(["a","b","c","a"]) 

    t = Traverser()
    t.grouper_add("cycle", lambda n,e,contxt: (n,e) ) 
    t.dfs(g,ignore_cycles=True) 


### Travser context assertions  #### 

def test_context_path_assertion():
    g = Graph() 
    g.add_path(["a","b","c"])
    g.add_path(["e","b","g"]) 
    select_e = lambda n,e,context:  (n,e) if  "e" in context[Traverser.PATH] else (None,None)
   
    t = Traverser()
    t.grouper_add("path_contains", select_e )
    t.dfs(g) 
    assert len(t.groups()["path_contains"]) == 1 
    assert "path_contains" in t.groups() 
    assert t.groups()["path_contains"][0].edges == set([("e","b"),("b","g"),("b","c")])

def test_dfs_all():
    g = Graph() 
    g.add_path(["a","b","c"])
 
    select_all = lambda n,e,context:  (n,e)
   
    t = Traverser()
    t.grouper_add("main", select_all )
    t.dfs(g) 
    assert len(t.groups()["main"]) > 0
     


