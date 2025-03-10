import argparse
import configparser
import handlers, view
from subjects import Subject


def main():

    # Load Configurations
    config = configparser.ConfigParser()
    if not config.read("acgnx.ini"):
        with open("acgnx.ini", "w") as configfile:
            config["PATH"] = {"dbpath": "acgnx.db"}
            config.write(configfile)

    config.read("acgnx.ini")
    if "PATH" not in config:
        config["PATH"] = {"dbpath": "acgnx.db"}

    # Main Argument Parser
    argparser = argparse.ArgumentParser(
        prog="acgnx", usage="%(prog)s [command]", description="ACGN indeX v0.0.1"
    )
    subparsers = argparser.add_subparsers(dest="command")

    # List Command Parser
    list_parser = subparsers.add_parser(
        "list", help="list subjects based on specified conditions"
    )
    list_condition = list_parser.add_mutually_exclusive_group(required=True)
    list_condition.add_argument(
        "-n", "--name", type=str, help="list based subject name/aliases"
    )
    list_condition.add_argument(
        "-a", "--all", action="store_true", help="list all subjects"
    )

    # View Command Parser
    view_parser = subparsers.add_parser("view", help="view subject with id")
    view_parser.add_argument("id", type=int, help="to-be-viewed subject id")

    # Update Command Parser
    update_parser = subparsers.add_parser(
        "update", help="update specified subject based on subject id"
    )
    update_parser.add_argument(
        "id", type=int, help="to-be-updated subject id", default=0
    )

    # Fetch Command Parser
    fetch_parser = subparsers.add_parser(
        "fetch", help="fetch subject based on subject id"
    )
    fetch_parser.add_argument("id", type=int, help="to-be-fetched subject id")

    # Remove Command Parser
    remove_parser = subparsers.add_parser(
        "remove", help="remove specified subject based on subject id"
    )
    remove_parser.add_argument("id", type=int, help="to-be-removed subject id")

    # Search Command Parser
    search_parser = subparsers.add_parser("search", help="search subjects from bgm.tv")
    search_parser.add_argument("keyword", type=str, help="search keyword")

    args = argparser.parse_args()

    # Initialize handlers
    apihandler = handlers.APIHandler()
    dbhandler = handlers.DBHandler(config.get("PATH", "dbpath"))

    match args.command:

        case "list":
            if args.all:
                viewer = view.Viewer(dbhandler.fetch_all_subjects())
                viewer.list_subjects()
            elif args.name is not None:
                viewer = view.Viewer(dbhandler.search_subjects(args.name))
                viewer.list_subjects()
            return

        case "view":
            subject = dbhandler.fetch_subject(args.id)
            if subject is None:
                print(f"There is no such ID in the database.: {args.id}")
                return
            viewer = view.Viewer([subject], view.Updater(dbhandler))
            viewer.update_subjects()
            viewer.view_subject()
            return

        case "update":
            if args.id > 0:
                viewer = view.Viewer(
                    dbhandler.fetch_all_subjects(), view.Updater(apihandler)
                )
                viewer.update_subjects()
                dbhandler.update_subjects(*viewer.subjects)
                viewer.list_subjects()
                print("All subjects updated")
                return
            else:
                viewer = view.Viewer(
                    [dbhandler.fetch_subject(args.id)], view.Updater(apihandler)
                )
                viewer.update_subjects()
                dbhandler.update_subjects(*viewer.subjects)
                viewer.list_subjects()
                print("All required subjects updated")
                return

        case "fetch":
            updater = view.Updater(apihandler)
            viewer = view.Viewer([Subject(args.id)], updater)
            viewer.update_subjects()
            dbhandler.insert_subjects(*viewer.subjects)
            viewer.list_subjects()
            print("All required subject fetched")
            return

        case "remove":
            subject_id = args.id
            subject = dbhandler.fetch_subject(subject_id)
            if subject is None:
                print(f"There is no such ID in the database.: {subject_id}")
                return
            viewer = view.Viewer([Subject(args.id)], view.Updater(dbhandler))
            viewer.update_subjects()
            dbhandler.remove_subjects(*viewer.subjects)
            viewer.list_subjects()
            print("All required subject removed")
            return

        case "search":
            updater = view.Updater(apihandler)
            viewer = view.Viewer([], updater, view.Selector())
            viewer.search_subjects(args.keyword)
            viewer.list_subjects()
            print("Viewing searching results")
            return

        case _:
            argparser.print_help()
            return


if __name__ == "__main__":
    main()
