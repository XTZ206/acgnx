import argparse
import handlers, view
from subjects import Subject


def main():
    apihandler = handlers.APIHandler()
    dbhandler = handlers.DBHandler("acgnx.db")

    argparser = argparse.ArgumentParser(
        prog="acgnx", usage="%(prog)s [command]", description="ACGN indeX v0.0.1"
    )
    subparsers = argparser.add_subparsers(dest="command")

    list_parser = subparsers.add_parser(
        "list", help="list subjects based on subject name and aliases"
    )
    list_parser.add_argument("name", nargs="?", type=str, default="")
    view_parser = subparsers.add_parser("view", help="view subject with id")
    view_parser.add_argument("id", type=int, help="to-be-viewed subject id")
    update_parser = subparsers.add_parser(
        "update", help="update specified subject based on subject id"
    )
    update_parser.add_argument("id", type=int, help="to-be-updated subject id")
    fetch_parser = subparsers.add_parser(
        "fetch", help="fetch subject based on subject id"
    )
    fetch_parser.add_argument("id", type=int, help="to-be-fetched subject id")
    search_parser = subparsers.add_parser("search", help="search subjects from bgm.tv")
    search_parser.add_argument("keyword", type=str, help="search keyword")
    args = argparser.parse_args()

    match args.command:

        case "list":
            if args.name == "":
                viewer = view.Viewer(dbhandler.fetch_all_subjects())
            else:
                viewer = view.Viewer(dbhandler.search_subjects(args.name))
            viewer.list_subjects()
            return

        case "view":
            viewer = view.Viewer([Subject(id=args.id)], view.Updater(dbhandler))
            viewer.view_subject()
            return

        case "update":
            if args.id is None:
                viewer = view.Viewer(
                    dbhandler.fetch_all_subjects(), view.Updater(apihandler)
                )
                viewer.update_subjects()
                dbhandler.update_subjects(*viewer.subjects)
                viewer.list_subjects()
                print("All subjects updated")
                return
            else:
                viewer = view.Viewer(dbhandler.fetch_subject(args.id))
                viewer.list_subject()
                print("All required subjects updated")
                return

        case "fetch":
            updater = view.Updater(apihandler)
            viewer = view.Viewer([Subject(args.id)], updater)
            viewer.update_subjects()
            dbhandler.insert_subjects(*viewer.subjects)
            viewer.list_subjects()
            print("All required subject fetched")

        case "search":
            updater = view.Updater(apihandler)
            viewer = view.Viewer([], updater, view.Selector())
            viewer.search_subjects(args.keyword)
            viewer.list_subjects()
            print("Viewing searching results")
            return

        case "help":
            argparser.print_help()
            return

        case _:
            argparser.print_help()
            return


if __name__ == "__main__":
    main()
