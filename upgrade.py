from build_config import Environments
from builder.env import EnvArgs
from builder.upgrader import Upgrader


# comments are automatically turned into argparse help
class Args(EnvArgs):
    eager: bool = False  # eager to upgrade All packages


if __name__ == "__main__":
    args = Args().parse_args()

    for python_env in args.get_python_envs(Environments):
        python_env.print()
        Upgrader(python_env).install_for(*Environments.requirements, eager=args.eager)
        print()
