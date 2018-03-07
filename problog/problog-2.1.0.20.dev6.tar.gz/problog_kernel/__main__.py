if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    from .kernel import ProbLogKernel
    IPKernelApp.launch_instance(kernel_class=ProbLogKernel)