import active_learning
import transfer_learning

def active_learning_function(raw_pt, fold, rounds , label, mapping):
    print("Hey, you have succesfully imported melange_active_learning")

    fn = active_learning.get_name_features(raw_pt)

    al = active_learning.active_learning(fold,rounds, fn, label, raw_pt, mapping)

    al.run_CV()



def transfer_learning_function( ptn, train_fd , test_fd , train_label, test_label):
    print "hey, you have succesfully imported malange_transfer_learning"

    test_fn = transfer_learning.get_name_features(ptn)

    tl = transfer_learning.transfer_learning(train_fd, test_fd, train_label, test_label, test_fn, True)
    tl.run()





