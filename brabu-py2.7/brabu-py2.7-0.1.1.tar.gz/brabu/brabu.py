from gui.bramsrc import *
from ramsin_controller.ramsin_controller import brabu_data_dir

def main():

    if not os.path.isfile("{}/ramsin_controller/variables.dat".format(brabu_data_dir)):
        print(
            "Path in environment variable BRABU_DATA_DIR does not exists or not set correctly. Please export BRABU_DATA_DIR='PATH_to_BRABU_data_dir'. Usually $BRABU/data")
        exit(-1)

    app = QApplication(sys.argv)  # A new instance of QApplication

    form = RamsinBrams()  # We set the form to be our ExampleApp (design)
    form.show()  # Show the form
    sys.exit(app.exec_())

if __name__ == '__main__':  # if we're running file directly and not importing it
    main()

