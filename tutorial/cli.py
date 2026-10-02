"""命令行入口：跑新手引导样例。"""

import argparse

from .core import Tutorial


def build_parser():
    parser = argparse.ArgumentParser(prog="tutorial-steps", description="新手引导")
    parser.add_argument("--sample", default="require",
                        help="require / skip / dup / order / scan")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.sample == "require":
        steps = [{"id": "a", "requires": [], "skip_flag": False},
                 {"id": "b", "requires": ["a"], "skip_flag": False}]
        tut = Tutorial(steps)
        print("ok=%s" % str(tut.activate("b", "r1")).lower())
    elif args.sample == "skip":
        steps = [{"id": "a", "requires": [], "skip_flag": True},
                 {"id": "b", "requires": ["a"], "skip_flag": False}]
        tut = Tutorial(steps)
        tut.activate("a", "r1")
        print("skipped=%d" % len(tut.skipped_list()))
    elif args.sample == "dup":
        steps = [{"id": "a", "requires": [], "skip_flag": False}]
        tut = Tutorial(steps)
        tut.activate("a", "same")
        second = tut.activate("a", "same")
        print("second=%s" % str(second).lower())
    elif args.sample == "order":
        steps = [{"id": "a", "requires": [], "skip_flag": False},
                 {"id": "b", "requires": [], "skip_flag": False}]
        tut = Tutorial(steps)
        tut.activate("b", "r1")
        tut.activate("a", "r2")
        print("progress=%s" % ",".join(tut.progress()))
    elif args.sample == "scan":
        steps = [{"id": "s-%d" % index, "requires": [], "skip_flag": False}
                 for index in range(3000)]
        tut = Tutorial(steps)
        for index in range(3000):
            tut.activate("s-%d" % index, "r-%d" % index)
        print("scanned=%d" % tut.scanned_count())
    else:
        raise SystemExit("需要 --sample require|skip|dup|order|scan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
