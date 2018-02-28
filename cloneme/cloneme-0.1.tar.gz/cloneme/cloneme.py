from .parser import create_parser
from .repository.Repository import Repository

def main():
    parser = create_parser()
    args = parser.parse_args()

    repo = Repository(args.repo)
    repo.clone()
if __name__ == "__main__":
    main()
