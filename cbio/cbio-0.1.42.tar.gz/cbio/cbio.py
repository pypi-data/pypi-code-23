import argparse
import os
import tailer as tl
import io
import cbio


def vcf_analysis(args):
    filepath = os.path.abspath(args.vcf)

    vcf = VCF(filepath, args)

    vcf.head()
    vcf.tail()



def vcf_sub_commands(add_arg):
    # Create child commands
    # use required option to make the option mandatory
    # Use metavar to print description for what kind of input is expected
    add_arg.add_argument("-i", "--bed", help='Location to tf state file',
                       required=True)
    add_arg.add_argument("-f", "--head", help='First Variants in VCF')
    add_arg.add_argument("-t", "--tail", help='Lasts Variants in VCF')
    add_arg.add_argument("-p", "--pretty", action='store_true', help='Pretty print VCF')

    return add_arg

def bed_sub_commands(add_arg):
    # Create child commands
    # use required option to make the option mandatory
    # Use metavar to print description for what kind of input is expected
    add_arg.add_argument("-i", "--vcf", help='Location to tf state file',
                       required=True)
    add_arg.add_argument("-f", "--head", help='First Variants in VCF')
    add_arg.add_argument("-t", "--tail", help='Lasts Variants in VCF')
    add_arg.add_argument("-p", "--pretty", action='store_true', help='Pretty print VCF')

    return add_arg


def parse_options():
    parser = argparse.ArgumentParser(description='Any description to be displayed for the program.')
    # Create a subcommand
    subparsers = parser.add_subparsers(help='Add sub commands', dest='command')
    # Define a primary command apply & set child/sub commands for apply
    add_p = subparsers.add_parser('vcf', help='Tools to apply to VCF files')
    vcf_sub_commands(add_p)
    add_bed = subparsers.add_parser('bed', help='Tools to apply to BED files')
    bed_sub_commands(add_bed)

    # add_p = subparsers.add_parser('destroy', help='Destroy the infra from system')
    # sub_commands(add_p)
    # add_p = subparsers.add_parser('plan', help='Verify your changes before apply')
    # sub_commands(add_p)
    args = parser.parse_args()
    return args


def main():

    # parse some argument lists
    # args = parser.parse_args()

    import cbio

    print(dir(cbio))
    print(dir(cbio.biofiles))

    args = parse_options()

    if args.command == 'vcf':
        vcf_analysis(args)
    elif args.command == 'bed':
        bed_analysis(args)

if __name__ == "__main__":

    main()
